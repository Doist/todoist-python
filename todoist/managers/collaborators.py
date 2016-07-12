# -*- coding: utf-8 -*-
from .generic import Manager, GetByIdMixin, SyncMixin


class CollaboratorsManager(Manager, GetByIdMixin, SyncMixin):

    state_name = 'collaborators'
    object_type = None  # there is no object type associated
