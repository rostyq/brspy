from cv2 import imread
from json import load
from bson import loads


def read_pic(path, **kwargs):
    return imread(path, **kwargs)


def read_txt(path):
    with open(path, 'r') as f:
        return load(f)


def read_dat(path):
    with open(path, 'rb') as f:
        return loads(f.read())
