# -*- coding: utf-8 -*-
from .generic import Manager


class BizInvitationsManager(Manager):

    state_name = None  # there is no local state associated
    object_type = None  # there is no object type associated
    resource_type = None  # there is no resource type associated

    def accept(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to accept a business invitation to
        share a project.
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
        Appends a request to the queue, to reject a business invitation to
        share a project.
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
