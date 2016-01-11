import numpy

from chainer.functions.connection import linear
from chainer import link
import chainer.initializations as I


class Linear(link.Link):

    """Linear layer (a.k.a. fully-connected layer).

    This is a link that wraps the :func:`~chainer.functions.linear` function,
    and holds a weight matrix ``W`` and optionally a bias vector ``b`` as
    parameters.

    The weight matrix ``W`` is initialized with i.i.d. Gaussian samples, each
    of which has zero mean and deviation :math:`\sqrt{1/\\text{in_size}}`. The
    bias vector ``b`` is of size ``out_size``. Each element is initialized with
    the ``bias`` value. If ``nobias`` argument is set to True, then this link
    does not hold a bias vector.

    Args:
        in_size (int): Dimension of input vectors.
        out_size (int): Dimension of output vectors.
        wscale (float): Scaling factor of the weight matrix.
        bias (float): Initial bias value.
        nobias (bool): If True, then this function does not use the bias.
        initialW (2-D array): Initial weight value. If ``None``, then this
            function uses to initialize ``wscale``. May also be a function 
            that takes a tuple of (outpu_size, input_size) and returns a 
            matrix of the same dimensions to use for initialization
        initial_bias (1-D array): Initial bias value. If ``None``, then this
            function uses to initialize ``bias``. May also be a function
            that behaves in the same manner as initalW

    .. seealso:: :func:`~chainer.functions.linear`

    Attributes:
        W (~chainer.Variable): Weight parameter.
        b (~chainer.Variable): Bias parameter.

    """

    def __init__(self, in_size, out_size, wscale=1, bias=0, nobias=False,
                 initialW=None, initial_bias=None):
        super(Linear, self).__init__(W=(out_size, in_size))

        I.init_weight(self.W.data, initialW, scale=wscale)

        if nobias:
            self.b = None
        else:
            self.add_param('b', out_size)
            I.init_weight(self.b.data, initialW, none_default=bias)

    def __call__(self, x):
        """Applies the linear layer.

        Args:
            x (~chainer.Variable): Batch of input vectors.

        Returns:
            ~chainer.Variable: Output of the linear layer.

        """
        return linear.linear(x, self.W, self.b)
