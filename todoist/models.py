from pprint import pformat


class Model(object):
    """
    Implements a generic object.
    """
    def __init__(self, data, api):
        self.temp_id = ''
        self.data = data
        self.api = api

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __repr__(self):
        formatted_dict = pformat(dict(self.data))
        classname = self.__class__.__name__
        return '%s(%s)' % (classname, formatted_dict)


class Collaborator(Model):
    """
    Implements a collaborator.
    """
    def delete(self, project_id):
        """
        Deletes a collaborator from a shared project.
        """
        self.api.collaborators.delete(project_id, self['email'])


class CollaboratorState(Model):
    """
    Implements a collaborator state.
    """
    pass


class Filter(Model):
    """
    Implements a filter.
    """
    def update(self, **kwargs):
        """
        Updates filter.
        """
        self.api.filters.update(self['id'], **kwargs)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes filter.
        """
        self.api.filters.delete(self['id'])
        self.data['is_deleted'] = 1


class Item(Model):
    """
    Implements an item.
    """
    def update(self, **kwargs):
        """
        Updates item.
        """
        self.api.items.update(self['id'], **kwargs)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes item.
        """
        self.api.items.delete([self['id']])
        self.data['is_deleted'] = 1

    def move(self, to_project):
        """
        Moves item to another project.
        """
        self.api.items.move({self['project_id']: [self['id']]}, to_project)
        self.data['project_id'] = to_project

    def close(self):
        """
        Marks item as closed
        """
        self.api.items.close(self['id'])

    def complete(self, force_history=0):
        """
        Marks item as completed.
        """
        self.api.items.complete([self['id']], force_history)
        self.data['checked'] = 1
        self.data['in_history'] = force_history

    def uncomplete(self, update_item_orders=1, restore_state=None):
        """
        Marks item as not completed.
        """
        self.api.items.uncomplete([self['id']], update_item_orders,
                                  restore_state)
        self.data['checked'] = 0
        self.data['in_history'] = 0
        if restore_state and self['id'] in restore_state:
            self.data['in_history'] = restore_state[self['id']][0]
            self.data['checked'] = restore_state[self['id']][1]
            self.data['item_order'] = restore_state[self['id']][2]
            self.data['indent'] = restore_state[self['id']][3]

    def update_date_complete(self, new_date_utc=None, date_string=None,
                             is_forward=None):
        """
        Completes a recurring task.
        """
        self.api.items.update_date_complete(self['id'], new_date_utc,
                                            date_string, is_forward)
        if new_date_utc:
            self.data['due_date_utc'] = new_date_utc
        if date_string:
            self.data['date_string'] = date_string


class Label(Model):
    """
    Implements a label.
    """
    def update(self, **kwargs):
        """
        Updates label.
        """
        self.api.labels.update(self['id'], **kwargs)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes label.
        """
        self.api.labels.delete(self['id'])
        self.data['is_deleted'] = 1


class LiveNotification(Model):
    """
    Implements a live notification.
    """
    pass


class GenericNote(Model):
    """
    Implements a note.
    """
    #: has to be defined in subclasses
    local_manager = None

    def update(self, **kwargs):
        """
        Updates note.
        """
        self.local_manager.update(self['id'], **kwargs)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes note.
        """
        self.local_manager.delete(self['id'])
        self.data['is_deleted'] = 1


class Note(GenericNote):
    """
    Implement an item note.
    """
    def __init__(self, data, api):
        GenericNote.__init__(self, data, api)
        self.local_manager = self.api.notes


class ProjectNote(GenericNote):
    """
    Implement a project note.
    """
    def __init__(self, data, api):
        GenericNote.__init__(self, data, api)
        self.local_manager = self.api.project_notes


class Project(Model):
    """
    Implements a project.
    """
    def update(self, **kwargs):
        """
        Updates project.
        """
        self.api.projects.update(self['id'], **kwargs)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes project.
        """
        self.api.projects.delete([self['id']])
        self.data['is_deleted'] = 1

    def archive(self):
        """
        Marks project as archived.
        """
        self.api.projects.archive(self['id'])
        self.data['is_archived'] = 1

    def unarchive(self):
        """
        Marks project as not archived.
        """
        self.api.projects.unarchive(self['id'])
        self.data['is_archived'] = 0

    def share(self, email, message=''):
        """
        Shares projects with a user.
        """
        self.api.projects.share(self['id'], email, message)

    def take_ownership(self):
        """
        Takes ownership of a shared project.
        """
        self.api.projects.take_ownership(self['id'])


class Reminder(Model):
    """
    Implements a reminder.
    """
    def update(self, **kwargs):
        """
        Updates reminder.
        """
        self.api.reminders.update(self['id'], **kwargs)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes reminder.
        """
        self.api.reminders.delete(self['id'])
        self.data['is_deleted'] = 1
