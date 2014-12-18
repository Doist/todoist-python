# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager


class RemindersManager(Manager):

    def get_by_id(self, reminder_id):
        """
        Finds and returns reminder based on its id.
        """
        for obj in self.state['Reminders']:
            if obj['id'] == reminder_id or obj.temp_id == str(reminder_id):
                return obj
        return None

    def add(self, item_id, **kwargs):
        """
        Adds a reminder to the local state, and appends the equivalent request
        to the queue.
        """
        obj = models.Reminder({'item_id': item_id}, self.api)
        ts = self.api.generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state['Reminders'].append(obj)
        item = {
            'type': 'reminder_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj
