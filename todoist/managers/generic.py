# -*- coding: utf-8 -*-
class Manager(object):

    # should be re-defined in a subclass
    state_name = None
    object_type = None
    resource_type = None

    def __init__(self, api):
        self.api = api

    # shortcuts

    @property
    def state(self):
        return self.api.state

    @property
    def queue(self):
        return self.api.queue


class AllMixin(object):
    def all(self, filt=None):
        return list(filter(filt, self.state[self.state_name]))


class GetByIdMixin(object):

    def get_by_id(self, obj_id, only_local=False):
        """
        Finds and returns the object based on its id.
        """
        for obj in self.state[self.state_name]:
            if obj['id'] == obj_id or obj.temp_id == str(obj_id):
                return obj

        if not only_local:
            getter = getattr(self.api, 'get_%s' % self.object_type)
            return getter(obj_id)

        return None


class SyncMixin(object):
    """
    Syncs this specific type of objects.
    """
    def sync(self):
        return self.api.sync(resource_types=[self.resource_type])
