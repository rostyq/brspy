from pandas import DataFrame
import os
from .utils import get_item
from .utils import vecs2angles


class AttributeExport:

    id_col = 'frame'
    ext = '.csv'

    def __init__(self, name, headers, snapshot_path=None, sep=';'):
        self.name = name
        self.data = None
        self.snapshot_path = snapshot_path[::-1]
        self.sep = sep
        self.create_data_dict(headers)

    def create_data_dict(self, headers):
        self.data = {header: [] for header in headers}
        self.data[self.id_col] = []

    def append(self, number, dict_data):
        self.data[self.id_col].append(number)

        for key, value in dict_data[self.name].items():
            self.data[key].append(value)

    def get_table(self):
        return DataFrame(self.data).set_index(self.id_col)

    def append_snapshot(self, snapshot):
        self.append(snapshot.number, get_item(snapshot, self.snapshot_path[:]))

    def write(self, path):
        path = os.path.join(path, self.name)
        self.get_table().to_csv(path + self.ext, sep=self.sep)


class GazeExport(AttributeExport):

    spherical_header = ['yaw', 'pitch']

    def __init__(self, name, headers, snapshot_path, sep=';'):
        super().__init__(name=name, headers=headers, snapshot_path=snapshot_path, sep=sep)

    def get_table(self, raw=False):

        df = DataFrame(self.data).set_index(self.id_col)

        if raw:
            return df
        else:
            return DataFrame(vecs2angles(-df[['X', 'Y', 'Z']].values),
                             columns=self.spherical_header,
                             index=df.index)


class FacePropertiesExport(AttributeExport):

    name = 'FaceProperties'
    header = ['Happy',
              'Engaged',
              'WearingGlasses',
              'LeftEyeClosed',
              'RightEyeClosed',
              'MouthOpen',
              'MouthMoved',
              'LookingAway']

    snapshot_path = ['KinectFace']

    def __init__(self, person_index):
        super().__init__(self.name, self.header, self.snapshot_path)
        self.snapshot_path.insert(0, person_index)


class JointOrientationExport(AttributeExport):

    joints_key = 'JointOrientations'
    value_key = 'Orientation'

    def __init__(self, name, headers, snapshot_path, sep=';'):
        super().__init__(name, headers, snapshot_path=snapshot_path, sep=sep)
        self.snapshot_path.insert(0, self.joints_key)

    def append(self, number, dict_data):
        self.data[self.id_col].append(number)

        for key, value in dict_data[self.name][self.value_key].items():
            self.data[key].append(value)


class JointExport(JointOrientationExport):

    joints_key = 'Joints'
    value_key = 'Position'
    tracking_state_flag = 'TrackingState'

    def __init__(self, name, headers, snapshot_path, sep=';'):
        super().__init__(name, headers, snapshot_path=snapshot_path, sep=sep)
        self.data[self.tracking_state_flag] = []

    def append(self, number, dict_data):
        self.data[self.id_col].append(number)

        for key, value in dict_data[self.name][self.value_key].items():
            self.data[key].append(value)

        tracking_state = dict_data[self.name][self.tracking_state_flag]

        self.data[self.tracking_state_flag].append(tracking_state)


class MimicExport(AttributeExport):

    def __init__(self, name, headers, snapshot_path, sep=';'):
        # cut string from name
        super().__init__(name[1:], headers, snapshot_path=snapshot_path, sep=sep)
