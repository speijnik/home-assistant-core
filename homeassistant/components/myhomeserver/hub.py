"""Implementation of the MyHomeSERVER hub."""
from __future__ import annotations

import typing

import myhome.client
import myhome.object
from urllib3.exceptions import MaxRetryError


class MyHomeServerHub:
    """MyHomeSERVER hub implementation."""

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host
        self.client = myhome.client.Client(host)
        self._object_list: myhome.object.ObjectList | None = None

    @property
    def object_list(self) -> myhome.object.ObjectList:
        if not self._object_list:
            self._object_list = self.client.get_object_list()

        return self._object_list

    def update_object_list(self) -> myhome.object.ObjectList:
        self._object_list = None
        return self.object_list

    def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        try:
            self.client.login(username, password)
            return True
        except (myhome.client.LoginDenied, myhome.client.RemoteAccessDenied):
            return False

    def get_server_serial(self) -> str | None:
        """Test if we have working HTTP connectivity."""
        try:
            return self.client.get_server_serial()
        except MaxRetryError:
            return None

    def lights(self) -> typing.Iterable[myhome.object.Light]:
        lights: list[myhome.object.Light] = []
        for o in self.object_list.filter(type="light"):
            if isinstance(o, myhome.object.Light):
                lights.append(o)
        return lights

    def dimmers(self) -> typing.Iterable[myhome.object.Dimmer]:
        dimmers: list[myhome.object.Dimmer] = []
        for o in self.object_list.filter(type="dimmer"):
            if isinstance(o, myhome.object.Dimmer):
                dimmers.append(o)
        return dimmers
