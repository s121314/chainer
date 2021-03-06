"""Context management on ideep.

Very thin wrapper to exploit the speed of IA (Intel Architecture)
computation. Following modules and classes defined in ideep are imported
to :mod:`chainer.ia` module for convenience (refer to this table
when reading chainer's source cods).

============================ =================================
 imported name                original name
============================ =================================
 ``chainer.ideep4py``         :mod:`ideep4py`
 ``chainer.ia.mdarray``       :class:`ideep4py.mdarray`
 ``chainer.ia.{operation}``   :class:`ideep4py.{opertaion}`
============================ =================================

"""

import contextlib
import os

import numpy

import chainer
from chainer.configuration import config


available = False
ideep_enabled = False

try:
    import ideep4py  # NOQA
    from ideep4py import mdarray  # NOQA
    from ideep4py import mdarrayVector  # NOQA

    from ideep4py import array  # NOQA

    from ideep4py import intVector  # NOQA

    from ideep4py import batchNormalization  # NOQA
    from ideep4py import concat  # NOQA
    from ideep4py import convolution2D  # NOQA
    from ideep4py import convolution2DParam  # NOQA
    from ideep4py import dropout  # NOQA
    from ideep4py import linear  # NOQA
    from ideep4py import localResponseNormalization  # NOQA
    from ideep4py import localResponseNormalizationParam  # NOQA
    from ideep4py import pooling2D  # NOQA
    from ideep4py import pooling2DParam  # NOQA
    from ideep4py import relu  # NOQA

    from ideep4py import basic_acc_sum as acc_add  # NOQA

    from ideep4py import cosim  # NOQA
    available = True
except Exception as ex:
    class mdarray(object):
        pass

if available:
    _ideep_disabled_by_user = int(os.environ.get('CHAINER_IDEEP', '1')) == 0
    ideep_enabled = not _ideep_disabled_by_user


# ------------------------------------------------------------------------------
# ideep configuration
# ------------------------------------------------------------------------------
_SHOULD_USE_IDEEP = {
    '==always': {'always': True, 'auto': False, 'never': False},
    '>=auto': {'always': True, 'auto': True, 'never': False},
}


_ideep_version = 0


def should_use_ideep(level, lowest_version=0):
    """Determines if we should use ideep.

    This function checks ``chainer.config.use_ideep``,
    ``chainer.ia.ideep_enabled``. Note that ``ideep_enabled``
    flag is fixed at loading of :mod: `chainer` module.

    Args:
        level (str): ideep use level. It must be either ``'==always'`` or
            ``'>=auto'``. ``'==always'`` indicates that the ``use_ideep``
            config must be ``'always'`` to use ideep.
        lowest_version (int): Required lowest ideep version. It must be
            non-negative.

    Returns:
        bool: ``True`` if the caller should use ideep

    """
    if not ideep_enabled:
        return False

    if _ideep_version < lowest_version:
        return False

    if level not in _SHOULD_USE_IDEEP:
        raise ValueError('invalid ideep use level: %s '
                         '(must be either of "==always" or ">=auto")' %
                         repr(level))
    flags = _SHOULD_USE_IDEEP[level]

    use_ideep = config.use_ideep
    if use_ideep not in flags:
        raise ValueError('invalid use_ideep configuration: %s '
                         '(must be either of "always", "auto", or "never")' %
                         repr(use_ideep))
    return flags[use_ideep]


def check_ideep_enabled():
    """Check ``ideep_enabled``

    """
    return ideep_enabled


@contextlib.contextmanager
def disable():
    """Disable ideep optimization at Chainer runtime.

    """
    global ideep_enabled
    old = ideep_enabled
    ideep_enabled = False
    try:
        yield
    finally:
        ideep_enabled = old


def all_ready(inputs, supported_ndim=(2, 4)):
    """Check inputs and configuration supported for ideep optimization.

    The function checks :func:`chainer.ia.should_use_ideep`, ``inputs``
        info and ``supported_ndim``.

    Args:
        inputs (numpy.ndarray, cupy.ndarray, ideep.mdarray):
            ``inputs`` to be checked including array type, dimension
            and data type.
        supported_ndim: A tuple of ndim. ideep supports array dimension
            in either 2 or 4 only.

    Returns:
        bool: ``True`` if all conditions meet.

    """
    if not ideep_enabled:
        return False

    _inputs = [x.data if isinstance(x, chainer.variable.Variable)
               else x for x in inputs]

    if ideep4py.check_ndim(_inputs, supported_ndim) is False:
        return False
    elif isinstance(_inputs[0], mdarray):
        return True
    else:
        return ideep4py.check_type(_inputs) and \
            should_use_ideep('>=auto')


def get_array_module(x):
    if ideep_enabled:
        return ideep4py.get_array_module(x)
    else:
        return numpy
