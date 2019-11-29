# -*- coding: utf-8 -*-
from .. import models
from .generic import AllMixin, GetByIdMixin, Manager, SyncMixin


class FiltersManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = "filters"
    object_type = "filter"

    def add(self, name, query, **kwargs):
        """
        Creates a local filter object.
        """
        obj = models.Filter({"name": name, "query": query}, self.api)
        obj.temp_id = obj["id"] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            "type": "filter_add",
            "temp_id": obj.temp_id,
            "uuid": self.api.generate_uuid(),
            "args": {key: obj.data[key] for key in obj.data if key != "id"},
        }
        self.queue.append(cmd)
        return obj

    def update(self, filter_id, **kwargs):
        """
        Updates a filter remotely.
        """
        args = {"id": filter_id}
        args.update(kwargs)
        cmd = {
            "type": "filter_update",
            "uuid": self.api.generate_uuid(),
            "args": args,
        }
        self.queue.append(cmd)

    def delete(self, filter_id):
        """
        Deletes a filter remotely.
        """
        cmd = {
            "type": "filter_delete",
            "uuid": self.api.generate_uuid(),
            "args": {"id": filter_id},
        }
        self.queue.append(cmd)

    def update_orders(self, id_order_mapping):
        """
        Updates the orders of multiple filters remotely.
        """
        cmd = {
            "type": "filter_update_orders",
            "uuid": self.api.generate_uuid(),
            "args": {"id_order_mapping": id_order_mapping},
        }
        self.queue.append(cmd)

    def get(self, filter_id):
        """
        Gets an existing filter.
        """
        params = {"token": self.token, "filter_id": filter_id}
        obj = self.api._get("filters/get", params=params)
        if obj and "error" in obj:
            return None
        data = {"filters": []}
        if obj.get("filter"):
            data["filters"].append(obj.get("filter"))
        self.api._update_state(data)
        return obj
