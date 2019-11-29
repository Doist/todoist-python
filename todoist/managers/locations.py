# -*- coding: utf-8 -*-
from .generic import AllMixin, Manager, SyncMixin


class LocationsManager(Manager, AllMixin, SyncMixin):

    state_name = "locations"
    object_type = None  # there is no local state associated

    def clear(self):
        """
        Clears the locations.
        """
        cmd = {
            "type": "clear_locations",
            "uuid": self.api.generate_uuid(),
            "args": {},
        }
        self.queue.append(cmd)
