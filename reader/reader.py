from .utils import read_dat
from .utils import read_txt
from .utils import read_pic

from datetime import datetime
import os


class Session:

    device_mapping_file = 'DeviceMapping.txt'
    timestamps_file = 'timestamps.txt'
    source_dir = 'DataSource'

    file_extensions = {

        # BRS devices
        'KinectColor': 'png',
        'KinectDepth': 'png',
        'KinectInfrared': 'png',
        'KinectBodyIndex': 'png',
        'KinectBody': 'dat',
        'KinectFace': 'txt',
        'KinectFaceVertices': 'dat',
        'WebCamera': 'png',
        'InfraredCamera': 'png',
        'GazeEstimation': 'txt',
        'Gazepoint': 'txt',

        # custom devices
        'Markers': 'txt',
        'ManualPupils': 'txt'

    }

    custom_devices = {
        'GazeEstimation': 'cam_100',
        'Markers': 'cam_101',
        'ManualPupils': 'cam_102'
    }

    def __init__(self, path, filename_len=5,
                 device_mapping_file=None, source_dir=None,
                 custom_devices=None, custom_extensions=None):

        # session name
        self.name = os.path.split(path)[-1]

        # path to session
        self.path = path

        # filename length for example 00005.png == 5
        self.filename_len = filename_len

        # load database data
        self.data = read_txt(os.path.join(self.path, self.name + '.brs'))

        # load timestamps data
        self.timestamps = self.__read_timestamps()

        # add parameters if not default
        if source_dir:
            self.source_dir = source_dir
        if device_mapping_file:
            self.device_mapping_file = device_mapping_file
        if custom_devices:
            self.custom_devices.update(custom_devices)
        if custom_extensions:
            self.file_extensions.update(custom_extensions)

        # device mapping
        self.device_mapping = {}
        self.__create_device_mapping()

    def __read_timestamps(self):

        # create path to timestamps file
        timestamps_path = os.path.join(self.path, self.source_dir, self.timestamps_file)

        # create empty dict (dict needed for pandas.DataFrame
        timestamps = {}

        # open file
        with open(timestamps_path, 'r') as f:

            # iterate on lines
            for line in f.readlines():

                # split line into index and unix timestamp
                # map to int
                i, timestamp = map(int, line.strip().strip(';').split(';'))

                # write data in datetime format (divide on 1000 means ms -> s)
                timestamps[i] = datetime.fromtimestamp(timestamp / 1000)

        return timestamps

    def __create_device_mapping(self):

        # read mapping from txt file
        path_to_txt = os.path.join(self.path, self.device_mapping_file)
        self.device_mapping = self.__read_device_mapping(path_to_txt)

        # load available dirs in session
        dir_list = os.listdir(os.path.join(self.path, self.source_dir))

        # check and add custom devices
        for custom_dev, custom_dir in self.custom_devices.items():
            if custom_dir in dir_list:
                self.device_mapping[custom_dev] = custom_dir

        return self

    def remove_devices(self, *args):

        for arg in args:

            try:

                # remove device from mapping
                self.device_mapping.pop(arg)

            except KeyError:

                # if key is absent -> do nothing
                pass

        return self

    @staticmethod
    def __read_device_mapping(path_to_txt):

        # create empty dict
        device_mapping = {}

        # read file with device mapping
        with open(path_to_txt, 'r') as dev_map_file:
            for line in dev_map_file.readlines():

                # clean line and split into device directory name and device name
                device_dir, device = line.replace(';', '').replace('.', '').split()

                # add data
                device_mapping[device] = device_dir

        return device_mapping

    def read_snapshot(self, number):
        return Snapshot(number,
                        self.timestamps.get(number),
                        os.path.join(self.path, self.source_dir),
                        self.filename_len).read(self.device_mapping)

    def snapshots_iterate(self, *args, verbose=False, **kwargs):

        # add tqdm
        try:
            if not verbose:
                raise ImportError
            from tqdm import tqdm
            generator = tqdm(range(*args))
        except ImportError:
            generator = range(*args)

        # yield available snapshots
        for number in generator:
            try:
                yield self.read_snapshot(number)
            except FileNotFoundError:
                pass


class Snapshot(Session):

    read_extensions = {
        'png': read_pic,
        'dat': read_dat,
        'txt': read_txt
    }

    def __init__(self, number, timestamp, path, filename_len):

        # snapshot parameters
        self.number = number
        self.timestamp = timestamp

        # file storing parameters
        self.path = path
        self.filename_len = filename_len

    def filename(self, ext):
        return str(self.number).rjust(self.filename_len, '0') + '.' + ext

    def create_file_path(self, device_dir, ext):
        return os.path.join(self.path, device_dir, self.filename(ext))

    def read(self, device_mapping):

        # iterate on available devices
        for device, device_dir in device_mapping.items():

            # get extension
            extension = self.file_extensions[device]

            # create file path
            file_path = self.create_file_path(device_dir, extension)

            # write to attribute
            self.__setattr__(device, self.read_extensions[extension](file_path))

        return self
