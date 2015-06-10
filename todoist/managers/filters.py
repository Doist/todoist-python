# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class FiltersManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Filters'
    object_type = 'filter'
    resource_type = 'filters'

    def add(self, name, query, **kwargs):
        """
        Creates a local filter object, and appends the equivalent request to
        the queue.
        """
        obj = models.Filter({'name': name, 'query': query}, self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            'type': 'filter_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(cmd)
        return obj

    def update(self, filter_id, **kwargs):
        """
        Updates a filter remotely, by appending the equivalent request to the
        queue.
        """
        args = {'id': filter_id}
        args.update(kwargs)
        cmd = {
            'type': 'filter_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.queue.append(cmd)

    def delete(self, filter_id):
        """
        Deletes a filter remotely, by appending the equivalent request to the
        queue.
        """
        cmd = {
            'type': 'filter_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': filter_id,
            },
        }
        self.queue.append(cmd)

    def update_orders(self, id_order_mapping):
        """
        Updates the orders of multiple filters remotely, by appending the
        equivalent request to the queue.
        """
        cmd = {
            'type': 'filter_update_orders',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id_order_mapping': id_order_mapping,
            },
        }
        self.queue.append(cmd)
