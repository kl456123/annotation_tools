import os
from annotation_tools.core.io import PointCloudReader, ImageReaderFactory
import pickle
from abc import ABC, abstractclassmethod
from annotation_tools.utils import common_util
import annotation_tools


class Dataset(ABC):
    def __init__(self, cfg):
        root_path = os.path.join(annotation_tools.root_path(),
                                 cfg["root_path"])
        image_path = cfg["image_path"]
        velo_path = cfg["velo_path"]
        label_path = cfg["label_path"]
        self.label_type = cfg["label_type"]
        log_filename = cfg["log_name"]
        self._velo_only = cfg["velodyne_only"]
        self._num_classes = cfg["num_classes"]
        self._classes = cfg["classes"]

        pc_reader_cfg = cfg["pointcloud_reader"]
        img_reader_cfg = cfg["image_reader"]
        resume = cfg["resume"]
        self.prefix_name = cfg.get("prefix_name")
        self.filter_classes = cfg.get("filter_classes")
        self.step = cfg['step']

        self.image_path = os.path.join(root_path, image_path)
        self.velo_path = os.path.join(root_path, velo_path)
        self.label_path = os.path.join(root_path, label_path)

        self.InitDir()

        self.root_path = root_path
        self.image_names = []
        self.velo_names = []

        self.pc_reader = PointCloudReader(pc_reader_cfg)
        if self._velo_only:
            self.img_reader = None
        else:
            self.img_reader = ImageReaderFactory().GenerateImageReader(
                img_reader_cfg["type"])

        self._data_idx = 1
        # load data nLoadNextames
        if not self._velo_only:
            self.LoadImageNames()
        self.LoadVeloNames()
        self._num = len(self.velo_names)
        self.SetLogName(log_filename)

        if resume:
            self.LoadStatus()
        self.CheckDataIdxLegal()

        #########################
        # inner state and file
        #########################
        self._cur_img_name = None
        self._cur_velo_name = None
        self._label_filename = None

    @property
    def data_idx(self):
        return self._data_idx

    @property
    def num_classes(self):
        return self._num_classes

    @property
    def cur_prefix_name(self):
        return os.path.splitext(os.path.basename(self._cur_velo_name))[0]

    @property
    def label_filename(self):
        return self._label_filename

    def InitDir(self):
        if not os.path.isdir(self.label_path):
            os.mkdir(self.label_path)

    @property
    def velo_only(self):
        return self._velo_only

    # def CheckFinish(self):
    # if self.data_idx == self.num:
    # print("all data are processed ,exit!")
    # os.system("exit")

    def CheckDataIdxLegal(self, data_idx=None):
        if data_idx is None:
            data_idx = self._data_idx
        if data_idx >= 1 and data_idx <= self._num:
            return True
        return False

    def SetLogName(self, log_filename):
        self.log_filename = os.path.join(self.root_path, log_filename)

    def LoadImageNames(self):
        # filename(not include path)
        image_names = common_util.ListFile(self.image_path)
        image_names.sort()
        #  image_names.sort(key=lambda x: int(x[:-4]))
        for img_name in image_names:
            self.image_names.append(os.path.join(self.image_path, img_name))

    def GenerateLabelName(self):
        basename = os.path.basename(self._cur_velo_name)
        prefix, suffix = os.path.splitext(basename)
        suffix = "." + self.label_type
        return os.path.join(self.label_path, prefix + suffix)

    def LoadVeloNames(self):
        velo_names = common_util.ListFile(self.velo_path)
        velo_names.sort()

        for velo_name in velo_names:
            self.velo_names.append(os.path.join(self.velo_path, velo_name))

    def LoadDataNameByStep(self, step):
        self.LoadDataNameByIdx(self._data_idx + step)

    def LoadDataNameByIdx(self, idx):
        assert self.CheckDataIdxLegal(
            idx), "Data Idx:{:d} is out of range".format(self._data_idx)
        self._data_idx = idx
        if self._velo_only:
            self._cur_img_name = None
        else:
            self._cur_img_name = self.image_names[self._data_idx - 1]
        self._cur_velo_name = self.velo_names[self._data_idx - 1]

    def Load(self, step):
        self.LoadDataNameByStep(step)
        self.LoadData()

        self.LoadLabel()
        self.ParseLabel()

    def LoadNext(self, step):
        self.Load(step)

    def LoadPrev(self, step):
        self.Load(-step)

    def LoadData(self):
        self.pc_reader.SetFileName(self._cur_velo_name, self._velo_only)
        if self.img_reader:
            self.img_reader.SetFileName(self._cur_img_name)
            self.img_reader.Update()
        self.pc_reader.Update()

    def LoadLabel(self):
        self._label_filename = self.GenerateLabelName()

        if not os.path.isfile(self._label_filename):
            print("{}:label is not exist".format(self._label_filename))
            self.label = []
            return
        if self.label_type == "pkl":
            mode = "rb"
        else:
            mode = "r"
        with open(self._label_filename, mode) as f:
            if self.label_type == "pkl":
                self.label = self.LoadFromPKL(f)
            else:
                self.label = self.LoadFromText(f)

    def GetModeFromDataIdx(self):
        if (self._data_idx - 1) % self.step == 0:
            return "annotation"
        else:
            return "display"

    def GetImageSize(self):
        if self.img_reader:
            return self.img_reader.GetOutput().GetDimensions()

    def GetCurrentInfo(self):
        info = {}
        info["data_idx"] = self._data_idx
        return info

    def LoadStatus(self):
        if not os.path.isfile(self.log_filename):
            print("log file is not exist")
            return
        with open(self.log_filename, "rb") as f:
            info = pickle.load(f)
            self._data_idx = info["data_idx"]

    def SaveStatus(self):
        with open(self.log_filename, "wb") as f:
            pickle.dump(self.GetCurrentInfo(), f)
        print("Dataset status is saved! ")

    def LoadFromText(self, file):
        lines = file.readlines()

        return map(lambda x: x.strip().split(), lines)

    def LoadFromPKL(self, file):
        return pickle.load(file)

    def ClearAll(self):
        for file in [self.log_filename, self.label_filename]:
            os.remove(file)

    def SetLabel(self, info):
        self.label = info

    def StorePKL(self, labels, file):
        pickle.dump(labels, file)

    def StoreText(self, labels, file):
        res = []
        for line in labels:
            tmp = ""
            for item in line:
                tmp += str(item)
                tmp += " "
            res.append(tmp)
        file.write("\n".join(res))

    def SaveLabel(self):
        if self.label_type == "pkl":
            mode = "wb"
        else:
            mode = "w"
        with open(self.label_filename, mode) as f:
            if self.label_type == "pkl":
                self.StorePKL(self.label, f)
            else:
                self.StoreText(self.label, f)
        print("Dataset label is saved! ")

    def PrintLabel(self):
        print(self.label)
        print("num of box:{}".format(len(self.label)))

    def SetClassMap(self, cls_map):
        raise NotImplementedError

    def SetColsName(self):
        raise NotImplementedError

    def SetColsLens(self):
        raise NotImplementedError


# class KITTIDataset(Dataset):
#     def SetClassMap(self,cls_map):
#         self.cls_map = cls_map

# def SetColsName(self):
#     self.cols_name = ["type","truncated","occluded",
#                       "alpha","bbox","dimensions",
#                       "location","rotation_y","score"]
# def SetColsLens(self):
#     self.values = [1,1,1,1,4,3,3,1,1]


@abstractclassmethod
def ParseLabel(self):
    pass
