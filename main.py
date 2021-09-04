# -*- coding:utf-8 -*-
import uuid

from ruamel import yaml


def save_config(data: dict):
    with open("config.yml", "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=yaml.RoundTripDumper)


def load_config():
    with open("config.yml", "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.Loader)


if __name__ == "__main__":
    config = load_config()
    if config["clientToken"] is None and config["auto_generate_clientToken"]:
        config["client_token"] = uuid.uuid4()
