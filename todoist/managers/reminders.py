# -*- coding: utf-8 -*-
from .. import models
from .generic import AllMixin, GetByIdMixin, Manager, SyncMixin


class RemindersManager(Manager, AllMixin, GetByIdMixin, SyncMixin):

    state_name = "reminders"
    object_type = "reminder"

    def add(self, item_id, **kwargs):
        """
        Creates a local reminder object.
        """
        obj = models.Reminder({"item_id": item_id}, self.api)
        obj.temp_id = obj["id"] = self.api.generate_uuid()
        obj.data.update(kwargs)
        self.state[self.state_name].append(obj)
        cmd = {
            "type": "reminder_add",
            "temp_id": obj.temp_id,
            "uuid": self.api.generate_uuid(),
            "args": {key: obj.data[key] for key in obj.data if key != "id"},
        }
        self.queue.append(cmd)
        return obj

    def update(self, reminder_id, **kwargs):
        """
        Updates a reminder remotely.
        """
        args = {"id": reminder_id}
        args.update(kwargs)
        cmd = {
            "type": "reminder_update",
            "uuid": self.api.generate_uuid(),
            "args": args,
        }
        self.queue.append(cmd)

    def delete(self, reminder_id):
        """
        Deletes a reminder remotely.
        """
        cmd = {
            "type": "reminder_delete",
            "uuid": self.api.generate_uuid(),
            "args": {"id": reminder_id},
        }
        self.queue.append(cmd)

    def get(self, reminder_id):
        """
        Gets an existing reminder.
        """
        params = {"token": self.token, "reminder_id": reminder_id}
        obj = self.api._get("reminders/get", params=params)
        if obj and "error" in obj:
            return None
        data = {"reminders": []}
        if obj.get("reminder"):
            data["reminders"].append(obj.get("reminder"))
        self.api._update_state(data)
        return obj
