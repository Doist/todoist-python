# -*- coding: utf-8 -*-
from .generic import Manager, GetByIdMixin, SyncMixin


class CollaboratorsManager(Manager, GetByIdMixin, SyncMixin):

    state_name = 'Collaborators'
    object_type = None  # there is no object type associated
    resource_type = 'collaborators'

    def get_by_id(self, user_id):
        """
        Finds and returns the collaborator based on the user id.
        """
        super(CollaboratorsManager, self).get_by_id(user_id, only_local=True)
