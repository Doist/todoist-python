# -*- coding: utf-8 -*-
from .generic import Manager


class LiveNotificationsManager(Manager):

    def get_by_key(self, notification_key):
        """
        Finds and returns live notification based on its key.
        """
        for obj in self.state['LiveNotifications']:
            if obj['notification_key'] == notification_key:
                return obj
        return None

    def mark_as_read(self, seq_no):
        """
        Sets in the local state the last notification read, and appends the
        equivalent request to the queue.
        """
        self.state['LiveNotificationsLastRead'] = seq_no
        item = {
            'type': 'live_notifications_mark_as_read',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'seq_no': seq_no,
            },
        }
        self.queue.append(item)
