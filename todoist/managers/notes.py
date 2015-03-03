# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class NotesManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Notes'
    object_type = 'note'
    resource_type = 'notes'

    def add(self, item_id, content, **kwargs):
        """
        Adds a note to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.Note({'item_id': item_id, 'content': content}, self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        item = {
            'type': 'note_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(item)
        return obj
