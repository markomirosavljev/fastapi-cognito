import json
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class CognitoSettings(BaseSettings):
    """
    This class contains all mandatory fields which should get values from
    provided config file
    """
    model_config = SettingsConfigDict(extra="ignore")

    check_expiration: bool
    jwt_header_name: str
    jwt_header_prefix: str
    userpools: dict[str, dict[str, Any]]

    @classmethod
    def from_global_settings(cls, global_settings: BaseSettings):
        """
        Parse configurations from global BaseSettings object where all
        configurations could be provided.
        :param global_settings: global BaseSettings object.
        :return: mapped CognitoSettings class
        """
        return cls(**global_settings.model_dump())

    @classmethod
    def load_yaml(cls, yaml_file: str):
        """
        Open provided .yaml file and read configs from it.
        :param yaml_file: file that should contain all required configurations
        :return: mapped CognitoSettings class
        """
        with open(yaml_file, "r") as file:
            return cls(**yaml.safe_load(file))

    @classmethod
    def load_json(cls, json_file: str):
        """
        Open provided .json file and read configs from it.
        :param json_file: file that should contain all required configurations.
        :return: mapped CognitoSettings class
        """
        with open(json_file) as file:
            return cls(**json.load(file))
