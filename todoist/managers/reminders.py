# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin


class RemindersManager(Manager, AllMixin, GetByIdMixin):

    state_name = 'Reminders'
    object_type = 'reminder'

    def add(self, item_id, **kwargs):
        """
        Adds a reminder to the local state, and appends the equivalent request
        to the queue.
        """
        obj = models.Reminder({'item_id': item_id}, self.api)
        ts = self.api.generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        item = {
            'type': 'reminder_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj
