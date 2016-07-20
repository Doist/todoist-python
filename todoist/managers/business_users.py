# -*- coding: utf-8 -*-
import json

from .generic import Manager


class BusinessUsersManager(Manager):
    def invite(self, email_list):
        """
        Send a business user invitation.
        """
        params = {'token': self.token,
                  'email_list': json.dumps(email_list)}
        return self.api._get('business/users/invite', params=params)

    def accept_invitation(self, id, secret):
        """
        Accept a business user invitation.
        """
        params = {'token': self.token,
                  'id': id,
                  'secret': secret}
        return self.api._get('business/users/accept_invitation', params=params)

    def reject_invitation(self, id, secret):
        """
        Reject a business user invitation.
        """
        params = {'token': self.token,
                  'id': id,
                  'secret': secret}
        return self.api._get('business/users/reject_invitation', params=params)
