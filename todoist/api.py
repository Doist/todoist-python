import time
import random
import json
import requests

from todoist import models


class TodoistAPI(object):
    """
    Implements the API that makes it possible to interact with a Todoist user
    account and its data.
    """
    def __init__(self, api_token=''):
        self.api_url = 'https://todoist.com/API/'  # Standard API
        self.sync_url = 'https://api.todoist.com/TodoistSync/v5.3/'  # Sync API
        self.seq_no = 0  # Sequence number since last update
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
            'Projects': [],
            'Reminders': [],
            'Settings': {},
            'SettingsNotifications': {},
            'User': {},
            'UserId': -1,
            'WebStaticVersion': -1,
        }
        self.api_token = api_token  # User's API token
        self.temp_ids = {}  # Mapping of temporary ids to real ids
        self.queue = []  # Requests to be sent are appended here

    def __getitem__(self, key):
        return self.state[key]

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
                        'Notes', 'Projects', 'Reminders':
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
            return self.filter_get_by_id(obj['id'])
        elif objtype == 'Items':
            return self.item_get_by_id(obj['id'])
        elif objtype == 'Labels':
            return self.label_get_by_id(obj['id'])
        elif objtype == 'LiveNotifications':
            return self.live_notifications_get_by_key(obj['notification_key'])
        elif objtype == 'Notes':
            return self.note_get_by_id(obj['id'])
        elif objtype == 'Projects':
            return self.project_get_by_id(obj['id'])
        elif objtype == 'Reminders':
            return self.reminder_get_by_id(obj['id'])
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
        for datatype in ['Filters', 'Items', 'Labels', 'Notes', 'Projects',
                         'Reminders']:
            key = 'id'
            if datatype == 'Notes':
                key = 'note_id'
            for obj in self.state[datatype]:
                if obj.temp_id == temp_id:
                    obj[key] = new_id
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
            json = response.json()
            return json
        except ValueError:
            return response.text

    def _post(self, call, url=None, **kwargs):
        """
        Sends an HTTP POST request to the specified URL, and returns the JSON
        object received (if any), or whatever answer it got otherwise.
        """
        if not url:
            url = self.sync_url
        response = requests.post(url + call, **kwargs)
        try:
            return response.json()
        except ValueError:
            return response.text

    def _generate_timestamp(self):
        """
        Generates a timestamp, which is based on the current unix time plus
        four random digits at the end.
        """
        return str(int(time.time()) * 1000 + random.randint(0, 999))

    # Standard API based calls
    def login(self, email, password):
        """
        Logins user, and returns the response received by the server.
        """
        data = self._get('login', params={'email': email,
                                          'password': password})
        if 'api_token' in data:
            self.api_token = data['api_token']
        return data

    def login_with_google(self, email, oauth2_token, **kwargs):
        """
        Logins user with Google account, and returns the response received by
        the server.

        """
        data = self._get('loginWithGoogle', params={'email': email,
                         'oauth2_token': oauth2_token}, **kwargs)
        if 'api_token' in data:
            self.api_token = data['api_token']
        return data

    def ping(self, token):
        """
        Tests user's login token, and returns the response received by the
        server.
        """
        return self._get('ping', params={'token': token})

    def get_timezones(self):
        """
        Returns the timezones supported by the server.
        """
        return self._get('getTimezones')

    def query(self, queries, **kwargs):
        """
        Performs date queries and other searches, and returns the results.
        """
        return self._get('query', params={'queries': json.dumps(queries),
                         'token': self.api_token}, **kwargs)

    def upload_file(self, filename, **kwargs):
        """
        Uploads a file.
        """
        files = {'file': open(filename, 'rb')}
        return self._post('uploadFile', self.api_url,
                          params={'token': self.api_token}, files=files,
                          **kwargs)

    # Sync API based calls
    def get(self, **kwargs):
        """
        Retrieves all or only updated data from the server.
        """
        params = {'seq_no': self.seq_no,
                  'api_token': self.api_token,
                  'day_orders_timestamp': self.state['DayOrdersTimestamp']}
        params.update(kwargs)
        data = self._post('get', params=params)
        self._update_state(data)
        if 'seq_no' in data:
            self.seq_no = data['seq_no']
        return data

    def sync(self, items_to_sync=[], **kwargs):
        """
        Sends to the server the changes that took place locally.
        """
        params = {'api_token': self.api_token,
                  'items_to_sync': json.dumps(items_to_sync)}
        params.update(kwargs)
        data = self._post('sync', params=params)
        self._update_state(data)
        return data

    def sync_and_get_updated(self, items_to_sync=[], **kwargs):
        """
        Sends to the server the changes that were made locally, and also
        fetches the latest updated data from the server.
        """
        params = {'seq_no': self.seq_no,
                  'api_token': self.api_token,
                  'items_to_sync': json.dumps(items_to_sync),
                  'day_orders_timestamp': self.state['DayOrdersTimestamp']}
        params.update(kwargs)
        data = self._post('syncAndGetUpdated', params=params)
        self._update_state(data)
        if 'seq_no' in data:
            self.seq_no = data['seq_no']
        return data

    default_action = sync_and_get_updated  # Preferred Sync API call to use

    def commit(self):
        """
        Commits all requests that are queued.  Note that, without calling this
        method none of the changes that are made to the objects are actually
        synchronized to the server, unless one of the aforementioned Sync API
        calls are called directly.
        """
        if len(self.queue) == 0:
            return
        ret = self.default_action(items_to_sync=self.queue)
        del self.queue[:]
        if 'TempIdMapping' in ret:
            for temp_id, new_id in ret['TempIdMapping'].items():
                self.temp_ids[temp_id] = new_id
                self._replace_temp_id(temp_id, new_id)

    # Projects
    def project_get_by_id(self, project_id):
        """
        Finds and returns project based on its id.
        """
        for obj in self.state['Projects']:
            if obj['id'] == project_id or obj.temp_id == str(project_id):
                return obj
        return None

    def project_get_by_name(self, name):
        """
        Finds and returns project based on its name.
        """
        for obj in self.state['Projects']:
            if obj['name'] == name:
                return obj
        return None

    def project_add(self, name, **kwargs):
        """
        Adds a project to the local state, and appends the equivalent request
        to the queue.
        """
        obj = models.Project({'name': name}, self)
        ts = self._generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Projects'].append(obj)
        item = {
            'type': 'project_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    def project_update_orders_indents(self, ids_to_orders_indents):
        """
        Updates in the local state the orders and indents of multiple projects,
        and appends the equivalent request to the queue.
        """
        for project_id in ids_to_orders_indents.keys():
            obj = self.project_get_by_id(project_id)
            if obj:
                obj['item_order'] = ids_to_orders_indents[project_id][0]
                obj['indent'] = ids_to_orders_indents[project_id][1]
        item = {
            'type': 'project_update_orders_indents',
            'timestamp': self._generate_timestamp(),
            'args': {
                'ids_to_orders_indents': ids_to_orders_indents,
            },
        }
        self.queue.append(item)

    # Items
    def item_get_by_id(self, item_id):
        """
        Finds and returns item based on its id.
        """
        for obj in self.state['Items']:
            if obj['id'] == item_id or obj.temp_id == str(item_id):
                return obj
        return None

    def item_get_by_content(self, content):
        """
        Finds and returns item based on its content.
        """
        for obj in self.state['Items']:
            if obj['content'] == content:
                return obj
        return None

    def item_add(self, content, project_id, **kwargs):
        """
        Adds an item to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Item({'content': content, 'project_id': project_id}, self)
        ts = self._generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Items'].append(obj)
        item = {
            'type': 'item_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    def item_uncomplete_update_meta(self, project_id, ids_to_metas):
        """
        Marks an item as completed in the local state, and appends the
        equivalent request to the queue.
        """
        for item_id in ids_to_metas.keys():
            obj = self.item_get_by_id(item_id)
            if obj:
                obj['in_history'] = ids_to_metas[item_id][0]
                obj['checked'] = ids_to_metas[item_id][1]
                obj['item_order'] = ids_to_metas[item_id][2]
        item = {
            'type': 'item_uncomplete_update_meta',
            'timestamp': self._generate_timestamp(),
            'args': {
                'project_id': project_id,
                'ids_to_metas': ids_to_metas,
            },
        }
        self.queue.append(item)

    def item_update_date_complete(self, item_id, new_date_utc, date_string,
                                  is_forward):
        """
        Updates in the local state the date of multiple recurring tasks, and
        appends the equivalent request to the queue.
        """
        obj = self.item_get_by_id(item_id)
        if obj:
            obj['new_date_utc'] = new_date_utc
            obj['date_string'] = date_string
            obj['is_forward'] = is_forward
        item = {
            'type': 'item_update_date_complete',
            'timestamp': self._generate_timestamp(),
            'args': {
                'id': item_id,
                'new_date_utc': new_date_utc,
                'date_string': date_string,
                'is_forward': is_forward,
            },
        }
        self.queue.append(item)

    def item_update_orders_indents(self, ids_to_orders_indents):
        """
        Updates in the local state the order and indents of multiple items, and
        appends the equivalent request to the queue.
        """
        for item_id in ids_to_orders_indents.keys():
            obj = self.item_get_by_id(item_id)
            if obj:
                obj['item_order'] = ids_to_orders_indents[item_id][0]
                obj['indent'] = ids_to_orders_indents[item_id][1]
        item = {
            'type': 'item_update_orders_indents',
            'timestamp': self._generate_timestamp(),
            'args': {
                'ids_to_orders_indents': ids_to_orders_indents,
            },
        }
        self.queue.append(item)

    def item_update_day_orders(self, ids_to_orders):
        """
        Updates in the local state the day orders of multiple items, and
        appends the equivalent request to the queue.
        """
        for item_id in ids_to_orders.keys():
            obj = self.item_get_by_id(item_id)
            if obj:
                obj['day_order'] = ids_to_orders[item_id]
        item = {
            'type': 'item_update_day_orders',
            'timestamp': self._generate_timestamp(),
            'args': {
                'ids_to_orders': ids_to_orders,
            },
        }
        self.queue.append(item)

    # Labels
    def label_get_by_id(self, label_id):
        """
        Finds and returns label based on its id.
        """
        for obj in self.state['Labels']:
            if obj['id'] == label_id or obj.temp_id == str(label_id):
                return obj
        return None

    def label_register(self, name, **kwargs):
        """
        Registers a label in the local state, and appends the equivalent
        request to the queue.
        """
        obj = models.Label({'name': name}, self)
        ts = self._generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Labels'].append(obj)
        item = {
            'type': 'label_register',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    # Notes
    def note_get_by_id(self, note_id):
        """
        Finds and returns note based on its id.
        """
        for obj in self.state['Notes']:
            if obj['id'] == note_id or obj.temp_id == str(note_id):
                return obj
        return None

    def note_add(self, item_id, content, **kwargs):
        """
        Adds a note to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Note({'item_id': item_id, 'content': content}, self)
        ts = self._generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Notes'].append(obj)
        item = {
            'type': 'note_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    # Filters
    def filter_get_by_id(self, filter_id):
        """
        Finds and returns filter based on its id.
        """
        for obj in self.state['Filters']:
            if obj['id'] == filter_id or obj.temp_id == str(filter_id):
                return obj
        return None

    def filter_add(self, name, query, **kwargs):
        """
        Adds a filter to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Filter({'name': name, 'query': query}, self)
        ts = self._generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Filters'].append(obj)
        item = {
            'type': 'filter_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    def filter_update_orders(self, id_order_mapping):
        """
        Updates in the local state the orders of multiple filters, and appends
        the equivalent request to the queue.
        """
        for filter_id in id_order_mapping.keys():
            obj = self.filter_get_by_id(filter_id)
            if obj:
                obj['item_order'] = id_order_mapping[filter_id]
        item = {
            'type': 'filter_update_orders',
            'timestamp': self._generate_timestamp(),
            'args': {
                'id_order_mapping': id_order_mapping,
            },
        }
        self.queue.append(item)

    # Reminders
    def reminder_get_by_id(self, reminder_id):
        """
        Finds and returns reminder based on its id.
        """
        for obj in self.state['Reminders']:
            if obj['id'] == reminder_id or obj.temp_id == str(reminder_id):
                return obj
        return None

    def reminder_add(self, item_id, **kwargs):
        """
        Adds a reminder to the local state, and appends the equivalent request
        to the queue.
        """
        obj = models.Reminder({'item_id': item_id}, self)
        ts = self._generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Reminders'].append(obj)
        item = {
            'type': 'reminder_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    # Live notifications
    def live_notifications_get_by_key(self, notification_key):
        """
        Finds and returns live notification based on its key.
        """
        for obj in self.state['LiveNotifications']:
            if obj['notification_key'] == notification_key:
                return obj
        return None

    def live_notifications_mark_as_read(self, seq_no):
        """
        Sets in the local state the last notification read, and appends the
        equivalent request to the queue.
        """
        self.state['LiveNotificationsLastRead'] = seq_no
        item = {
            'type': 'live_notifications_mark_as_read',
            'timestamp': self._generate_timestamp(),
            'args': {
                'seq_no': seq_no,
            },
        }
        self.queue.append(item)

    # User
    def user_update(self, **kwargs):
        """
        Updates the user data, and appends the equivalent request to the queue.
        """
        self.state['User'].update(kwargs)
        kwargs['token'] = self.api_token
        item = {
            'type': 'user_update',
            'timestamp': self._generate_timestamp(),
            'args': kwargs,
        }
        self.queue.append(item)

    # Sharing
    def share_project(self, project_id, email, message='', **kwargs):
        """
        Appends a request to the queue, to share a project with a user.
        """
        ts = self._generate_timestamp()
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
            'timestamp': self._generate_timestamp(),
            'args': {
                'project_id': project_id,
                'email': email,
            },
        }
        self.queue.append(item)

    def accept_invitation(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to accept an invitation to share a
        project.
        """
        item = {
            'type': 'accept_invitation',
            'timestamp': self._generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(item)

    def reject_invitation(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to reject an invitation to share a
        project.
        """
        item = {
            'type': 'reject_invitation',
            'timestamp': self._generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(item)

    def delete_invitation(self, invitation_id):
        """
        Appends a request to the queue, to delete an invitation to share a
        project.
        """
        item = {
            'type': 'delete_invitation',
            'timestamp': self._generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
            },
        }
        self.queue.append(item)

    def take_ownership(self, project_id):
        """
        Appends a request to the queue, take ownership of a shared project.
        """
        item = {
            'type': 'take_ownership',
            'timestamp': self._generate_timestamp(),
            'args': {
                'id': project_id,
            },
        }
        self.queue.append(item)

    def biz_accept_invitation(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to accept a business invitation to
        share a project.
        """
        item = {
            'type': 'biz_accept_invitation',
            'timestamp': self._generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(item)

    def biz_reject_invitation(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to reject a business invitation to
        share a project.
        """
        item = {
            'type': 'biz_reject_invitation',
            'timestamp': self._generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(item)
