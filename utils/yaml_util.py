# -*- coding: utf-8 -*-
import os
import yaml
import pickle
import collections


def LoadYAML(config):
    with open(config, "r") as f:
        cfg = yaml.load(f)
    return cfg


def ListFile(dir_path):
    return [
        f for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
    ]


def Update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = Update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
