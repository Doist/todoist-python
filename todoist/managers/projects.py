# -*- coding: utf-8 -*-
from .. import models
from .generic import AllMixin, GetByIdMixin, Manager, SyncMixin


class ProjectsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = "projects"
    object_type = "project"

    def add(self, name, **kwargs):
        """
        Creates a local project object.
        """
        obj = models.Project({"name": name}, self.api)
        obj.temp_id = obj["id"] = "$" + self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            "type": "project_add",
            "temp_id": obj.temp_id,
            "uuid": self.api.generate_uuid(),
            "args": {key: obj.data[key] for key in obj.data if key != "id"},
        }
        self.queue.append(cmd)
        return obj

    def update(self, project_id, **kwargs):
        """
        Updates a project remotely.
        """
        obj = self.get_by_id(project_id)
        if obj:
            obj.data.update(kwargs)

        args = {"id": project_id}
        args.update(kwargs)
        cmd = {
            "type": "project_update",
            "uuid": self.api.generate_uuid(),
            "args": args,
        }
        self.queue.append(cmd)

    def delete(self, project_id):
        """
        Deletes a project remotely.
        """
        cmd = {
            "type": "project_delete",
            "uuid": self.api.generate_uuid(),
            "args": {"id": project_id},
        }
        self.queue.append(cmd)

    def archive(self, project_id):
        """
        Marks project as archived remotely.
        """
        cmd = {
            "type": "project_archive",
            "uuid": self.api.generate_uuid(),
            "args": {"id": project_id},
        }
        self.queue.append(cmd)

    def unarchive(self, project_id):
        """
        Marks project as unarchived remotely.
        """
        cmd = {
            "type": "project_unarchive",
            "uuid": self.api.generate_uuid(),
            "args": {"id": project_id},
        }
        self.queue.append(cmd)

    def move(self, project_id, parent_id):
        """
        Moves project to another parent.
        """
        args = {
            "id": project_id,
            "parent_id": parent_id,
        }
        cmd = {"type": "project_move", "uuid": self.api.generate_uuid(), "args": args}
        self.queue.append(cmd)

    def reorder(self, projects):
        """
        Updates the child_order of the specified projects.
        """
        cmd = {
            "type": "project_reorder",
            "uuid": self.api.generate_uuid(),
            "args": {"projects": projects},
        }
        self.queue.append(cmd)

    def share(self, project_id, email):
        """
        Shares a project with a user.
        """
        cmd = {
            "type": "share_project",
            "temp_id": self.api.generate_uuid(),
            "uuid": self.api.generate_uuid(),
            "args": {"project_id": project_id, "email": email},
        }
        self.queue.append(cmd)

    def get_archived(self):
        """
        Returns archived projects.
        """
        params = {"token": self.token}
        return self.api._get("projects/get_archived", params=params)

    def get_data(self, project_id):
        """
        Returns a project's uncompleted items.
        """
        params = {"token": self.token, "project_id": project_id}
        return self.api._get("projects/get_data", params=params)

    def get(self, project_id):
        """
        Gets an existing project.
        """
        params = {"token": self.token, "project_id": project_id}
        obj = self.api._get("projects/get", params=params)
        if obj and "error" in obj:
            return None
        data = {"projects": [], "project_notes": []}
        if obj.get("project"):
            data["projects"].append(obj.get("project"))
        if obj.get("notes"):
            data["project_notes"] += obj.get("notes")
        self.api._update_state(data)
        return obj
