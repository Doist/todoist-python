# -*- coding: utf-8 -*-
from .generic import Manager


class BizInvitationsManager(Manager):

    # there is no local state associated with the manager
    state_name = None

    def accept(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to accept a business invitation to
        share a project.
        """
        item = {
            'type': 'biz_accept_invitation',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(item)

    def reject(self, invitation_id, invitation_secret):
        """
        Appends a request to the queue, to reject a business invitation to
        share a project.
        """
        item = {
            'type': 'biz_reject_invitation',
            'timestamp': self.api.generate_timestamp(),
            'args': {
                'invitation_id': invitation_id,
                'invitation_secret': invitation_secret,
            },
        }
        self.queue.append(item)
