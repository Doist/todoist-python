# -*- coding: utf-8 -*-
from .generic import Manager


class UserManager(Manager):

    def refresh(self):
        return self.api.sync(resource_types=[])

    def update(self, **kwargs):
        """
        Updates the user data, and appends the equivalent request to the queue.
        """
        self.state['User'].update(kwargs)
        item = {
            'type': 'user_update',
            'timestamp': self.api.generate_timestamp(),
            'args': kwargs,
        }
        self.queue.append(item)

    def get(self):
        return self.state['User']

    def get_id(self):
        return self.state['UserId']
