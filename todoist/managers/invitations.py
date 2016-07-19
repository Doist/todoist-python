# -*- coding: utf-8 -*-
from .generic import Manager, SyncMixin


class InvitationsManager(Manager, SyncMixin):

    state_name = None  # there is no local state associated
    object_type = 'share_invitation'

    def accept(self, invitation_id, invitation_secret):
        """
        Accepts an invitation to share a project.
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
        Rejets an invitation to share a project.
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
        Delete an invitation to share a project.
        """
        cmd = {
            'type': 'delete_invitation',
            'uuid': self.api.generate_uuid(),
            'args': {
                'invitation_id': invitation_id,
            },
        }
        self.queue.append(cmd)
