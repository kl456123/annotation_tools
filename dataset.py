
import os
from myio import *
import pickle
import yaml
import collections

def LoadYAML(config):
    with open(config, "r") as f:
        cfg = yaml.load(f)
    return cfg

def ListFile(dir_path):
    return [f for f in os.listdir(dir_path)
     if os.path.isfile(os.path.join(dir_path, f))]

def Update(d,u):
    for k,v in u.items():
        if isinstance(v,collections.Mapping):
            d[k] = Update(d.get(k,{}),v)
        else:
            d[k] = v
    return d

class ConfigParser(object):
    def __init__(self):
        self.LoadDefaultConfig()

    def LoadDefaultConfig(self,config="./config/default.yaml"):
        self.cfg = LoadYAML(config)

    def LoadConfig(self,config):
        cfg = LoadYAML(config)
        self.cfg = Update(self.cfg,cfg)

    def GetConfig(self):
        return self.cfg

    def GetDatasetConfig(self):
        return self.cfg["dataset"]

    def GetDisplayerConfig(self):
        return self.cfg["displayer"]



class Dataset(object):
    def __init__(self,cfg):
        root_path = cfg["root_path"]
        image_path = cfg["image_path"]
        velo_path = cfg["velo_path"]
        label_path = cfg["label_path"]
        self.label_type = cfg["label_type"]
        log_filename = cfg["log_name"]

        pc_reader_cfg = cfg["pointcloud_reader"]
        img_reader_cfg = cfg["image_reader"]
        resume = cfg["resume"]

        self.image_path = os.path.join(root_path,image_path)
        self.velo_path = os.path.join(root_path,velo_path)
        self.label_path = os.path.join(root_path, label_path)

        self.InitDir()

        self.root_path = root_path
        self.image_names = []
        self.velo_names = []


        self.pc_reader = PointCloudReader(pc_reader_cfg)
        self.img_reader = ImageReaderFactory().GenerateImageReader(img_reader_cfg["type"])

        self.data_idx  = -1
        self.label_filename = None
        # load data names
        self.LoadImageNames()
        self.LoadVeloNames()
        self.num = len(self.image_names)
        self.SetLogName(log_filename)

        if resume:
            self.LoadStatus()
        self.CheckFinish()

    def InitDir(self):
        if not os.path.isdir(self.label_path):
            os.mkdir(self.label_path)


    def CheckFinish(self):
        if self.data_idx==self.num:
            print("all data are processed ,exit!")
            os.system("exit")

    def SetLogName(self,log_filename):
        self.log_filename = os.path.join(self.root_path,log_filename)

    # def SetLabelFileName(self,label_filename):
    #     self.label_filename = os.path.join(self.root_path,label_filename)

    def LoadImageNames(self):
        # filename(not include path)
        image_names = ListFile(self.image_path)
        image_names.sort(key= lambda x:int(x[:-4]))
        for img_name in image_names:
            self.image_names.append(os.path.join(self.image_path,img_name))

    def GenerateLabelName(self,data_name):
        basename = os.path.basename(data_name)
        prefix,suffix = os.path.splitext(basename)
        suffix="."+self.label_type
        return os.path.join(self.label_path,prefix+suffix)


    def LoadVeloNames(self):
        velo_names = ListFile(self.velo_path)

        velo_names.sort(key=lambda x:int(x[:-4]))
        for velo_name in velo_names:
            self.velo_names.append(os.path.join(self.velo_path,velo_name))


    def GetNextDataName(self):
        print("data idx: ", self.data_idx)
        self.data_idx += 1

        if self.data_idx>self.num-1:
            print("all data is processed! ")
            import sys
            sys.exit(0)
            # return None,None
        return self.image_names[self.data_idx],self.velo_names[self.data_idx]

    def GetPrevDataName(self):
        assert not self.data_idx==-1,print("it is the first data! ")
        self.data_idx-=1

        return self.image_names[self.data_idx],self.velo_names[self.data_idx]


    def GetDataNameGenerator(self):
        for img_name,velo_name in zip(self.image_names,self.velo_names):
            yield img_name,velo_name

    def LoadPrev(self,mode="display"):
        img_name,velo_name = self.GetPrevDataName()

        self.label_filename = self.GenerateLabelName(img_name)

        if mode=="display":
            self.LoadLabel(self.label_filename)
            self.ParseLabel()
        # work finish
        # if img_name is None:
        #     return
        self.pc_reader.SetFileName(velo_name)
        self.img_reader.SetFileName(img_name)
        self.pc_reader.Update()

        self.img_reader.Update()

    def LoadNext(self,mode="display"):
        # data_names_gen = self.GetDataNameGenerator()
        # for img_name , velo_name in data_names_gen:
        img_name,velo_name = self.GetNextDataName()


        self.label_filename = self.GenerateLabelName(img_name)

        if mode=="display":
            self.LoadLabel(self.label_filename)
            self.ParseLabel()
        # work finish
        # if img_name is None:
        #     return
        self.pc_reader.SetFileName(velo_name)
        self.img_reader.SetFileName(img_name)
        self.pc_reader.Update()

        self.img_reader.Update()

    def GetImageSize(self):
        return self.img_reader.GetOutput().GetDimensions()
            # yield self.pc_reader.GetOutputPort(),self.img_reader.GetOutputPort()
    def GetCurrentInfo(self):
        info = {}
        info["data_idx"] = self.data_idx-1
        return info

    def LoadStatus(self):
        if not os.path.isfile(self.log_filename):
            print("log file is not exist")
            return
        with open(self.log_filename,"rb") as f:
            info = pickle.load(f)
            self.data_idx = info["data_idx"]

    def SaveStatus(self):
        with open(self.log_filename,"wb") as f:
            pickle.dump(self.GetCurrentInfo(),f)
        print("Dataset status is saved! ")


    def LoadLabel(self,label_filename):
        if not os.path.isfile(label_filename):
            print("label is not exist")
            self.label = []
            return
        if self.label_type =="pkl":
            mode = "rb"
        else:
            mode = "r"
        with open(label_filename,mode) as f:
            if self.label_type=="pkl":
                self.label = self.LoadFromPKL(f)
            else:
                self.label = self.LoadFromText(f)

    def LoadFromText(self,file):
        lines = file.readlines()
        return map(lambda x: x.strip().split(), lines)

    def LoadFromPKL(self,file):
        return pickle.load(file)

    def ClearAll(self):
        for file in [self.log_filename,self.label_filename]:
            os.remove(file)

    def SetLabel(self,info):
        self.label = info

    def StorePKL(self,labels,file):
        pickle.dump(labels, file)

    def StoreText(self,labels,file):
        res = []
        for line in labels:
            tmp =""
            for item in line:
                tmp +=str(item)
                tmp+=" "
            res.append(tmp)
        file.write("\n".join(res))

    def SaveLabel(self):
        if self.label_type=="pkl":
            mode = "wb"
        else:
            mode = "w"
        with open(self.label_filename,mode) as f:
            if self.label_type=="pkl":
                self.StorePKL(self.label,f)
            else:
                self.StoreText(self.label,f)
        print("Dataset label is saved! ")

    def PrintLabel(self):
        print(self.label)
        print("num of box:{}".format(len(self.label)))

    def SetClassMap(self,cls_map):
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

    def ParseLabel(self):
        objs = []
        for l in self.label:
            o = {}
            o['type'] = l[0]
            o['truncation'] = float(l[1])
            o['occlusion'] = int(l[2])
            o['alpha'] = float(l[3])
            o['box2d'] = [float(l[4]), float(l[5]), float(l[6]), float(l[7])]
            o['h'] = float(l[8])
            o['w'] = float(l[9])
            o['l'] = float(l[10])
            o['t'] = [float(l[11]), float(l[12]), float(l[13])]
            o['yaw'] = float(l[14])
            objs.append(o)
        self.label = objs







