# -*- coding: utf-8 -*-
from .generic import Manager, GetByIdMixin, SyncMixin


class CollaboratorsManager(Manager, GetByIdMixin, SyncMixin):

    state_name = 'collaborators'
    object_type = None  # there is no object type associated

    def delete(self, project_id, email):
        """
        Deletes a collaborator from a shared project.
        """
        cmd = {
            'type': 'delete_collaborator',
            'uuid': self.api.generate_uuid(),
            'args': {
                'project_id': project_id,
                'email': email,
            },
        }
        self.queue.append(cmd)
