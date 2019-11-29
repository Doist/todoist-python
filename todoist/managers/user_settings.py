# -*- coding: utf-8 -*-
from .generic import Manager


class UserSettingsManager(Manager):
    def update(self, **kwargs):
        """
        Updates the user's settings.
        """
        cmd = {
            "type": "user_settings_update",
            "uuid": self.api.generate_uuid(),
            "args": kwargs,
        }
        self.queue.append(cmd)
