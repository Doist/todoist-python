# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class FiltersManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Filters'
    object_type = 'filter'
    resource_type = 'filters'

    def add(self, name, query, **kwargs):
        """
        Adds a filter to the local state, and appends the equivalent request to
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
        Updates filter, and appends the equivalent request to the queue.
        """
        obj = self.get_by_id(filter_id)
        if obj:
            obj.data.update(kwargs)

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
        Deletes filter, and appends the equivalent request to the queue.
        """
        obj = self.get_by_id(filter_id)
        if obj:
            self.state[self.state_name].remove(obj)

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
        Updates in the local state the orders of multiple filters, and appends
        the equivalent request to the queue.
        """
        for filter_id in id_order_mapping.keys():
            obj = self.get_by_id(filter_id)
            if obj:
                obj['item_order'] = id_order_mapping[filter_id]
        cmd = {
            'type': 'filter_update_orders',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id_order_mapping': id_order_mapping,
            },
        }
        self.queue.append(cmd)
