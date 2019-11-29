# -*- coding: utf-8 -*-
from .generic import Manager


class EmailsManager(Manager):
    def get_or_create(self, obj_type, obj_id, **kwargs):
        """
        Get or create email to an object.
        """
        params = {"token": self.token, "obj_type": obj_type, "obj_id": obj_id}
        params.update(kwargs)
        return self.api._get("emails/get_or_create", params=params)

    def disable(self, obj_type, obj_id, **kwargs):
        """
        Disable email to an object.
        """
        params = {"token": self.token, "obj_type": obj_type, "obj_id": obj_id}
        params.update(kwargs)
        return self.api._get("emails/disable", params=params)
