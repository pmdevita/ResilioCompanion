import configparser
import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

logger = logging.Logger(__name__)


class ResilioAPIException(Exception):
    pass


class ResilioAPI:
    def __init__(self, host, port, username, password):
        self.base_url = "http://{}:{}".format(host, port)
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = self.get_token()
        logger.info(f"Connected to {self.get_system_info()['hostname']}")

    @classmethod
    def from_ini(cls, file_path: str | Path):
        parser = configparser.ConfigParser()
        parser.read(file_path)
        return cls(
            parser["general"]["host"],
            parser["general"]["port"],
            parser["general"]["username"],
            parser["general"]["password"],
        )

    @classmethod
    def from_env(cls):
        return cls(
            os.environ["RESILIO_HOST"],
            os.environ["RESILIO_PORT"],
            os.environ["RESILIO_USER"],
            os.environ["RESILIO_PASSWORD"],
        )

    def get(self, url, params=None):
        r = self.session.get(
            self.base_url + url, auth=(self.username, self.password), params=params
        )
        return r

    def api_get(self, command, params=None):
        full_params = {"token": self.token, "action": command}
        if params:
            full_params = {**full_params, **params}
        logger.debug("Request:", full_params)
        return self.get("/gui/", full_params)

    def get_token(self):
        r = self.get("/gui/token.html")
        return ET.fromstring(r.text).find("div").text

    def get_version(self):
        r = self.api_get("version")
        return r.json()["value"]

    def get_master_folder(self):
        r = self.api_get("getmasterfolder")
        return r.json()["value"]

    def get_system_info(self):
        r = self.api_get("getsysteminfo")
        return r.json()["value"]

    def get_sync_folders(self):
        r = self.api_get("getsyncfolders")
        return r.json()["folders"]

    def get_history(self):
        r = self.api_get("history")
        return r.json()["value"]

    def get_folder_settings(self):
        r = self.api_get("getfoldersettings")
        return r.json()["value"]

    def set_pause(self, pause: bool):
        r = self.api_get("setpause", {"value": pause, "allowed": "true"})
        if r.status_code != 200:
            raise ResilioAPIException(r.json()["error"])

    def get_folder_prefs(self, folder_id):
        r = self.api_get("folderpref", {"id": folder_id})
        return r.json()["value"]

    def set_folder_prefs(self, folder_id, data):
        r = self.api_get("setfolderpref", {"id": folder_id, **data})
        if r.status_code != 200:
            raise ResilioAPIException(r.json()["error"])

    def remove_folder(self, folder_id, delete_directory=False, from_all_devices=False):
        r = self.api_get(
            "removefolder",
            {
                "folderid": folder_id,
                "deletedirectory": delete_directory,
                "fromalldevices": from_all_devices,
            },
        )
        if r.status_code != 200:
            raise ResilioAPIException(r.json()["error"])
