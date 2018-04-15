
import os
from myio import *
import pickle

class Dataset(object):
    def __init__(self,
                 root_path,
                 image_path="image_00/data",
                 velo_path="velodyne_points/data",
                 log_filename="log.pkl",
                 label_filename="annotation.pkl"):
        self.image_path = os.path.join(root_path,image_path)
        self.velo_path = os.path.join(root_path,velo_path)
        self.root_path = root_path
        self.image_names = []
        self.velo_names = []

        self.pc_reader = PointCloudReader()
        self.img_reader = ImageReaderFactory().GenerateImageReader("png")

        self.data_idx  = -1
        self.current_label = []
        # load data names
        self.LoadImageNames()
        self.LoadVeloNames()
        self.num = len(self.image_names)
        self.SetLogName(log_filename)
        self.SetLabelFileName(label_filename)
        self.LoadLabel()
        self.LoadStatus()
        self.CheckFinish()

    def CheckFinish(self):
        if self.data_idx==self.num:
            print("all data are processed ,exit!")
            os.system("exit")

    def SetLogName(self,log_filename):
        self.log_filename = log_filename

    def SetLabelFileName(self,label_filename):
        self.label_filename = label_filename

    def LoadImageNames(self):
        # filename(not include path)
        image_names = os.listdir(self.image_path)
        image_names.sort(key= lambda x:int(x[:-4]))
        for img_name in image_names:
            self.image_names.append(os.path.join(self.image_path,img_name))
        # self.image_names.sort()

    def LoadVeloNames(self):
        velo_names = os.listdir(self.velo_path)
        velo_names.sort(key=lambda x:int(x[:-4]))
        for velo_name in velo_names:
            self.velo_names.append(os.path.join(self.velo_path,velo_name))
        # self.velo_names.sort(key= lambda x:int(x[:-4]))

    def GetNextDataName(self):
        self.data_idx += 1
        if self.data_idx>self.num-1:
            print("all data is processed! ")
            import sys
            sys.exit(0)
            # return None,None
        return self.image_names[self.data_idx],self.velo_names[self.data_idx]

    def GetDataNameGenerator(self):
        for img_name,velo_name in zip(self.image_names,self.velo_names):
            yield img_name,velo_name


    def LoadNext(self):
        # data_names_gen = self.GetDataNameGenerator()
        # for img_name , velo_name in data_names_gen:
        img_name,velo_name = self.GetNextDataName()

        # work finish
        # if img_name is None:
        #     return
        self.pc_reader.SetFileName(velo_name)
        self.img_reader.SetFileName(img_name)
        self.pc_reader.Update()
        self.img_reader.Update()
            # yield self.pc_reader.GetOutputPort(),self.img_reader.GetOutputPort()
    def GetCurrentInfo(self):
        info = {}
        info["data_idx"] = self.data_idx
        return info

    def LoadStatus(self):
        if not os.path.isfile(self.log_filename):
            print("log file is not exist")
            return
        with open(self.log_filename,"rb") as f:
            info = pickle.load(f)
            self.data_idx = info["data_idx"]

    def SaveStatus(self):
        f =open(self.log_filename,"wb")
        pickle.dump(self.GetCurrentInfo(),f)
        f.close()
        print("Dataset status is saved! ")


    def LoadLabel(self):
        if not os.path.isfile(self.label_filename):
            print("label is not exist")
            self.label = []
            return
        with open(self.label_filename,"rb") as f:
            self.label = pickle.load(f)

    def ClearAll(self):
        for file in [self.log_filename,self.label_filename]:
            os.remove(file)

    def SetLabel(self,info):
        self.current_label = info

    def SaveLabel(self):
        self.label +=self.current_label
        f =open(self.label_filename,"wb")
        pickle.dump(self.label,f)
        f.close()
        print("Dataset label is saved! ")

    def PrintLabel(self):
        with open(self.label_filename,"rb") as f:
            data = pickle.load(f)
        print(data)
        print("num of box:{}".format(len(data)))




