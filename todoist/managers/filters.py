# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin


class FiltersManager(Manager, AllMixin, GetByIdMixin):

    state_name = 'Filters'

    def add(self, name, query, **kwargs):
        """
        Adds a filter to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Filter({'name': name, 'query': query}, self.api)
        ts = self.api.generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        item = {
            'type': 'filter_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    def update_orders(self, id_order_mapping):
        """
        Updates in the local state the orders of multiple filters, and appends
        the equivalent request to the queue.
        """
        for filter_id in id_order_mapping.keys():
            obj = self.get_by_id(filter_id)
            if obj:
                obj['item_order'] = id_order_mapping[filter_id]
        item = {
            'type': 'filter_update_orders',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'id_order_mapping': id_order_mapping,
            },
        }
        self.queue.append(item)
