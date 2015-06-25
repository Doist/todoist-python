# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class ItemsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Items'
    object_type = 'item'
    resource_type = 'items'

    def add(self, content, project_id, **kwargs):
        """
        Creates a local item object, by appending the equivalent request to the
        queue.
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
        """
        Updates an item remotely, by appending the equivalent request to the
        queue.
        """
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
        Deletes items remotely, by appending the equivalent request to the
        queue.
        """
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
        Moves items to another project remotely, by appending the equivalent
        request to the queue.
        """
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
        Marks items as completed remotely, by appending the equivalent request to the
        queue.
        """
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
        Marks items as not completed remotely, by appending the equivalent request to the
        queue.
        """
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

    def update_date_complete(self, item_id, new_date_utc=None, date_string=None,
                             is_forward=None):
        """
        Completes a recurring task remotely, by appending the equivalent
        request to the queue.
        """
        args = {
            'id': item_id,
        }
        if new_date_utc:
            args['new_date_utc'] = new_date_utc
        if date_string:
            args['date_string'] = date_string
        if is_forward:
            args['is_forward'] = is_forward
        cmd = {
            'type': 'item_update_date_complete',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.queue.append(cmd)

    def uncomplete_update_meta(self, project_id, ids_to_metas):
        """
        Marks an item as completed remotely, by appending the equivalent
        request to the queue.
        """
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
        Updates the order and indents of multiple items remotely, by appending
        the equivalent request to the queue.
        """
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
        Updates in the local state the day orders of multiple items remotely,
        by appending the equivalent request to the queue.
        """
        cmd = {
            'type': 'item_update_day_orders',
            'uuid': self.api.generate_uuid(),
            'args': {
                'ids_to_orders': ids_to_orders,
            },
        }
        self.queue.append(cmd)
