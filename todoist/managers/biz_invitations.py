# -*- coding: utf-8 -*-
from .generic import Manager


class BizInvitationsManager(Manager):

    state_name = None  # there is no local state associated
    object_type = None  # there is no object type associated

    def accept(self, invitation_id, invitation_secret):
        """
        Accepts a business invitation to share a project.
        """
        cmd = {
            'type': 'biz_accept_invitation',
            'uuid': self.api.generate_uuid(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(cmd)

    def reject(self, invitation_id, invitation_secret):
        """
        Rejects a business invitation to share a project.
        """
        cmd = {
            'type': 'biz_reject_invitation',
            'uuid': self.api.generate_uuid(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(cmd)
