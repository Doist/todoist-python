# -*- coding: utf-8 -*-
from .generic import Manager, AllMixin, SyncMixin


class LiveNotificationsManager(Manager, AllMixin, SyncMixin):

    state_name = 'live_notifications'
    object_type = 'live_notification'

    def get_by_key(self, notification_key):
        """
        Finds and returns live notification based on its key.
        """
        for obj in self.state[self.state_name]:
            if obj['notification_key'] == notification_key:
                return obj
        return None

    def set_last_read(self, id):
        """
        Sets in the local state the last notification read, and appends the
        equivalent request to the queue.
        """
        cmd = {
            'type': 'live_notifications_set_last_read',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': id,
            },
        }
        self.queue.append(cmd)
