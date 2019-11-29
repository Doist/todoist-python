# -*- coding: utf-8 -*-
from .generic import AllMixin, GetByIdMixin, Manager, SyncMixin


class LiveNotificationsManager(Manager, GetByIdMixin, AllMixin, SyncMixin):

    state_name = "live_notifications"
    object_type = None  # there is no object type associated

    def set_last_read(self, id):
        """
        Sets the last known notification.
        """
        cmd = {
            "type": "live_notifications_set_last_read",
            "uuid": self.api.generate_uuid(),
            "args": {"id": id},
        }
        self.queue.append(cmd)

    def mark_read(self, id):
        """
        Marks notification as read.
        """
        cmd = {
            "type": "live_notifications_mark_read",
            "uuid": self.api.generate_uuid(),
            "args": {"id": id},
        }
        self.queue.append(cmd)

    def mark_read_all(self):
        """
        Marks all notifications as read.
        """
        cmd = {
            "type": "live_notifications_mark_read_all",
            "uuid": self.api.generate_uuid(),
        }
        self.queue.append(cmd)

    def mark_unread(self, id):
        """
        Marks notification as unread.
        """
        cmd = {
            "type": "live_notifications_mark_unread",
            "uuid": self.api.generate_uuid(),
            "args": {"id": id},
        }
        self.queue.append(cmd)
