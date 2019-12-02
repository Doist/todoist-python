"""
Managers to get the list of archived items and sections.

Manager makers available as "items_archive" and "sections_archive" attributes of
API object.


Usage example (for items).

```python

# Create an API object
import todoist
api = todoist.TodoistAPI(...)

# Get project ID (take inbox)
project_id = api.user.get()['inbox_project']

# Initiate ItemsArchiveManager
archive = api.items_archive.for_project(project_id)

# Iterate over the list of completed items for the archive
for item in archive.items():
    print(item["date_completed"], item["content"])
```
"""

from typing import TYPE_CHECKING

from ..models import Item, Model, Section
from .generic import Manager

if TYPE_CHECKING:
    from ..api import TodoistAPI


class ArchiveManager(Manager):

    object_model = Model

    def __init__(self, api, object_type):
        # type: (TodoistAPI, str) -> None
        super(ArchiveManager, self).__init__(api=api)
        assert object_type in {"sections", "items"}
        self.api = api
        self.cursor = None
        self.has_more = True
        self.elements = []
        self.object_type = object_type

    def reset(self):
        """Reset internal cache of manager and start iteration from scratch."""
        self.has_more = True
        self.cursor = None
        self.elements[:] = []

    def next_page(self):
        """Return response for the next page of the archive."""
        resp = self.api.session.get(
            self._next_url(),
            params=self._next_query_params(),
            headers=self._request_headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def _next_url(self):
        return "{0}/sync/{1}/archive/{2}".format(
            self.api.api_endpoint, self.api.api_version, self.object_type
        )

    def _next_query_params(self):
        ret = {}
        if self.cursor:
            ret["cursor"] = self.cursor
        return ret

    def _request_headers(self):
        return {"Authorization": "Bearer {}".format(self.api.token)}

    def _iterate(self):
        for el in self.elements:
            yield el

        while True:
            if not self.has_more:
                break

            resp = self.next_page()
            objects = resp[self.object_type]

            self.elements += [self._make_object(data) for data in objects]
            self.has_more = resp["has_more"]
            self.cursor = resp.get("next_cursor")

            for obj in objects:
                yield obj

    def _make_object(self, data):
        return self.object_model(data, self.api)


class SectionsArchiveManagerMaker(object):
    def __init__(self, api):
        self.api = api

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def for_project(self, project_id):
        """Get manager to iterate over all archived sections for project."""
        return SectionsArchiveManager(api=self.api, project_id=project_id)


class SectionsArchiveManager(ArchiveManager):

    object_model = Section

    def __init__(self, api, project_id):
        super(SectionsArchiveManager, self).__init__(api, "sections")
        self.project_id = project_id

    def __repr__(self):
        return "SectionsArchiveManager(project_id={})".format(self.project_id)

    def sections(self):
        """Iterate over all archived sections."""
        for obj in self._iterate():
            yield obj

    def _next_query_params(self):
        ret = super(SectionsArchiveManager, self)._next_query_params()
        ret["project_id"] = self.project_id
        return ret


class ItemsArchiveManagerMaker(object):
    def __init__(self, api):
        self.api = api

    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

    def for_project(self, project_id):
        """Get manager to iterate over all top-level archived items for project."""
        return ItemsArchiveManager(api=self.api, project_id=project_id)

    def for_section(self, section_id):
        """Get manager to iterate over all top-level archived items for section."""
        return ItemsArchiveManager(api=self.api, section_id=section_id)

    def for_parent(self, parent_id):
        """Get manager to iterate over all archived sub-tasks for an item."""
        return ItemsArchiveManager(api=self.api, parent_id=parent_id)


class ItemsArchiveManager(ArchiveManager):

    object_model = Item

    def __init__(self, api, project_id=None, section_id=None, parent_id=None):
        super(ItemsArchiveManager, self).__init__(api, "items")
        assert sum([bool(project_id), bool(section_id), bool(parent_id)]) == 1
        self.project_id = project_id
        self.section_id = section_id
        self.parent_id = parent_id

    def __repr__(self):
        k, v = self._key_value()
        return "ItemsArchiveManager({}={})".format(k, v)

    def items(self):
        """Iterate over all archived items."""
        for obj in self._iterate():
            yield obj

    def _next_query_params(self):
        ret = super(ItemsArchiveManager, self)._next_query_params()
        k, v = self._key_value()
        ret[k] = v
        return ret

    def _key_value(self):
        if self.project_id:
            return "project_id", self.project_id
        elif self.section_id:
            return "section_id", self.section_id
        else:  # if self.parent_id:
            return "parent_id", self.parent_id
