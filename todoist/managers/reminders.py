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
        item = {
            'type': 'reminder_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(item)
        return obj
