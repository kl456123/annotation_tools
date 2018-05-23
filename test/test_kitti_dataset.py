# -*- coding: utf-8 -*-

from annotation_tools.datasets.kitti_dataset import KITTIDataset
from annotation_tools.config_parser import ConfigParser


def main():
    config_parser = ConfigParser('')
    dataset = KITTIDataset(config_parser.GetDatasetConfig())
    dataset.LoadNext(0)


if __name__ == '__main__':
    main()
