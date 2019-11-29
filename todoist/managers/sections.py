# -*- coding: utf-8 -*-
from .. import models
from .generic import AllMixin, GetByIdMixin, Manager, SyncMixin


class SectionsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = "sections"
    object_type = "section"

    def add(self, name, project_id, **kwargs):
        """
        Creates a local section object.
        """
        obj = models.Section({"name": name, "project_id": project_id}, self.api)
        obj.temp_id = obj["id"] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            "type": "section_add",
            "temp_id": obj.temp_id,
            "uuid": self.api.generate_uuid(),
            "args": {key: obj.data[key] for key in obj.data if key != "id"},
        }
        self.queue.append(cmd)
        return obj

    def update(self, section_id, **kwargs):
        """
        Updates a section remotely.
        """
        args = {"id": section_id}
        args.update(kwargs)
        cmd = {
            "type": "section_update",
            "uuid": self.api.generate_uuid(),
            "args": args,
        }
        self.queue.append(cmd)

    def delete(self, section_id):
        """
        Delete a section remotely.
        """
        cmd = {
            "type": "section_delete",
            "uuid": self.api.generate_uuid(),
            "args": {"id": section_id},
        }
        self.queue.append(cmd)

    def move(self, section_id, project_id):
        """
        Moves section to another project remotely.
        """
        cmd = {
            "type": "section_move",
            "uuid": self.api.generate_uuid(),
            "args": {"id": section_id, "project_id": project_id},
        }
        self.queue.append(cmd)

    def archive(self, section_id, **kwargs):
        """
        Marks section as archived remotely.
        """
        args = {
            "id": section_id,
        }
        if kwargs.get("date_archived"):
            args["date_archived"] = kwargs.get("date_archived")
        cmd = {
            "type": "section_archive",
            "uuid": self.api.generate_uuid(),
            "args": args,
        }
        self.queue.append(cmd)

    def unarchive(self, section_id):
        """
        Marks section as unarchived remotely.
        """
        cmd = {
            "type": "section_unarchive",
            "uuid": self.api.generate_uuid(),
            "args": {"id": section_id},
        }
        self.queue.append(cmd)

    def reorder(self, sections):
        """
        Updates the section_order of the specified sections.
        """
        cmd = {
            "type": "section_reorder",
            "uuid": self.api.generate_uuid(),
            "args": {"sections": sections},
        }
        self.queue.append(cmd)

    def get(self, section_id):
        """
        Gets an existing section.
        """
        params = {"token": self.token, "section_id": section_id}
        obj = self.api._get("sections/get", params=params)
        if obj and "error" in obj:
            return None
        data = {"sections": []}
        if obj.get("section"):
            data["sections"].append(obj.get("section"))
        self.api._update_state(data)
        return obj
