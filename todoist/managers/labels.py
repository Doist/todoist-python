# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class LabelsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'labels'
    object_type = 'label'

    def add(self, name, **kwargs):
        """
        Creates a local label object.
        """
        obj = models.Label({'name': name}, self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            'type': 'label_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': {key: obj.data[key] for key in obj.data if key != 'id'}
        }
        self.queue.append(cmd)
        return obj

    def update(self, label_id, **kwargs):
        """
        Updates a label remotely.
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
        Deletes a label remotely.
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
        Updates the orders of multiple labels remotely.
        """
        cmd = {
            'type': 'label_update_orders',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id_order_mapping': id_order_mapping,
            },
        }
        self.queue.append(cmd)

    def get(self, label_id):
        """
        Gets an existing label.
        """
        params = {'token': self.token,
                  'label_id': label_id}
        obj = self.api._get('labels/get', params=params)
        if obj and 'error' in obj:
            return None
        data = {'labels': []}
        if obj.get('label'):
            data['labels'].append(obj.get('label'))
        self.api._update_state(data)
        return obj
