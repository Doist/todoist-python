# -*- coding: utf-8 -*-
from .. import models
from .generic import Manager, AllMixin, GetByIdMixin, SyncMixin


class ProjectsManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = 'Projects'
    object_type = 'project'
    resource_type = 'projects'

    def add(self, name, **kwargs):
        """
        Adds a project to the local state, and appends the equivalent request
        to the queue.
        """
        obj = models.Project({'name': name}, self.api)
        obj.temp_id = obj['id'] = '$' + self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        item = {
            'type': 'project_add',
            'temp_id': obj.temp_id,
            'uuid': self.api.generate_uuid(),
            'args': obj.data,
        }
        self.queue.append(item)
        return obj

    def update_orders_indents(self, ids_to_orders_indents):
        """
        Updates in the local state the orders and indents of multiple projects,
        and appends the equivalent request to the queue.
        """
        for project_id in ids_to_orders_indents.keys():
            obj = self.get_by_id(project_id)
            if obj:
                obj['item_order'] = ids_to_orders_indents[project_id][0]
                obj['indent'] = ids_to_orders_indents[project_id][1]
        item = {
            'type': 'project_update_orders_indents',
            'uuid': self.api.generate_uuid(),
            'args': {
                'ids_to_orders_indents': ids_to_orders_indents,
            },
        }
        self.queue.append(item)
