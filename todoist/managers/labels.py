# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager


class LabelsManager(Manager):

    def get_by_id(self, label_id):
        """
        Finds and returns label based on its id.
        """
        for obj in self.state['Labels']:
            if obj['id'] == label_id or obj.temp_id == str(label_id):
                return obj
        return None

    def register(self, name, **kwargs):
        """
        Registers a label in the local state, and appends the equivalent
        request to the queue.
        """
        obj = models.Label({'name': name}, self.api)
        ts = self.api.generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Labels'].append(obj)
        item = {
            'type': 'label_register',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj
