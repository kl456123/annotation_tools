from displayer import StylePickerDisplayer

from dataset import ConfigParser

from dataset import Dataset


def main():
    config_parser = ConfigParser()
    config_parser.LoadConfig("config/velo_only.yaml")

    dataset = Dataset(config_parser.GetDatasetConfig())

    displayer = StylePickerDisplayer(dataset,
                                     config_parser.GetDisplayerConfig())

    displayer.Start()


if __name__ == "__main__":
    main()
