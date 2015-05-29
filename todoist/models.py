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
        cmd = {
            'type': 'filter_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.api.queue.append(cmd)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes filter, and appends the equivalent request to the queue.
        """
        cmd = {
            'type': 'filter_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': self['id'],
            },
        }
        self.api.queue.append(cmd)
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
        cmd = {
            'type': 'item_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.api.queue.append(cmd)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes item, and appends the equivalent request to the queue.
        """
        cmd = {
            'type': 'item_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'ids': [self['id']],
            },
        }
        self.api.queue.append(cmd)
        self.api.state['Items'].remove(self)

    def move(self, to_project):
        """
        Moves item to another project, and appends the equivalent request to
        the queue.
        """
        cmd = {
            'type': 'item_move',
            'uuid': self.api.generate_uuid(),
            'args': {
                'project_items': {
                    self.data['project_id']: [self['id']],
                },
                'to_project': to_project,
            },
        }
        self.api.queue.append(cmd)
        self.data['project_id'] = to_project

    def complete(self, force_history=0):
        """
        Marks item as completed, and appends the equivalent request to the
        queue.
        """
        cmd = {
            'type': 'item_complete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'project_id': self['project_id'],
                'ids': [self['id']],
                'force_history': force_history,
            },
        }
        self.api.queue.append(cmd)
        self.data['checked'] = 1
        self.data['in_history'] = force_history

    def uncomplete(self, update_item_orders=1):
        """
        Marks item as not completed, and appends the equivalent request to the
        queue.
        """
        cmd = {
            'type': 'item_uncomplete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'project_id': self['project_id'],
                'ids': [self['id']],
                'update_item_orders': update_item_orders,
            },
        }
        self.api.queue.append(cmd)
        self.data['checked'] = 0
        self.data['in_history'] = 0

    def update_date_complete(self, new_date_utc, date_string, is_forward):
        """
        Completes a recurring task, and appends the equivalent request to the
        queue.
        """
        cmd = {
            'type': 'item_update_date_complete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': self['id'],
                'new_date_utc': new_date_utc,
                'date_string': date_string,
                'is_forward': is_forward,
            },
        }
        self.api.queue.append(cmd)
        self.data['new_date_utc'] = new_date_utc
        self.data['date_string'] = date_string
        self.data['is_forward'] = is_forward


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
        cmd = {
            'type': 'label_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.api.queue.append(cmd)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes label, and appends the equivalent request to the queue.
        """
        cmd = {
            'type': 'label_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': self['id'],
            },
        }
        self.api.queue.append(cmd)
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
        cmd = {
            'type': 'note_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.api.queue.append(cmd)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes note, and appends the equivalent request to the queue.
        """
        cmd = {
            'type': 'note_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': self['id'],
            },
        }
        self.api.queue.append(cmd)
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
        cmd = {
            'type': 'project_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.api.queue.append(cmd)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes project, and appends the equivalent request to the queue.
        """
        cmd = {
            'type': 'project_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'ids': [self['id']],
            },
        }
        self.api.queue.append(cmd)
        self.api.state['Projects'].remove(self)

    def archive(self):
        """
        Marks project as archived, and appends the equivalent request to the
        queue.
        """
        cmd = {
            'type': 'project_archive',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': self['id']
            },
        }
        self.api.queue.append(cmd)
        self.data['is_archived'] = 1

    def unarchive(self):
        """
        Marks project as not archived, and appends the equivalent request to
        the queue.
        """
        cmd = {
            'type': 'project_unarchive',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': self['id']
            },
        }
        self.api.queue.append(cmd)
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
        cmd = {
            'type': 'reminder_update',
            'uuid': self.api.generate_uuid(),
            'args': args,
        }
        self.api.queue.append(cmd)
        self.data.update(kwargs)

    def delete(self):
        """
        Deletes reminder, and appends the equivalent request to the queue.
        """
        cmd = {
            'type': 'reminder_delete',
            'uuid': self.api.generate_uuid(),
            'args': {
                'id': self['id'],
            },
        }
        self.api.queue.append(cmd)
        self.api.state['Reminders'].remove(self)
