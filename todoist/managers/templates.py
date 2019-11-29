# -*- coding: utf-8 -*-
from .generic import Manager


class TemplatesManager(Manager):
    def import_into_project(self, project_id, filename, **kwargs):
        """
        Imports a template into a project.
        """
        data = {"token": self.token, "project_id": project_id}
        data.update(kwargs)
        files = {"file": open(filename, "r")}
        return self.api._post("templates/import_into_project", data=data, files=files)

    def export_as_file(self, project_id, **kwargs):
        """
        Exports a template as a file.
        """
        data = {"token": self.token, "project_id": project_id}
        data.update(kwargs)
        return self.api._post("templates/export_as_file", data=data)

    def export_as_url(self, project_id, **kwargs):
        """
        Exports a template as a URL.
        """
        data = {"token": self.token, "project_id": project_id}
        data.update(kwargs)
        return self.api._post("templates/export_as_url", data=data)
