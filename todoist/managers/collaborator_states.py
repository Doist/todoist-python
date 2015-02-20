# -*- coding: utf-8 -*-
from .generic import Manager, SyncMixin


class CollaboratorStatesManager(Manager, SyncMixin):

    state_name = 'CollaboratorStates'
    object_type = None  # there is no object type associated
    resource_type = 'collaborators'

    def get_by_ids(self, project_id, user_id):
        """
        Finds and returns the collaborator state based on the project and user
        ids.
        """
        for obj in self.state[self.state_name]:
            if obj['project_id'] == project_id and obj['user_id'] == user_id:
                return obj
        return None
