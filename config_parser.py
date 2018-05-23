# -*- coding: utf-8 -*-

from annotation_tools.utils.yaml_util import LoadYAML
from annotation_tools.utils.common_util import Update
import annotation_tools
import os


class ConfigParser(object):
    def __init__(self):
        self.LoadDefaultConfig()

    def LoadDefaultConfig(self, config=None):
        if config is None:
            config = os.path.join(annotation_tools.root_path(),
                                  "./config/default.yaml")
        self.cfg = LoadYAML(config)

    def LoadConfig(self, config):
        cfg = LoadYAML(config)
        self.cfg = Update(self.cfg, cfg)

    def GetConfig(self):
        return self.cfg

    def GetDatasetConfig(self):
        return self.cfg["dataset"]

    def GetDisplayerConfig(self):
        return self.cfg["displayer"]
