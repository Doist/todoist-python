# -*- coding: utf-8 -*-
from .generic import Manager


class QuickManager(Manager):
    def add(self, text, **kwargs):
        """
        Quick add task implementation.
        """
        params = {'token': self.token, 'text': text}
        params.update(kwargs)
        return self.api._get('quick/add', params=params)
