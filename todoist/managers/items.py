# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class ItemsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Items'
    object_type = 'item'
    resource_type = 'items'

    def add(self, content, project_id, **kwargs):
        """
        Adds an item to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Item({'content': content, 'project_id': project_id},
                          self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            'type': 'item_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(cmd)
        return obj

    def update(self, item_id, **kwargs):
        obj = self.get_by_id(item_id)
        if obj:
            obj.data.update(kwargs)

        args = {'id': item_id}
        args.update(kwargs)
        cmd = {
            'type': 'item_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.queue.append(cmd)

    def delete(self, item_ids):
        """
        Deletes items, and appends the equivalent request to the queue.
        """
        for item_id in item_ids:
            obj = self.get_by_id(item_id)
            if obj:
                self.state[self.state_name].remove(obj)

        cmd = {
            'type': 'item_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'ids': item_ids
            }
        }
        self.queue.append(cmd)

    def move(self, project_items, to_project):
        """
        Moves items to another project, and appends the equivalent request to
        the queue.
        """
        for _, item_ids in project_items.items():
            for item_id in item_ids:
                obj = self.get_by_id(item_id)
                if obj:
                    obj['project_id'] = to_project

        cmd = {
            'type': 'item_move',
            'uuid': self.api.generate_uuid(),
            'args': {
                'project_items': project_items,
                'to_project': to_project,
            },
        }
        self.queue.append(cmd)

    def complete(self, project_id, item_ids, force_history=0):
        """
        Marks items as completed, and appends the equivalent request to the
        queue.
        """
        for item_id in item_ids:
            obj = self.get_by_id(item_id)
            if obj:
                obj['checked'] = 1
                obj['in_history'] = force_history

        cmd = {
            'type': 'item_complete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'project_id': project_id,
                'ids': item_ids,
                'force_history': force_history,
            },
        }
        self.queue.append(cmd)

    def uncomplete(self, project_id, item_ids, update_item_orders=1,
                   restore_state=None):
        """
        Marks items as not completed, and appends the equivalent request to the
        queue.
        """
        for item_id in item_ids:
            obj = self.get_by_id(item_id)
            if obj:
                obj['checked'] = 0
                obj['in_history'] = 0
                if restore_state and item_id in restore_state:
                    obj['in_history'] = restore_state[item_id][0]
                    obj['checked'] = restore_state[item_id][1]
                    obj['item_order'] = restore_state[item_id][2]
                    obj['indent'] = restore_state[item_id][3]

        args = {
            'project_id': project_id,
            'ids': item_ids,
            'update_item_orders': update_item_orders,
        }
        if restore_state:
            args['restore_state'] = restore_state
        cmd = {
            'type': 'item_uncomplete',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.queue.append(cmd)

    def update_date_complete(self, item_id, new_date_utc, date_string,
                             is_forward):
        """
        Completes a recurring task, and appends the equivalent request to the
        queue.
        """
        obj = self.get_by_id(item_id)
        if obj:
            obj['new_date_utc'] = new_date_utc
            obj['date_string'] = date_string
            obj['is_forward'] = is_forward

        cmd = {
            'type': 'item_update_date_complete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': item_id,
                'new_date_utc': new_date_utc,
                'date_string': date_string,
                'is_forward': is_forward,
            },
        }
        self.queue.append(cmd)

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

        cmd = {
            'type': 'item_uncomplete_update_meta',
            'uuid': self.api.generate_uuid(),
            'args': {
                'project_id': project_id,
                'ids_to_metas': ids_to_metas,
            },
        }
        self.queue.append(cmd)

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

        cmd = {
            'type': 'item_update_orders_indents',
            'uuid': self.api.generate_uuid(),
            'args': {
                'ids_to_orders_indents': ids_to_orders_indents,
            },
        }
        self.queue.append(cmd)

    def update_day_orders(self, ids_to_orders):
        """
        Updates in the local state the day orders of multiple items, and
        appends the equivalent request to the queue.
        """
        for item_id in ids_to_orders.keys():
            obj = self.get_by_id(item_id)
            if obj:
                obj['day_order'] = ids_to_orders[item_id]

        cmd = {
            'type': 'item_update_day_orders',
            'uuid': self.api.generate_uuid(),
            'args': {
                'ids_to_orders': ids_to_orders,
            },
        }
        self.queue.append(cmd)
