# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class GenericNotesManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    object_type = 'note'

    def update(self, note_id, **kwargs):
        """
        Updates an note remotely.
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
        Deletes an note remotely.
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

    state_name = 'notes'

    def add(self, item_id, content, **kwargs):
        """
        Creates a local item note object.
        """
        obj = models.Note({'item_id': item_id, 'content': content}, self.api)
        obj.temp_id = obj['id'] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            'type': 'note_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': {key: obj.data[key] for key in obj.data if key != 'id'}
        }
        self.queue.append(cmd)
        return obj

    def get(self, note_id):
        """
        Gets an existing note.
        """
        params = {'token': self.token,
                  'note_id': note_id}
        obj = self.api._get('notes/get', params=params)
        if obj and 'error' in obj:
            return None
        data = {'notes': []}
        if obj.get('note'):
            data['notes'].append(obj.get('note'))
        self.api._update_state(data)
        return obj


class ProjectNotesManager(GenericNotesManager):

    state_name = 'project_notes'

    def add(self, project_id, content, **kwargs):
        """
        Creates a local project note object.
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
            'args': {key: obj.data[key] for key in obj.data if key != 'id'}
        }
        self.queue.append(cmd)
        return obj
