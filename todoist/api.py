import time
import json
import requests

from todoist import models
from todoist.managers.biz_invitations import BizInvitationsManager
from todoist.managers.filters import FiltersManager
from todoist.managers.invitations import InvitationsManager
from todoist.managers.live_notifications import LiveNotificationsManager
from todoist.managers.notes import NotesManager
from todoist.managers.projects import ProjectsManager
from todoist.managers.project_notes import ProjectNotesManager
from todoist.managers.items import ItemsManager
from todoist.managers.labels import LabelsManager
from todoist.managers.reminders import RemindersManager
from todoist.managers.user import UserManager


class TodoistAPI(object):
    """
    Implements the API that makes it possible to interact with a Todoist user
    account and its data.
    """
    _serialize_fields = ('token', 'api_url', 'seq_no', 'seq_no_partial',
                         'state', 'temp_ids', 'timestamp', 'timestamp_suffix')

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        for key in cls._serialize_fields:
            if key in data:
                setattr(obj, key, data[key])
        return obj

    def __init__(self, token='', api_endpoint='https://api.todoist.com'):
        self.api_url = '%s/API/v6/' % api_endpoint  # Todoist API
        self.seq_no = 0  # Sequence number since last update
        self.seq_no_partial = {}  # Sequence number of partial syncs
        self.state = {  # Local copy of all of the user's objects
            'CollaboratorStates': [],
            'Collaborators': [],
            'DayOrders': {},
            'DayOrdersTimestamp': '',
            'Filters': [],
            'Items': [],
            'Labels': [],
            'LiveNotifications': [],
            'LiveNotificationsLastRead': -1,
            'Notes': [],
            'ProjectNotes': [],
            'Projects': [],
            'Reminders': [],
            'Settings': {},
            'SettingsNotifications': {},
            'User': {},
            'UserId': -1,
            'WebStaticVersion': -1,
        }
        self.token = token  # User's API token
        self.temp_ids = {}  # Mapping of temporary ids to real ids
        self.queue = []  # Requests to be sent are appended here
        self.timestamp = -1
        self.timestamp_suffix = -1

        # managers
        self.projects = ProjectsManager(self)
        self.project_notes = ProjectNotesManager(self)
        self.items = ItemsManager(self)
        self.labels = LabelsManager(self)
        self.filters = FiltersManager(self)
        self.notes = NotesManager(self)
        self.live_notifications = LiveNotificationsManager(self)
        self.reminders = RemindersManager(self)
        self.invitations = InvitationsManager(self)
        self.biz_invitations = BizInvitationsManager(self)
        self.user = UserManager(self)

    def __getitem__(self, key):
        return self.state[key]

    def serialize(self):
        return {key: getattr(self, key) for key in self._serialize_fields}

    def _update_state(self, syncdata):
        """
        Updates the local state, with the data returned by the server after a
        sync.
        """
        # It is straightforward to update these type of data, since it is
        # enough to just see if they are present in the sync data, and then
        # either replace the local values or update them.
        if 'Collaborators' in syncdata:
            self.state['Collaborators'] = syncdata['Collaborators']
        if 'CollaboratorStates' in syncdata:
            self.state['CollaboratorStates'] = syncdata['CollaboratorStates']
        if 'DayOrders' in syncdata:
            self.state['DayOrders'].update(syncdata['DayOrders'])
        if 'DayOrdersTimestamp' in syncdata:
            self.state['DayOrdersTimestamp'] = syncdata['DayOrdersTimestamp']
        if 'LiveNotificationsLastRead' in syncdata:
            self.state['LiveNotificationsLastRead'] = \
                syncdata['LiveNotificationsLastRead']
        if 'Settings' in syncdata:
            self.state['Settings'].update(syncdata['Settings'])
        if 'SettingsNotifications' in syncdata:
            self.state['SettingsNotifications'].\
                update(syncdata['SettingsNotifications'])
        if 'User' in syncdata:
            self.state['User'].update(syncdata['User'])
        if 'UserId' in syncdata:
            self.state['UserId'] = syncdata['UserId']
        if 'WebStaticVersion' in syncdata:
            self.state['WebStaticVersion'] = syncdata['WebStaticVersion']

        # Updating these type of data is a bit more complicated, since it is
        # necessary to find out whether an object in the sync data is new,
        # updates an existing object, or marks an object to be deleted.  But
        # the same procedure takes place for each of these types of data.
        for datatype in 'Filters', 'Items', 'Labels', 'LiveNotifications', \
                        'Notes', 'ProjectNotes', 'Projects', 'Reminders':
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
                    if remoteobj.get('is_deleted', 0) == 0:
                        localobj.data.update(remoteobj)
                    else:
                        self.state[datatype].remove(localobj)
                else:
                    # If not, then the object is new and it should be added,
                    # unless it is marked as to be deleted (in which case it's
                    # ignored).
                    if remoteobj.get('is_deleted', 0) == 0:
                        model = 'models.' + datatype[:-1]
                        newobj = eval(model)(remoteobj, self)
                        self.state[datatype].append(newobj)

    def _find_object(self, objtype, obj):
        """
        Searches for an object in the local state, depending on the type of
        object, and then on its primary key is.  If the object is found it is
        returned, and if not, then None is returned.
        """
        if objtype == 'Collaborators':
            return self.collaborators_get_by_id(obj['id'])
        elif objtype == 'CollaboratorStates':
            return self.collaborator_state_get_by_ids(obj['project_id'],
                                                      obj['user_id'])
        elif objtype == 'Filters':
            return self.filters.get_by_id(obj['id'], only_local=True)
        elif objtype == 'Items':
            return self.items.get_by_id(obj['id'], only_local=True)
        elif objtype == 'Labels':
            return self.labels.get_by_id(obj['id'], only_local=True)
        elif objtype == 'LiveNotifications':
            return self.live_notifications.get_by_key(obj['notification_key'])
        elif objtype == 'Notes':
            return self.notes.get_by_id(obj['id'], only_local=True)
        elif objtype == 'ProjectNotes':
            return self.project_notes.get_by_id(obj['id'], only_local=True)
        elif objtype == 'Projects':
            return self.projects.get_by_id(obj['id'], only_local=True)
        elif objtype == 'Reminders':
            return self.reminders.get_by_id(obj['id'], only_local=True)
        else:
            return None

    def _get_seq_no(self, resource_types):
        """
        Calculates what is the seq_no that should be sent, based on the last
        seq_no and the resource_types that are requested.
        """
        seq_no = self.seq_no
        if resource_types:
            for resource in resource_types:
                if resource in self.seq_no_partial:
                    if seq_no == 0 or self.seq_no_partial[resource] < seq_no:
                        seq_no = self.seq_no_partial[resource]
        return seq_no

    def _update_seq_no(self, seq_no, resource_types):
        """
        Updates the seq_no and the seq_no_partial, based on the seq_no in
        the response and the resource_types that were requested.
        """
        if not seq_no:
            return
        if resource_types and seq_no > self.seq_no:
            for resource in resource_types:
                self.seq_no_partial[resource] = seq_no
        else:
            self.seq_no = seq_no
            self.seq_no_partial = {}

    def _replace_temp_id(self, temp_id, new_id):
        """
        Replaces the temporary id generated locally when an object was first
        created, with a real Id supplied by the server.  True is returned if
        the temporary id was found and replaced, and False otherwise.
        """
        # Go through all the objects for which we expect the temporary id to be
        # replaced by a real one.
        for datatype in ['Filters', 'Items', 'Labels', 'Notes', 'Projects',
                         'Reminders']:
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
            url = self.api_url
        response = requests.get(url + call, **kwargs)
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
            url = self.api_url
        response = requests.post(url + call, **kwargs)
        try:
            return response.json()
        except ValueError:
            return response.text

    # Sync
    def generate_timestamp(self):
        """
        Generates a timestamp, which is based on the current unix time.
        """
        now = int(time.time())
        if now != self.timestamp:
            self.timestamp = now
            self.timestamp_suffix = 1
        else:
            self.timestamp_suffix += 1
        return str(self.timestamp) + '.' + str(self.timestamp_suffix)

    def sync(self, commands=None, **kwargs):
        """
        Sends to the server the changes that were made locally, and also
        fetches the latest updated data from the server.
        """
        params = {
            'seq_no': self._get_seq_no(kwargs.get('resource_types', None)),
            'token': self.token,
            'commands': json.dumps(commands or []),
            'day_orders_timestamp': self.state['DayOrdersTimestamp'],
        }
        if 'include_notification_settings' in kwargs:
            params['include_notification_settings'] = 1
        if 'resource_types' in kwargs:
            params['resource_types'] = json.dumps(kwargs['resource_types'])
        data = self._post('sync', params=params)
        self._update_state(data)
        self._update_seq_no(data.get('seq_no', None),
                            kwargs.get('resource_types', None))

        return data

    def commit(self):
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
        if 'TempIdMapping' in ret:
            for temp_id, new_id in ret['TempIdMapping'].items():
                self.temp_ids[temp_id] = new_id
                self._replace_temp_id(temp_id, new_id)
        return ret['SyncStatus']

    # Authentication
    def login(self, email, password):
        """
        Logins user, and returns the response received by the server.
        """
        data = self._get('login', params={'email': email,
                                          'password': password})
        if 'token' in data:
            self.token = data['token']
        return data

    def login_with_google(self, email, oauth2_token, **kwargs):
        """
        Logins user with Google account, and returns the response received by
        the server.

        """
        params = {'email': email, 'oauth2_token': oauth2_token}
        params.update(kwargs)
        data = self._get('login_with_google', params=params)
        if 'token' in data:
            self.token = data['token']
        return data

    # User
    def register(self, email, full_name, password, **kwargs):
        """
        Registers a new user.
        """
        params = {'email': email, 'full_name': full_name, 'password': password}
        params.update(kwargs)
        data = self._get('register', params=params)
        if 'token' in data:
            self.token = data['token']
        return data

    def delete_user(self, current_password, **kwargs):
        """
        Deletes an existing user.
        """
        params = {'token': self.token,
                  'current_password': current_password}
        params.update(kwargs)
        return self._get('delete_user', params=params)

    # Miscellaneous
    def upload_file(self, filename, **kwargs):
        """
        Uploads a file.
        """
        params = {'token': self.token}
        params.update(kwargs)
        files = {'file': open(filename, 'rb')}
        return self._post('upload_file', self.api_url, params=params,
                          files=files)

    def query(self, queries, **kwargs):
        """
        Performs date queries and other searches, and returns the results.
        """
        params = {'queries': json.dumps(queries), 'token': self.token}
        params.update(kwargs)
        return self._get('query', params=params)

    def get_redirect_link(self, **kwargs):
        """
        Returns the absolute URL to redirect or to open in a browser.
        """
        params = {'token': self.token}
        params.update(kwargs)
        return self._get('get_redirect_link', params=params)

    def get_productivity_stats(self):
        """
        Returns the user's recent productivity stats.
        """
        return self._get('get_productivity_stats',
                         params={'token': self.token})

    def update_notification_setting(self, notification_type, service,
                                    dont_notify):
        """
        Updates the user's notification settings.
        """
        return self._get('update_notification_setting',
                         params={'token': self.token,
                                 'notification_type': notification_type,
                                 'service': service,
                                 'dont_notify': dont_notify})

    def get_all_completed_items(self, **kwargs):
        """
        Returns all user's completed items.
        """
        params = {'token': self.token}
        params.update(kwargs)
        return self._get('get_all_completed_items', params=params)

    def add_item(self, content, **kwargs):
        """
        Adds a new task.
        """
        params = {'token': self.token,
                  'content': content}
        params.update(kwargs)
        return self._get('add_item', params=params)

    # Sharing
    def share_project(self, project_id, email, message='', **kwargs):
        """
        Appends a request to the queue, to share a project with a user.
        """
        ts = self.generate_timestamp()
        item = {
            'type': 'share_project',
            'temp_id': '$' + ts,
            'timestamp': ts,
            'args': {
                'project_id': project_id,
                'email': email,
            },
        }
        item['args'].update(kwargs)
        self.queue.append(item)

    def delete_collaborator(self, project_id, email):
        """
        Appends a request to the queue, to delete a collaborator from a shared
        project.
        """
        item = {
            'type': 'delete_collaborator',
            'timestamp': self.generate_timestamp(),
            'args': {
                'project_id': project_id,
                'email': email,
            },
        }
        self.queue.append(item)

    def take_ownership(self, project_id):
        """
        Appends a request to the queue, take ownership of a shared project.
        """
        item = {
            'type': 'take_ownership',
            'timestamp': self.generate_timestamp(),
            'args': {
                'project_id': project_id,
            },
        }
        self.queue.append(item)

    def collaborators_get_by_id(self, user_id):
        """
        Finds and returns the collaborator based on the user id.
        """
        for obj in self.state['Collaborators']:
            if obj['id'] == user_id:
                return obj
        return None

    def collaborator_state_get_by_ids(self, project_id, user_id):
        """
        Finds and returns the collaborator state based on the project and user
        id.
        """
        for obj in self.state['CollaboratorStates']:
            if obj['project_id'] == project_id and obj['user_id'] == user_id:
                return obj
        return None

    # Auxiliary
    def get_project(self, project_id):
        """
        Gets an existing project.
        """
        params = {'token': self.token,
                  'project_id': project_id}
        return self._get('get_project', params=params)

    def get_item(self, item_id):
        """
        Gets an existing item.
        """
        params = {'token': self.token,
                  'item_id': item_id}
        return self._get('get_item', params=params)

    def get_label(self, label_id):
        """
        Gets an existing label.
        """
        params = {'token': self.token,
                  'label_id': label_id}
        return self._get('get_label', params=params)

    def get_note(self, note_id):
        """
        Gets an existing note.
        """
        params = {'token': self.token,
                  'note_id': note_id}
        return self._get('get_note', params=params)

    def get_filter(self, filter_id):
        """
        Gets an existing filter.
        """
        params = {'token': self.token,
                  'filter_id': filter_id}
        return self._get('get_filter', params=params)

    def get_reminder(self, reminder_id):
        """
        Gets an existing reminder.
        """
        params = {'token': self.token,
                  'reminder_id': reminder_id}
        return self._get('get_reminder', params=params)

    # Class
    def __repr__(self):
        name = self.__class__.__name__
        unsaved = '*' if len(self.queue) > 0 else ''
        if self.seq_no == 0:
            email = '<not synchronized>'
        else:
            email = repr(self.state['User']['email'])
        return '%s%s(%s)' % (name, unsaved, email)
