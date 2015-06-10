# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class GenericNotesManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    object_type = 'note'
    resource_type = 'notes'

    def update(self, note_id, **kwargs):
        """
        Updates an note remotely, by appending the equivalent request to the
        queue.
        """
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
        Deletes an note remotely, by appending the equivalent request to the
        queue.
        """
        cmd = {
            'type': 'note_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': note_id,
            },
        }
        self.queue.append(cmd)


class NotesManager(GenericNotesManager):

    state_name = 'Notes'

    def add(self, item_id, content, **kwargs):
        """
        Creates a local item note object, and appends the equivalent request to
        the queue.
        """
        obj = models.Note({'item_id': item_id, 'content': content}, self.api)
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


class ProjectNotesManager(GenericNotesManager):

    state_name = 'ProjectNotes'

    def add(self, project_id, content, **kwargs):
        """
        Creates a local project note object, and appends the equivalent request
        to the queue.
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
