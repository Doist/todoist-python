# -*- coding: utf-8 -*-
from .generic import Manager, AllMixin, SyncMixin


class LocationsManager(Manager, AllMixin, SyncMixin):

    state_name = 'Locations'
    object_type = None  # there is no local state associated
    resource_type = 'locations'

    def clear(self):
        """
        Clears the locations.
        """
        cmd = {
            'type': 'clear_locations',
            'uuid': self.api.generate_uuid(),
            'args': {},
        }
        self.queue.append(cmd)
