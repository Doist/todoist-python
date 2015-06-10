# -*- coding: utf-8 -*-
from .generic import Manager, AllMixin, SyncMixin


class LiveNotificationsManager(Manager, AllMixin, SyncMixin):

    state_name = 'LiveNotifications'
    object_type = 'live_notification'
    resource_type = 'live_notifications'

    def get_by_key(self, notification_key):
        """
        Finds and returns live notification based on its key.
        """
        for obj in self.state[self.state_name]:
            if obj['notification_key'] == notification_key:
                return obj
        return None

    def mark_as_read(self, seq_no):
        """
        Sets in the local state the last notification read, and appends the
        equivalent request to the queue.
        """
        cmd = {
            'type': 'live_notifications_mark_as_read',
            'uuid': self.api.generate_uuid(),
            'args': {
                'seq_no': seq_no,
            },
        }
        self.queue.append(cmd)
