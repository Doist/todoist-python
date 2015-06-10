# -*- coding: utf-8 -*-
from .generic import Manager


class UserManager(Manager):

    def update(self, **kwargs):
        """
        Updates the user data, by appending the equivalent request to the queue.
        """
        cmd = {
            'type': 'user_update',
            'uuid': self.api.generate_uuid(),
            'args': kwargs,
        }
        self.queue.append(cmd)

    def update_goals(self, **kwargs):
        """
        Update the user's karma goals.
        """
        cmd = {
            'type': 'update_goals',
            'uuid': self.api.generate_uuid(),
            'args': kwargs,
        }
        self.queue.append(cmd)

    def sync(self):
        return self.api.sync(resource_types=['user'])

    def get(self, key=None, default=None):
        ret = self.state['User']
        if key is not None:
            ret = ret.get(key, default)
        return ret

    def get_id(self):
        return self.state['UserId']
