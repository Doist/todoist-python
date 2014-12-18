# -*- coding: utf-8 -*-


class Manager(object):

    def __init__(self, api):
        self.api = api
        # shortcuts
        self.state = self.api.state
        self.queue = self.api.queue
