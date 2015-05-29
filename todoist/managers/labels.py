# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class LabelsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Labels'
    object_type = 'label'
    resource_type = 'labels'

    def add(self, name, **kwargs):
        """
        Registers a label in the local state, and appends the equivalent
        request to the queue.
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
        Updates label, and appends the equivalent request to the queue.
        """
        obj = self.get_by_id(label_id)
        if obj:
            obj.data.update(kwargs)

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
        Deletes label, and appends the equivalent request to the queue.
        """
        obj = self.get_by_id(label_id)
        if obj:
            self.state[self.state_name].remove(obj)

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
        Updates in the local state the orders of multiple labels, and appends
        the equivalent request to the queue.
        """
        for filter_id in id_order_mapping.keys():
            obj = self.get_by_id(filter_id)
            if obj:
                obj['item_order'] = id_order_mapping[filter_id]
        cmd = {
            'type': 'label_update_orders',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id_order_mapping': id_order_mapping,
            },
        }
        self.queue.append(cmd)
