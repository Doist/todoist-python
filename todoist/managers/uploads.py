# -*- coding: utf-8 -*-
from .generic import Manager


class UploadsManager(Manager):
    def add(self, filename, **kwargs):
        """
        Uploads a file.

        param filename: (str) name of file to upload
        """
        data = {"token": self.token}
        data.update(kwargs)
        files = {"file": open(filename, "rb")}
        return self.api._post("uploads/add", data=data, files=files)

    def get(self, **kwargs):
        """
        Returns all user's uploads.

        kwargs:
            limit: (int, optional) number of results (1-50)
            last_id: (int, optional) return results with id<last_id
        """
        params = {"token": self.token}
        params.update(kwargs)
        return self.api._get("uploads/get", params=params)

    def delete(self, file_url):
        """
        Deletes upload.

        param file_url: (str) uploaded file URL
        """
        params = {"token": self.token, "file_url": file_url}
        return self.api._get("uploads/delete", params=params)
