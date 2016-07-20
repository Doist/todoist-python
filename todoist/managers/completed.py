# -*- coding: utf-8 -*-
from .generic import Manager


class CompletedManager(Manager):
    def get_stats(self):
        """
        Returns the user's recent productivity stats.
        """
        return self.api._get('completed/get_stats',
                             params={'token': self.token})

    def get_all(self, **kwargs):
        """
        Returns all user's completed items.
        """
        params = {'token': self.token}
        params.update(kwargs)
        return self.api._get('completed/get_all', params=params)
