from .attributes import AttributeExport
from .attributes import MimicExport
from .attributes import JointExport
from .attributes import JointOrientationExport
from .attributes import GazeExport

import os


class BodyPartsExport:

    ExportClass = AttributeExport

    def __init__(self, name, part_names, header, snapshot_path):

        self.name = name
        self.part_names = part_names

        self.header = header
        self.snapshot_path = snapshot_path

        self.create_parts()

    def create_parts(self):

        for part_name in self.part_names:
            attr = self.ExportClass(part_name, self.header, self.snapshot_path)

            self.__setattr__(part_name, attr)

    def append_snapshot(self, snapshot):

        for part_name in self.part_names:
            self.__getattribute__(part_name).append_snapshot(snapshot)

    def write(self, path):

        path = os.path.join(path, self.name)

        # create dir
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        # write each file
        for part_name in self.part_names:
            self.__getattribute__(part_name).write(path)


class MimicsExport(BodyPartsExport):
    name = 'mimics'
    header = ['X', 'Y', 'Z']
    snapshot_path = ['KinectFaceVertices']

    ExportClass = MimicExport

    face_points_count = 1346

    def __init__(self):
        part_names = list(map(lambda i: 'm' + str(i), range(self.face_points_count)))

        super().__init__(self.name, part_names, self.header, self.snapshot_path)


class GazesExport(BodyPartsExport):
    name = 'gazes'
    header = ['X', 'Y', 'Z']
    snapshot_path = ['GazeEstimation']

    ExportClass = GazeExport  # TODO change to GazeExport

    part_names = ['faceGaze', 'gazeRight', 'gazeLeft']

    def __init__(self):
        super().__init__(self.name, self.part_names, self.header, self.snapshot_path)


class JointsExport(BodyPartsExport):

    name = 'joints'
    header = ['X', 'Y', 'Z']
    snapshot_path = ['KinectBody']

    ExportClass = JointExport

    part_names = ['SpineBase',
                  'SpineMid',
                  'Neck',
                  'Head',
                  'ShoulderLeft',
                  'ElbowLeft',
                  'WristLeft',
                  'HandLeft',
                  'ShoulderRight',
                  'ElbowRight',
                  'WristRight',
                  'HandRight',
                  'HipLeft',
                  'KneeLeft',
                  'AnkleLeft',
                  'FootLeft',
                  'HipRight',
                  'KneeRight',
                  'AnkleRight',
                  'FootRight',
                  'SpineShoulder',
                  'HandTipLeft',
                  'ThumbLeft',
                  'HandTipRight',
                  'ThumbRight']

    def __init__(self, skeleton):
        snapshot_path = self.snapshot_path[:]
        snapshot_path.append(str(skeleton))

        super().__init__(self.name, self.part_names, self.header, snapshot_path)


class JointOrientationsExport(JointsExport):

    name = 'joints_orient'
    header = ['X', 'Y', 'Z', 'W']

    ExportClass = JointOrientationExport

    def __init__(self, skeleton):
        super().__init__(skeleton)
