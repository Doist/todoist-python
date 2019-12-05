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
from typing import TYPE_CHECKING, Dict, Iterator, Optional

from ..models import Item, Model, Section

if TYPE_CHECKING:
    from ..api import TodoistAPI


class ArchiveManager(object):

    object_model = Model

    def __init__(self, api, element_type):
        # type: (TodoistAPI, str) -> None
        assert element_type in {"sections", "items"}
        self.api = api
        self.element_type = element_type

    def next_page(self, cursor):
        # type: (Optional[str]) -> Dict
        """Return response for the next page of the archive."""
        resp = self.api.session.get(
            self._next_url(),
            params=self._next_query_params(cursor),
            headers=self._request_headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def _next_url(self):
        return "{0}/sync/{1}/archive/{2}".format(
            self.api.api_endpoint, self.api.api_version, self.element_type
        )

    def _next_query_params(self, cursor):
        # type: (Optional[str]) -> Dict
        ret = {}
        if cursor:
            ret["cursor"] = cursor
        return ret

    def _request_headers(self):
        return {"Authorization": "Bearer {}".format(self.api.token)}

    def _iterate(self):
        has_more = True
        cursor = None

        while True:
            if not has_more:
                break

            resp = self.next_page(cursor)

            elements = [self._make_element(data) for data in resp[self.element_type]]
            has_more = resp["has_more"]
            cursor = resp.get("next_cursor")
            for el in elements:
                yield el

    def _make_element(self, data):
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
        # type: () -> Iterator[Section]
        """Iterate over all archived sections."""
        for obj in self._iterate():
            yield obj

    def _next_query_params(self, cursor):
        ret = super(SectionsArchiveManager, self)._next_query_params(cursor)
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
        # type: () -> Iterator[Item]
        """Iterate over all archived items."""
        for obj in self._iterate():
            yield obj

    def _next_query_params(self, cursor):
        ret = super(ItemsArchiveManager, self)._next_query_params(cursor)
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
