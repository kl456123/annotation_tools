# -*- coding: utf-8 -*-

from annotation_tools.dataset import Dataset


class KITTIDataset(Dataset):
    def ParseLabel(self):
        objs = []
        for l in self.label:
            o = {}
            if len(l) == 0:
                continue
            o['type'] = l[0]
            if self.filter_classes is not None and l[0] not in self.filter_classes:
                continue
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
