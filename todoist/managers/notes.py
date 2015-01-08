# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin


class NotesManager(Manager, AllMixin, GetByIdMixin):

    state_name = 'Notes'

    def add(self, item_id, content, **kwargs):
        """
        Adds a note to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Note({'item_id': item_id, 'content': content}, self.api)
        ts = self.api.generate_timestamp()
        obj.temp_id = obj['id'] = '$' + ts
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        item = {
            'type': 'note_add',
            'temp_id': obj.temp_id,
            'timestamp': ts,
            'args': obj.data,
        }
        self.queue.append(item)
        return obj
