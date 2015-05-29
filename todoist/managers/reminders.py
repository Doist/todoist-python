# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class RemindersManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Reminders'
    object_type = 'reminder'
    resource_type = 'reminders'

    def add(self, item_id, **kwargs):
        """
        Adds a reminder to the local state, and appends the equivalent request
        to the queue.
        """
        obj = models.Reminder({'item_id': item_id}, self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            'type': 'reminder_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(cmd)
        return obj

    def update(self, reminder_id, **kwargs):
        """
        Updates reminder, and appends the equivalent request to the queue.
        """
        obj = self.get_by_id(reminder_id)
        if obj:
            obj.data.update(kwargs)

        args = {'id': reminder_id}
        args.update(kwargs)
        cmd = {
            'type': 'reminder_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.queue.append(cmd)

    def delete(self, reminder_id):
        """
        Deletes reminder, and appends the equivalent request to the queue.
        """
        obj = self.get_by_id(reminder_id)
        if obj:
            self.state[self.state_name].remove(obj)

        cmd = {
            'type': 'reminder_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': reminder_id,
            },
        }
        self.queue.append(cmd)
