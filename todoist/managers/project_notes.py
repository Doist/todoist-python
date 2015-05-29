# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class ProjectNotesManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'ProjectNotes'
    object_type = 'note'
    resource_type = 'notes'

    def add(self, project_id, content, **kwargs):
        """
        Adds a note to the local state, and appends the equivalent request to
        the queue.
        """
        obj = models.ProjectNote({'project_id': project_id, 'content': content},
                                 self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            'type': 'note_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(cmd)
        return obj

    def update(self, note_id, **kwargs):
        """
        Updates note, and appends the equivalent request to the queue.
        """
        obj = self.get_by_id(note_id)
        if obj:
            obj.data.update(kwargs)

        args = {'id': note_id}
        args.update(kwargs)
        cmd = {
            'type': 'note_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.queue.append(cmd)

    def delete(self, note_id):
        """
        Deletes note, and appends the equivalent request to the queue.
        """
        obj = self.get_by_id(note_id)
        if obj:
            self.state[self.state_name].remove(obj)

        cmd = {
            'type': 'note_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': note_id,
            },
        }
        self.queue.append(cmd)
