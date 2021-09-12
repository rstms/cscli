#!/usr/bin/env python3


class CloudSigmaClientError(Exception):
    def __init__(self, message):
        self.message = message


class ParameterError(CloudSigmaClientError):
    pass


class ResourceNotFound(CloudSigmaClientError):
    pass
