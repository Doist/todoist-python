# -*- coding: utf-8 -*-
from .generic import Manager


class UserManager(Manager):

    def update(self, **kwargs):
        """
        Updates the user data.
        """
        cmd = {
            'type': 'user_update',
            'uuid': self.api.generate_uuid(),
            'args': kwargs,
        }
        self.queue.append(cmd)

    def update_goals(self, **kwargs):
        """
        Updates the user's karma goals.
        """
        cmd = {
            'type': 'update_goals',
            'uuid': self.api.generate_uuid(),
            'args': kwargs,
        }
        self.queue.append(cmd)

    def sync(self):
        return self.api.sync()

    def get(self, key=None, default=None):
        ret = self.state['user']
        if key is not None:
            ret = ret.get(key, default)
        return ret

    def get_id(self):
        return self.state['user']['id']

    def login(self, email, password):
        """
        Logins user, and returns the response received by the server.
        """
        data = self.api._post('user/login', data={'email': email,
                              'password': password})
        if 'token' in data:
            self.api.token = data['token']
        return data

    def login_with_google(self, email, oauth2_token, **kwargs):
        """
        Logins user with Google account, and returns the response received by
        the server.

        """
        data = {'email': email, 'oauth2_token': oauth2_token}
        data.update(kwargs)
        data = self.api._post('user/login_with_google', data=data)
        if 'token' in data:
            self.api.token = data['token']
        return data

    def register(self, email, full_name, password, **kwargs):
        """
        Registers a new user.
        """
        data = {'email': email, 'full_name': full_name, 'password': password}
        data.update(kwargs)
        data = self.api._post('user/register', data=data)
        if 'token' in data:
            self.api.token = data['token']
        return data

    def delete(self, current_password, **kwargs):
        """
        Deletes an existing user.
        """
        params = {'token': self.token,
                  'current_password': current_password}
        params.update(kwargs)
        return self.api._get('user/delete', params=params)

    def update_notification_setting(self, notification_type, service,
                                    dont_notify):
        """
        Updates the user's notification settings.
        """
        return self.api._post('user/update_notification_setting',
                              data={'token': self.token,
                                    'notification_type': notification_type,
                                    'service': service,
                                    'dont_notify': dont_notify})
