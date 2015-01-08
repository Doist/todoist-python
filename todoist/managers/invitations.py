# -*- coding: utf-8 -*-
from .generic import Manager


class InvitationsManager(Manager):

    # there is no local state associated with the manager
    state_name = None

    def accept(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to accept an invitation to share a
        project.
        """
        item = {
            'type': 'accept_invitation',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(item)

    def reject(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to reject an invitation to share a
        project.
        """
        item = {
            'type': 'reject_invitation',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(item)

    def delete(self, invitation_id):
        """
        Appends a request to the queue, to delete an invitation to share a
        project.
        """
        item = {
            'type': 'delete_invitation',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
            },
        }
        self.queue.append(item)
