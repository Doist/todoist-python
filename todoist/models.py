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


class Filter(Model):
    """
    Implements a filter.
    """
    def update(self, **kwargs):
        """
        Updates filter, and appends the equivalent request to the queue.
        """
        args = {'id': self['id']}
        args.update(kwargs)
        item = {
            'type': 'filter_update',
            'timestamp': self.api.generate_timestamp(),
            'args': args,
        }
        self.api.queue.append(item)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes filter, and appends the equivalent request to the queue.
        """
        item = {
            'type': 'filter_delete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'id': self['id'],
            },
        }
        self.api.queue.append(item)
        self.data['is_deleted'] = 1
        self.api.state['Filters'].remove(self)


class Item(Model):
    """
    Implements an item.
    """
    def update(self, **kwargs):
        """
        Updates item, and appends the equivalent request to the queue.
        """
        args = {'id': self['id']}
        args.update(kwargs)
        item = {
            'type': 'item_update',
            'timestamp': self.api.generate_timestamp(),
            'args': args,
        }
        self.api.queue.append(item)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes item, and appends the equivalent request to the queue.
        """
        item = {
            'type': 'item_delete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'ids': [self['id']],
            },
        }
        self.api.queue.append(item)
        self.api.state['Items'].remove(self)

    def move(self, to_project):
        """
        Moves item to another project, and appends the equivalent request to
        the queue.
        """
        item = {
            'type': 'item_move',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'project_items': {
                    self.data['project_id']: [self['id']],
                },
                'to_project': to_project,
            },
        }
        self.api.queue.append(item)
        self.data['project_id'] = to_project

    def complete(self, force_history=0, **kwargs):
        """
        Marks item as completed, and appends the equivalent request to the
        queue.
        """
        item = {
            'type': 'item_complete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'project_id': self['project_id'],
                'ids': [self['id']],
                'force_history': force_history,
            },
        }
        self.api.queue.append(item)
        self.data['checked'] = 1
        self.data['in_history'] = force_history

    def uncomplete(self, update_item_orders=1, **kwargs):
        """
        Marks item as not completed, and appends the equivalent request to the
        queue.
        """
        item = {
            'type': 'item_uncomplete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'project_id': self['project_id'],
                'ids': [self['id']],
                'update_item_orders': update_item_orders,
            },
        }
        self.api.queue.append(item)
        self.data['checked'] = 0
        self.data['in_history'] = 0


class Label(Model):
    """
    Implements a label.
    """
    def update(self, **kwargs):
        """
        Updates label, and appends the equivalent request to the queue.
        """
        args = {'id': self['id']}
        args.update(kwargs)
        item = {
            'type': 'label_update',
            'timestamp': self.api.generate_timestamp(),
            'args': args,
        }
        self.api.queue.append(item)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes label, and appends the equivalent request to the queue.
        """
        item = {
            'type': 'label_delete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'id': self['id'],
            },
        }
        self.api.queue.append(item)
        self.data['is_deleted'] = 1
        self.api.state['Labels'].remove(self)


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
    local_store = None

    def update(self, **kwargs):
        """
        Updates note, and appends the equivalent request to the queue.
        """
        args = {'id': self['id']}
        args.update(kwargs)
        item = {
            'type': 'note_update',
            'timestamp': self.api.generate_timestamp(),
            'args': args,
        }
        self.api.queue.append(item)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes note, and appends the equivalent request to the queue.
        """
        item = {
            'type': 'note_delete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'id': self['id'],
            },
        }
        self.api.queue.append(item)
        self.data['is_deleted'] = 1
        self.api.state[self.local_store].remove(self)


class Note(GenericNote):
    local_store = 'Notes'


class ProjectNote(GenericNote):
    local_store = 'ProjectNotes'


class Project(Model):
    """
    Implements a project.
    """
    def update(self, **kwargs):
        """
        Updates project, and appends the equivalent request to the queue.
        """
        args = {'id': self['id']}
        args.update(kwargs)
        item = {
            'type': 'project_update',
            'timestamp': self.api.generate_timestamp(),
            'args': args,
        }
        self.api.queue.append(item)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes project, and appends the equivalent request to the queue.
        """
        item = {
            'type': 'project_delete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'ids': [self['id']],
            },
        }
        self.api.queue.append(item)
        self.api.state['Projects'].remove(self)

    def archive(self):
        """
        Marks project as archived, and appends the equivalent request to the
        queue.
        """
        item = {
            'type': 'project_archive',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'id': self['id']
            },
        }
        self.api.queue.append(item)
        self.data['is_archived'] = 1

    def unarchive(self):
        """
        Marks project as not archived, and appends the equivalent request to
        the queue.
        """
        item = {
            'type': 'project_unarchive',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'id': self['id']
            },
        }
        self.api.queue.append(item)
        self.data['is_archived'] = 0


class Reminder(Model):
    """
    Implements a reminder.
    """
    def update(self, **kwargs):
        """
        Updates reminder, and appends the equivalent request to the queue.
        """
        args = {'id': self['id']}
        args.update(kwargs)
        item = {
            'type': 'reminder_update',
            'timestamp': self.api.generate_timestamp(),
            'args': args,
        }
        self.api.queue.append(item)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes reminder, and appends the equivalent request to the queue.
        """
        item = {
            'type': 'reminder_delete',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'id': self['id'],
            },
        }
        self.api.queue.append(item)
        self.data['is_deleted'] = 1
        self.api.state['Reminders'].remove(self)
