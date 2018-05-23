from annotation_tools.core.displayer import StylePickerDisplayer

from annotation_tools.config_parser import ConfigParser

from annotation_tools.datasets.kitti_dataset import KITTIDataset
from annotation_tools import root_path
import os


def main():
    config_parser = ConfigParser()

    config_parser.LoadConfig(
        os.path.join(root_path(), "config/example.yaml"))

    dataset = KITTIDataset(config_parser.GetDatasetConfig())

    displayer = StylePickerDisplayer(dataset,
                                     config_parser.GetDisplayerConfig())

    displayer.Start()


if __name__ == "__main__":
    main()
