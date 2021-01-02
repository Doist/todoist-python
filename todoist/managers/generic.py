# -*- coding: utf-8 -*-
class Manager(object):

    # should be re-defined in a subclass
    state_name = None
    object_type = None

    def __init__(self, api):
        self.api = api

    # shortcuts
    @property
    def state(self):
        return self.api.state

    @property
    def queue(self):
        return self.api.queue

    @property
    def token(self):
        return self.api.token


class AllMixin(object):
    def all(self, filt=None):
        return list(filter(filt, self.state[self.state_name].values()))


class GetByIdMixin(object):
    def get_by_id(self, obj_id, only_local=False):
        """
        Finds and returns the object based on its id.
        """
        if str(obj_id) in self.state[self.state_name]:
            return self.state[self.state_name][str(obj_id)]

        for _, obj in self.state[self.state_name].items():
            if obj.temp_id == str(obj_id):
                return obj

        if not only_local and self.object_type is not None:
            getter = getattr(eval("self.api.%ss" % self.object_type), "get")
            data = getter(obj_id)

            if str(obj_id) in self.state[self.state_name]:
                return self.state[self.state_name]

            # retrieves from state, otherwise we return the raw data
            for _, obj in self.state[self.state_name].items():
                if obj.temp_id == str(obj_id):
                    return obj

            return data

        return None


class SyncMixin(object):
    """
    Syncs this specific type of objects.
    """

    def sync(self):
        return self.api.sync()
