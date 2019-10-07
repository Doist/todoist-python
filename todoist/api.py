import datetime
import functools
import json
import os
import uuid

import requests

from todoist import models
from todoist.managers.activity import ActivityManager
from todoist.managers.backups import BackupsManager
from todoist.managers.biz_invitations import BizInvitationsManager
from todoist.managers.business_users import BusinessUsersManager
from todoist.managers.collaborator_states import CollaboratorStatesManager
from todoist.managers.collaborators import CollaboratorsManager
from todoist.managers.completed import CompletedManager
from todoist.managers.emails import EmailsManager
from todoist.managers.filters import FiltersManager
from todoist.managers.invitations import InvitationsManager
from todoist.managers.items import ItemsManager
from todoist.managers.labels import LabelsManager
from todoist.managers.live_notifications import LiveNotificationsManager
from todoist.managers.locations import LocationsManager
from todoist.managers.notes import NotesManager, ProjectNotesManager
from todoist.managers.projects import ProjectsManager
from todoist.managers.quick import QuickManager
from todoist.managers.reminders import RemindersManager
from todoist.managers.templates import TemplatesManager
from todoist.managers.uploads import UploadsManager
from todoist.managers.user import UserManager
from todoist.managers.user_settings import UserSettingsManager


class SyncError(Exception):
    pass


class TodoistAPI(object):
    """
    Implements the API that makes it possible to interact with a Todoist user
    account and its data.
    """
    _serialize_fields = ('token', 'api_endpoint', 'sync_token', 'state',
                         'temp_ids')

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        for key in cls._serialize_fields:
            if key in data:
                setattr(obj, key, data[key])
        return obj

    def __init__(self,
                 token='',
                 api_endpoint='https://api.todoist.com',
                 session=None,
                 cache='~/.todoist-sync/'):
        self.api_endpoint = api_endpoint
        self.reset_state()
        self.token = token  # User's API token
        self.temp_ids = {}  # Mapping of temporary ids to real ids
        self.queue = []  # Requests to be sent are appended here
        self.session = session or requests.Session(
        )  # Session instance for requests

        # managers
        self.projects = ProjectsManager(self)
        self.project_notes = ProjectNotesManager(self)
        self.items = ItemsManager(self)
        self.labels = LabelsManager(self)
        self.filters = FiltersManager(self)
        self.notes = NotesManager(self)
        self.live_notifications = LiveNotificationsManager(self)
        self.reminders = RemindersManager(self)
        self.locations = LocationsManager(self)
        self.invitations = InvitationsManager(self)
        self.biz_invitations = BizInvitationsManager(self)
        self.user = UserManager(self)
        self.user_settings = UserSettingsManager(self)
        self.collaborators = CollaboratorsManager(self)
        self.collaborator_states = CollaboratorStatesManager(self)

        self.completed = CompletedManager(self)
        self.uploads = UploadsManager(self)
        self.activity = ActivityManager(self)
        self.business_users = BusinessUsersManager(self)
        self.templates = TemplatesManager(self)
        self.backups = BackupsManager(self)
        self.quick = QuickManager(self)
        self.emails = EmailsManager(self)

        if cache:  # Read and write user state on local disk cache
            self.cache = os.path.expanduser(cache)
            self._read_cache()
        else:
            self.cache = None

    def reset_state(self):
        self.sync_token = '*'
        self.state = {  # Local copy of all of the user's objects
            'collaborator_states': [],
            'collaborators': [],
            'day_orders': {},
            'day_orders_timestamp': '',
            'filters': [],
            'items': [],
            'labels': [],
            'live_notifications': [],
            'live_notifications_last_read_id': -1,
            'locations': [],
            'notes': [],
            'project_notes': [],
            'projects': [],
            'reminders': [],
            'settings_notifications': {},
            'user': {},
            'user_settings': {},
        }

    def __getitem__(self, key):
        return self.state[key]

    def serialize(self):
        return {key: getattr(self, key) for key in self._serialize_fields}

    def get_api_url(self):
        return '%s/sync/v8/' % self.api_endpoint

    def _update_state(self, syncdata):
        """
        Updates the local state, with the data returned by the server after a
        sync.
        """
        # Check sync token first
        if 'sync_token' in syncdata:
            self.sync_token = syncdata['sync_token']

        # It is straightforward to update these type of data, since it is
        # enough to just see if they are present in the sync data, and then
        # either replace the local values or update them.
        if 'day_orders' in syncdata:
            self.state['day_orders'].update(syncdata['day_orders'])
        if 'day_orders_timestamp' in syncdata:
            self.state['day_orders_timestamp'] = syncdata[
                'day_orders_timestamp']
        if 'live_notifications_last_read_id' in syncdata:
            self.state['live_notifications_last_read_id'] = syncdata[
                'live_notifications_last_read_id']
        if 'locations' in syncdata:
            self.state['locations'] = syncdata['locations']
        if 'settings_notifications' in syncdata:
            self.state['settings_notifications'].update(
                syncdata['settings_notifications'])
        if 'user' in syncdata:
            self.state['user'].update(syncdata['user'])
        if 'user_settings' in syncdata:
            self.state['user_settings'].update(syncdata['user_settings'])

        # Updating these type of data is a bit more complicated, since it is
        # necessary to find out whether an object in the sync data is new,
        # updates an existing object, or marks an object to be deleted.  But
        # the same procedure takes place for each of these types of data.
        resp_models_mapping = [
            ('collaborators', models.Collaborator),
            ('collaborator_states', models.CollaboratorState),
            ('filters', models.Filter),
            ('items', models.Item),
            ('labels', models.Label),
            ('live_notifications', models.LiveNotification),
            ('notes', models.Note),
            ('project_notes', models.ProjectNote),
            ('projects', models.Project),
            ('reminders', models.Reminder),
        ]
        for datatype, model in resp_models_mapping:
            if datatype not in syncdata:
                continue

            # Process each object of this specific type in the sync data.
            for remoteobj in syncdata[datatype]:
                # Find out whether the object already exists in the local
                # state.
                localobj = self._find_object(datatype, remoteobj)
                if localobj is not None:
                    # If the object is already present in the local state, then
                    # we either update it, or if marked as to be deleted, we
                    # remove it.
                    is_deleted = remoteobj.get('is_deleted', 0)
                    if is_deleted == 0 or is_deleted is False:
                        localobj.data.update(remoteobj)
                    else:
                        self.state[datatype].remove(localobj)
                else:
                    # If not, then the object is new and it should be added,
                    # unless it is marked as to be deleted (in which case it's
                    # ignored).
                    is_deleted = remoteobj.get('is_deleted', 0)
                    if is_deleted == 0 or is_deleted is False:
                        newobj = model(remoteobj, self)
                        self.state[datatype].append(newobj)

    def _read_cache(self):
        if not self.cache:
            return

        try:
            os.makedirs(self.cache)
        except OSError:
            if not os.path.isdir(self.cache):
                raise

        try:
            with open(self.cache + self.token + '.json') as f:
                state = f.read()
            state = json.loads(state)
            self._update_state(state)

            with open(self.cache + self.token + '.sync') as f:
                sync_token = f.read()
            self.sync_token = sync_token
        except:
            return

    def _write_cache(self):
        if not self.cache:
            return
        result = json.dumps(
            self.state, indent=2, sort_keys=True, default=state_default)
        with open(self.cache + self.token + '.json', 'w') as f:
            f.write(result)
        with open(self.cache + self.token + '.sync', 'w') as f:
            f.write(self.sync_token)

    def _find_object(self, objtype, obj):
        """
        Searches for an object in the local state, depending on the type of
        object, and then on its primary key is.  If the object is found it is
        returned, and if not, then None is returned.
        """
        if objtype == 'collaborators':
            return self.collaborators.get_by_id(obj['id'])
        elif objtype == 'collaborator_states':
            return self.collaborator_states.get_by_ids(obj['project_id'],
                                                       obj['user_id'])
        elif objtype == 'filters':
            return self.filters.get_by_id(obj['id'], only_local=True)
        elif objtype == 'items':
            return self.items.get_by_id(obj['id'], only_local=True)
        elif objtype == 'labels':
            return self.labels.get_by_id(obj['id'], only_local=True)
        elif objtype == 'live_notifications':
            return self.live_notifications.get_by_id(obj['id'])
        elif objtype == 'notes':
            return self.notes.get_by_id(obj['id'], only_local=True)
        elif objtype == 'project_notes':
            return self.project_notes.get_by_id(obj['id'], only_local=True)
        elif objtype == 'projects':
            return self.projects.get_by_id(obj['id'], only_local=True)
        elif objtype == 'reminders':
            return self.reminders.get_by_id(obj['id'], only_local=True)
        else:
            return None

    def _replace_temp_id(self, temp_id, new_id):
        """
        Replaces the temporary id generated locally when an object was first
        created, with a real Id supplied by the server.  True is returned if
        the temporary id was found and replaced, and False otherwise.
        """
        # Go through all the objects for which we expect the temporary id to be
        # replaced by a real one.
        for datatype in [
                'filters', 'items', 'labels', 'notes', 'project_notes',
                'projects', 'reminders'
        ]:
            for obj in self.state[datatype]:
                if obj.temp_id == temp_id:
                    obj['id'] = new_id
                    return True
        return False

    def _get(self, call, url=None, **kwargs):
        """
        Sends an HTTP GET request to the specified URL, and returns the JSON
        object received (if any), or whatever answer it got otherwise.
        """
        if not url:
            url = self.get_api_url()

        response = self.session.get(url + call, **kwargs)

        try:
            return response.json()
        except ValueError:
            return response.text

    def _post(self, call, url=None, **kwargs):
        """
        Sends an HTTP POST request to the specified URL, and returns the JSON
        object received (if any), or whatever answer it got otherwise.
        """
        if not url:
            url = self.get_api_url()

        response = self.session.post(url + call, **kwargs)

        try:
            return response.json()
        except ValueError:
            return response.text

    # Sync
    def generate_uuid(self):
        """
        Generates a uuid.
        """
        return str(uuid.uuid1())

    def sync(self, commands=None):
        """
        Sends to the server the changes that were made locally, and also
        fetches the latest updated data from the server.
        """
        post_data = {
            'token': self.token,
            'sync_token': self.sync_token,
            'day_orders_timestamp': self.state['day_orders_timestamp'],
            'include_notification_settings': 1,
            'resource_types': json_dumps(['all']),
            'commands': json_dumps(commands or []),
        }
        response = self._post('sync', data=post_data)
        if 'temp_id_mapping' in response:
            for temp_id, new_id in response['temp_id_mapping'].items():
                self.temp_ids[temp_id] = new_id
                self._replace_temp_id(temp_id, new_id)
        self._update_state(response)
        self._write_cache()
        return response

    def commit(self, raise_on_error=True):
        """
        Commits all requests that are queued.  Note that, without calling this
        method none of the changes that are made to the objects are actually
        synchronized to the server, unless one of the aforementioned Sync API
        calls are called directly.
        """
        if len(self.queue) == 0:
            return
        ret = self.sync(commands=self.queue)
        del self.queue[:]
        if 'sync_status' in ret:
            if raise_on_error:
                for k, v in ret['sync_status'].items():
                    if v != 'ok':
                        raise SyncError(k, v)
        return ret

    # Miscellaneous

    def query(self, queries, **kwargs):
        """
        DEPRECATED: query endpoint is deprecated for a long time and this
        method will be removed in the next major version of todoist-python
        """
        params = {'queries': json_dumps(queries), 'token': self.token}
        params.update(kwargs)
        return self._get('query', params=params)

    def add_item(self, content, **kwargs):
        """
        Adds a new task.
        """
        params = {'token': self.token, 'content': content}
        params.update(kwargs)
        if 'labels' in params:
            params['labels'] = str(params['labels'])
        return self._get('add_item', params=params)

    # Class
    def __repr__(self):
        name = self.__class__.__name__
        unsaved = '*' if len(self.queue) > 0 else ''
        email = self.user.get('email')
        email_repr = repr(email) if email else '<not synchronized>'
        return '%s%s(%s)' % (name, unsaved, email_repr)


def state_default(obj):
    return obj.data


def json_default(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, datetime.time):
        return obj.strftime('%H:%M:%S')


json_dumps = functools.partial(
    json.dumps, separators=',:', default=json_default)
