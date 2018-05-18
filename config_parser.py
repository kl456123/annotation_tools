# -*- coding: utf-8 -*-

import yaml

import collections

import os


def LoadYAML(config):
    with open(config, "r") as f:
        cfg = yaml.load(f)
    return cfg


def Update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = Update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class ConfigParser(object):
    def __init__(self):
        self.LoadDefaultConfig()

    def LoadDefaultConfig(self, config="./config/default.yaml"):
        self.cfg = LoadYAML(config)

    def LoadConfig(self, config):
        cfg = LoadYAML(config)
        self.cfg = Update(self.cfg, cfg)

    def GetConfig(self):
        return self.cfg

    def GetDatasetConfig(self):
        return self.cfg.get("dataset")

    def GetDisplayerConfig(self):
        return self.cfg.get("displayer")
