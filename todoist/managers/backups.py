# -*- coding: utf-8 -*-
from .generic import Manager


class BackupsManager(Manager):
    def get(self):
        """
        Get backups.
        """
        params = {"token": self.token}
        return self.api._get("backups/get", params=params)
