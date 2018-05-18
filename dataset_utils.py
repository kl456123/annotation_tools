# -*- coding: utf-8 -*-

def ListFile(dir_path):
    return [f for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f))]


