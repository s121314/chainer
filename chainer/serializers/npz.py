import numpy

from chainer import cuda
from chainer import serializer


class DictionarySerializer(serializer.Serializer):

    """Serializer for dictionary.

    This is the standard serializer in Chainer. The hierarchy of objects are
    simply mapped to a flat dictionary with keys representing the paths to
    objects in the hierarchy.

    Args:
        target (dict): The dictionary that this serializer saves the objects
            to. If target is None, then a new dictionary is created.
        path (str): The base path in the hierarchy that this serializer
            indicates.

    """
    def __init__(self, target=None, path=''):
        self.target = {} if target is None else target
        self.path = path

    def __getitem__(self, key):
        return DictionarySerializer(self.target, self.path + key + '/')

    def __call__(self, key, value):
        ret = value
        if isinstance(value, cuda.ndarray):
            value = value.get()
        arr = numpy.asarray(value)
        self.target[self.path + key] = arr
        return ret


def save_npz(filename, obj):
    """Saves an object to the file in NPZ format.

    This is a short-cut function to save only one object into an NPZ file.

    Args:
        filename (str): Target file name.
        obj: Object to be serialized. It must support serialization protocol.

    """
    s = DictionarySerializer()
    s.save(obj)
    with open(filename, 'wb') as f:
        numpy.savez(f, **s.target)


class NpzDeserializer(serializer.Deserializer):

    """Deserializer for NPZ format.

    This is the standard deserializer in Chainer. This deserializer can be used
    to read an object serialized by :func:`save_npz`.

    Args:
        npz: `npz` file opbject.
        path: The base path that the deserialization starts from.

    """
    def __init__(self, npz, path=''):
        self.npz = npz
        self.path = path

    def __getitem__(self, key):
        return NpzDeserializer(self.npz, self.path + key + '/')

    def __call__(self, key, value):
        dataset = self.npz[self.path + key]
        if isinstance(value, numpy.ndarray):
            numpy.copyto(value, dataset)
        elif isinstance(value, cuda.ndarray):
            value.set(numpy.asarray(dataset))
        else:
            value = type(value)(numpy.asarray(dataset))
        return value


def load_npz(filename, obj):
    """Loads an object from the file in NPZ format.

    This is a short-cut function to load from an `.npz` file that contains only
    one object.

    Args:
        filename (str): Name of the file to be loaded.
        obj: Object to be deserialized. It must support serialization protocol.

    """
    with numpy.load(filename) as f:
        d = NpzDeserializer(f)
        d.load(obj)
