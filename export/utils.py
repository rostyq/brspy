from numpy import sin
from numpy import cos
from numpy.linalg import norm

from numpy import arcsin
from numpy import arctan2
from numpy import column_stack


def get_item(data: dict, path_list: list):
    key = path_list.pop()
#     try:
#         key = int(key)
#     except ValueError:
#         pass
    if not path_list:
        try:
            return data.__getitem__(key)
        except:
            return data.__getattribute__(key)
    else:
        try:
            return get_item(data.__getitem__(key), path_list)
        except:
            return get_item(data.__getattribute__(key), path_list)


def vecs2angles(vectors):
    """
    theta = asin(-y) -- pitch
    phi = atan2(-x, -z) -- yaw
    """
    x, y, z = vectors.T

    pitch = arcsin(-y)
    yaw = arctan2(-x, -z)

    return column_stack((yaw, pitch))


def angles2vecs(angles):
    """
    x = (-1) * cos(pitch) * sin(yaw)
    y = (-1) * sin(pitch)
    z = (-1) * cos(pitch) * cos(yaw)
    """
    yaw, pitch = angles.T

    x = (-1) * cos(pitch) * sin(yaw)
    y = (-1) * sin(pitch)
    z = (-1) * cos(pitch) * cos(yaw)

    vectors = column_stack((x, y, z))

    return vectors / norm(vectors, axis=1, keepdims=True)
