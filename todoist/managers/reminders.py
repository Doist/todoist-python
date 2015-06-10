# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class RemindersManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Reminders'
    object_type = 'reminder'
    resource_type = 'reminders'

    def add(self, item_id, **kwargs):
        """
        Creates a local reminder object, and appends the equivalent request
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
        Updates a reminder remotely, by appending the equivalent request to the
        queue.
        """
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
        Deletes a reminder remotely, by appending the equivalent request to the
        queue.
        """
        cmd = {
            'type': 'reminder_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': reminder_id,
            },
        }
        self.queue.append(cmd)
