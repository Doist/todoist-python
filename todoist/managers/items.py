# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin


class ItemsManager(Manager, AllMixin, GetByIdMixin):

    state_name = 'Items'

    def add(self, content, project_id, **kwargs):
        """
        Adds an item to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Item({'content': content, 'project_id': project_id},
                          self.api)
        ts = self.api.generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        item = {
            'type': 'item_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    def uncomplete_update_meta(self, project_id, ids_to_metas):
        """
        Marks an item as completed in the local state, and appends the
        equivalent request to the queue.
        """
        for item_id in ids_to_metas.keys():
            obj = self.get_by_id(item_id)
            if obj:
                obj['in_history'] = ids_to_metas[item_id][0]
                obj['checked'] = ids_to_metas[item_id][1]
                obj['item_order'] = ids_to_metas[item_id][2]
        item = {
            'type': 'item_uncomplete_update_meta',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'project_id': project_id,
                'ids_to_metas': ids_to_metas,
            },
        }
        self.queue.append(item)

    def update_date_complete(self, item_id, new_date_utc, date_string,
                             is_forward):
        """
        Updates in the local state the date of multiple recurring tasks, and
        appends the equivalent request to the queue.
        """
        obj = self.get_by_id(item_id)
        if obj:
            obj['new_date_utc'] = new_date_utc
            obj['date_string'] = date_string
            obj['is_forward'] = is_forward
        item = {
            'type': 'item_update_date_complete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'id': item_id,
                'new_date_utc': new_date_utc,
                'date_string': date_string,
                'is_forward': is_forward,
            },
        }
        self.queue.append(item)

    def update_orders_indents(self, ids_to_orders_indents):
        """
        Updates in the local state the order and indents of multiple items, and
        appends the equivalent request to the queue.
        """
        for item_id in ids_to_orders_indents.keys():
            obj = self.get_by_id(item_id)
            if obj:
                obj['item_order'] = ids_to_orders_indents[item_id][0]
                obj['indent'] = ids_to_orders_indents[item_id][1]
        item = {
            'type': 'item_update_orders_indents',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'ids_to_orders_indents': ids_to_orders_indents,
            },
        }
        self.queue.append(item)

    def update_day_orders(self, ids_to_orders):
        """
        Updates in the local state the day orders of multiple items, and
        appends the equivalent request to the queue.
        """
        for item_id in ids_to_orders.keys():
            obj = self.get_by_id(item_id)
            if obj:
                obj['day_order'] = ids_to_orders[item_id]
        item = {
            'type': 'item_update_day_orders',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'ids_to_orders': ids_to_orders,
            },
        }
        self.queue.append(item)
