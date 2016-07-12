# -*- coding: utf-8 -*-
from .generic import Manager, GetByIdMixin, AllMixin, SyncMixin


class LiveNotificationsManager(Manager, GetByIdMixin, AllMixin, SyncMixin):

    state_name = 'live_notifications'
    object_type = None  # there is no object type associated

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
