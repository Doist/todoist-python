# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class LabelsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Labels'
    object_type = 'label'
    resource_type = 'labels'

    def register(self, name, **kwargs):
        """
        Registers a label in the local state, and appends the equivalent
        request to the queue.
        """
        obj = models.Label({'name': name}, self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        item = {
            'type': 'label_register',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(item)
        return obj
