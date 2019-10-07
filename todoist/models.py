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
        self.api.items.delete(self['id'])
        self.data['is_deleted'] = 1

    def move(self, **kwargs):
        """
        Moves item to another parent or project.
        """
        if 'parent_id' in kwargs:
            self.api.items.move(self['id'], parent_id=kwargs.get('parent_id'))
            self.data['parent_id'] = kwargs.get('parent_id')
        elif 'project_id' in kwargs:
            self.api.items.move(self['id'], project_id=kwargs.get('project_id'))
            self.data['project_id'] = kwargs.get('project_id')
        else:
            raise TypeError('move() takes one of parent_id or project_id arguments')

    def close(self):
        """
        Marks item as closed
        """
        self.api.items.close(self['id'])

    def complete(self, date_completed=None):
        """
        Marks item as completed.
        """
        self.api.items.complete(self['id'], date_completed=date_completed)
        self.data['checked'] = 1

    def uncomplete(self):
        """
        Marks item as uncompleted.
        """
        self.api.items.uncomplete(self['id'])
        self.data['checked'] = 0

    def archive(self):
        """
        Marks item as archived.
        """
        self.api.items.archive(self['id'])
        self.data['in_history'] = 1

    def unarchive(self):
        """
        Marks item as unarchived.
        """
        self.api.items.unarchive(self['id'])
        self.data['in_history'] = 0

    def update_date_complete(self, due=None):
        """
        Completes a recurring task.
        """
        self.api.items.update_date_complete(self['id'], due=due)
        if due:
            self.data['due'] = due


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
        self.api.projects.delete(self['id'])
        self.data['is_deleted'] = 1

    def archive(self):
        """
        Marks project as archived.
        """
        self.api.projects.archive(self['id'])
        self.data['is_archived'] = 1

    def unarchive(self):
        """
        Marks project as unarchived.
        """
        self.api.projects.unarchive(self['id'])
        self.data['is_archived'] = 0

    def move(self, parent_id):
        """
        Moves item to another parent.
        """
        self.api.projects.move(self['id'], parent_id)

    def share(self, email):
        """
        Shares projects with a user.
        """
        self.api.projects.share(self['id'], email)

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
