# -*- coding: utf-8 -*-
from .generic import Manager, SyncMixin


class InvitationsManager(Manager, SyncMixin):

    state_name = None  # there is no local state associated
    object_type = 'share_invitation'
    resource_type = None  # there is no resource type associated

    def accept(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to accept an invitation to share a
        project.
        """
        cmd = {
            'type': 'accept_invitation',
            'uuid': self.api.generate_uuid(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(cmd)

    def reject(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to reject an invitation to share a
        project.
        """
        cmd = {
            'type': 'reject_invitation',
            'uuid': self.api.generate_uuid(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(cmd)

    def delete(self, invitation_id):
        """
        Appends a request to the queue, to delete an invitation to share a
        project.
        """
        cmd = {
            'type': 'delete_invitation',
            'uuid': self.api.generate_uuid(),
            'args': {
                'invitation_id': invitation_id,
            },
        }
        self.queue.append(cmd)
