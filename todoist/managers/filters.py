# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager


class FiltersManager(Manager):

    def get_by_id(self, filter_id):
        """
        Finds and returns filter based on its id.
        """
        for obj in self.state['Filters']:
            if obj['id'] == filter_id or obj.temp_id == str(filter_id):
                return obj
        return None

    def add(self, name, query, **kwargs):
        """
        Adds a filter to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Filter({'name': name, 'query': query}, self.api)
        ts = self.api.generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Filters'].append(obj)
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
