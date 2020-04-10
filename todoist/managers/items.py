# -*- coding: utf-8 -*-
from .. import models
from .generic import AllMixin, GetByIdMixin, Manager, SyncMixin


class ItemsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = "items"
    object_type = "item"

    def add(self, content, **kwargs):
        """
        Creates a local item object.
        """
        project_id = kwargs.get("project_id")
        if not project_id:
            project_id = self.state["user"]["inbox_project"]
        obj = models.Item({"content": content, "project_id": project_id}, self.api)
        obj.temp_id = obj["id"] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            "type": "item_add",
            "temp_id": obj.temp_id,
            "uuid": self.api.generate_uuid(),
            "args": {key: obj.data[key] for key in obj.data if key != "id"},
        }
        self.queue.append(cmd)
        return obj

    def update(self, item_id, **kwargs):
        """
        Updates an item remotely.
        """
        args = {"id": item_id}
        args.update(kwargs)
        cmd = {
            "type": "item_update",
            "uuid": self.api.generate_uuid(),
            "args": args,
        }
        self.queue.append(cmd)

    def delete(self, item_id):
        """
        Deletes an item remotely.
        """
        cmd = {
            "type": "item_delete",
            "uuid": self.api.generate_uuid(),
            "args": {"id": item_id},
        }
        self.queue.append(cmd)

    def move(self, item_id, **kwargs):
        """
        Moves item to another parent, project, or section remotely.
        """
        args = {
            "id": item_id,
        }
        if "parent_id" in kwargs:
            args["parent_id"] = kwargs.get("parent_id")
        elif "project_id" in kwargs:
            args["project_id"] = kwargs.get("project_id")
        elif "section_id" in kwargs:
            args["section_id"] = kwargs.get("section_id")
        else:
            raise TypeError("move() takes one of parent_id, project_id, or section_id arguments")
        cmd = {"type": "item_move", "uuid": self.api.generate_uuid(), "args": args}
        self.queue.append(cmd)

    def close(self, item_id):
        """
        Marks item as done
        """
        cmd = {
            "type": "item_close",
            "uuid": self.api.generate_uuid(),
            "args": {"id": item_id},
        }
        self.queue.append(cmd)

    def complete(self, item_id, date_completed=None, force_history=None):
        """
        Marks item as completed remotely.
        """
        args = {
            "id": item_id,
        }
        if date_completed is not None:
            args["date_completed"] = date_completed
        if force_history is not None:
            args["force_history"] = force_history
        cmd = {
            "type": "item_complete",
            "uuid": self.api.generate_uuid(),
            "args": args,
        }
        self.queue.append(cmd)

    def uncomplete(self, item_id):
        """
        Marks item as uncompleted remotely.
        """
        cmd = {
            "type": "item_uncomplete",
            "uuid": self.api.generate_uuid(),
            "args": {"id": item_id},
        }
        self.queue.append(cmd)

    def archive(self, item_id):
        """
        Marks item as archived remotely.
        """
        cmd = {
            "type": "item_archive",
            "uuid": self.api.generate_uuid(),
            "args": {"id": item_id},
        }
        self.queue.append(cmd)

    def unarchive(self, item_id):
        """
        Marks item as unarchived remotely.
        """
        cmd = {
            "type": "item_unarchive",
            "uuid": self.api.generate_uuid(),
            "args": {"id": item_id},
        }
        self.queue.append(cmd)

    def update_date_complete(self, item_id, due=None):
        """
        Completes a recurring task remotely.
        """
        args = {
            "id": item_id,
        }
        if due:
            args["due"] = due
        cmd = {
            "type": "item_update_date_complete",
            "uuid": self.api.generate_uuid(),
            "args": args,
        }
        self.queue.append(cmd)

    def reorder(self, items):
        """
        Updates the child_order of the specified items.
        """
        cmd = {
            "type": "item_reorder",
            "uuid": self.api.generate_uuid(),
            "args": {"items": items},
        }
        self.queue.append(cmd)

    def update_day_orders(self, ids_to_orders):
        """
        Updates in the local state the day orders of multiple items remotely.
        """
        cmd = {
            "type": "item_update_day_orders",
            "uuid": self.api.generate_uuid(),
            "args": {"ids_to_orders": ids_to_orders},
        }
        self.queue.append(cmd)

    def get_completed(self, project_id, **kwargs):
        """
        Returns a project's completed items.
        """
        params = {"token": self.token, "project_id": project_id}
        params.update(kwargs)
        return self.api._get("items/get_completed", params=params)

    def get(self, item_id):
        """
        Gets an existing item.
        """
        params = {"token": self.token, "item_id": item_id}
        obj = self.api._get("items/get", params=params)
        if obj and "error" in obj:
            return None

        data = {"projects": [], "items": [], "notes": []}
        if obj.get("project"):
            data["projects"].append(obj.get("project"))
        if obj.get("item"):
            data["items"].append(obj.get("item"))
        if obj.get("notes"):
            data["notes"] += obj.get("notes")
        self.api._update_state(data)
        return obj
