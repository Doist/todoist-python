# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin


class ProjectNotesManager(Manager, AllMixin, GetByIdMixin):

    state_name = 'ProjectNotes'

    def add(self, project_id, content, **kwargs):
        """
        Adds a note to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.ProjectNote({'project_id': project_id, 'content': content},
                                 self.api)
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
