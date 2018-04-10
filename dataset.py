
import os

class Dataset(object):
    def __init__(self,root_path,image_path="image_00/data",velo_path="velodyne_points/data"):
        self.image_path = os.path.join(root_path,image_path)
        self.velo_path = os.path.join(root_path,velo_path)
        self.root_path = root_path
        self.image_names = []
        self.velo_names = []

        # load data names
        self.LoadImage()
        self.LoadVelo()

    def LoadImage(self):
        # filename(not include path)
        for img_name in os.listdir(self.image_path):
            self.image_names.append(os.path.join(self.image_path,img_name))

    def LoadVelo(self):
        for velo_name in os.listdir(self.velo_path):
            self.velo_names.append(os.path.join(self.velo_path,velo_name))


    def GetDataNameGenerator(self):
        for img_name,velo_name in zip(self.image_names,self.velo_names):
            yield img_name,velo_name



