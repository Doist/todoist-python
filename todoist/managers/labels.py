# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class LabelsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Labels'
    object_type = 'label'
    resource_type = 'labels'

    def add(self, name, **kwargs):
        """
        Creates a local label object, and appends the equivalent request to the
        queue.
        """
        obj = models.Label({'name': name}, self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            'type': 'label_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(cmd)
        return obj

    def update(self, label_id, **kwargs):
        """
        Updates a label remotely, by appending the equivalent request to the
        queue.
        """
        args = {'id': label_id}
        args.update(kwargs)
        cmd = {
            'type': 'label_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.queue.append(cmd)

    def delete(self, label_id):
        """
        Deletes a label remotely, by appending the equivalent request to the
        queue.
        """
        cmd = {
            'type': 'label_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': label_id,
            },
        }
        self.queue.append(cmd)

    def update_orders(self, id_order_mapping):
        """
        Updates the orders of multiple labels remotely, by appending the
        equivalent request to the queue.
        """
        cmd = {
            'type': 'label_update_orders',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id_order_mapping': id_order_mapping,
            },
        }
        self.queue.append(cmd)
