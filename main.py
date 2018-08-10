import export
import reader

from argparse import ArgumentParser
import os.path


def main():

    def is_valid_file(parser, arg):
        if not os.path.isdir(arg):
            parser.error("The session directory %s does not exist!" % arg)
        else:
            return arg

    parser = ArgumentParser(description="BRS Session Export script")
    parser.add_argument("-i", dest="sess_dirs", required=True, nargs='+',
                        help="input session directory", metavar="SESS_DIR",
                        type=lambda x: is_valid_file(parser, x))
    args = parser.parse_args()

    avoid = [
        'InfraredCamera',
        'KinectDepth',
        'KinectInfrared',
        'KinectBodyIndex',
        'KinectColor',
        # 'KinectBody',
        # 'KinectFaceVertices',
        # 'GazeEstimation',
        'WebCamera'
    ]

    for sess_dir in args.sess_dirs:
        sess = reader.Session(sess_dir)
        sess.remove_devices(*avoid)
        result_dir = os.path.join(sess_dir, 'Result')

        try:
            os.mkdir(result_dir)
        except:
            pass

        sep = ';'
        exported_timestamps_filename = 'exported_timestamps.csv'

        # faces_data = {for faceid in facesIdx}

        exported_timestamps = 'time;frame\n'

        joint_id = 5
        face_id = 0

        gazes = export.GazesExport()
        mimics = export.MimicsExport()
        joints = export.JointsExport(joint_id)
        joint_orientation = export.JointOrientationsExport(joint_id)
        face_properties = export.FacePropertiesExport(face_id)

        exports = [gazes, mimics, joints, joint_orientation, face_properties]

        for snapshot in sess.snapshots_iterate(0, 1500, verbose=True):

            exported_timestamps += str(snapshot.timestamp) + sep + str(snapshot.number) + '\n'

            for _export in exports:
                _export.append_snapshot(snapshot)

        for _export in exports:
            _export.write(result_dir)

        with open(os.path.join(result_dir, exported_timestamps_filename), 'w') as f:
            f.write(exported_timestamps)


if __name__ == '__main__':
    main()
