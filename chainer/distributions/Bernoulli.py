import chainer
from chainer.backends import cuda
from chainer import Distribution
from chainer.functions.array import broadcast
from chainer.functions.math import exponential
import numpy


class Bernoulli(Distribution):

    """Bernoulli Distribution.

    Args:
        p (:class:`~chainer.Variable` or :class:`numpy.ndarray` or \
        :class:`cupy.ndarray`): Parameter of distribution representing \
        probability that variable is 1.

    """

    def __init__(self, p):
        super(Bernoulli, self).__init__()
        if isinstance(p, chainer.Variable):
            self.p = p
        else:
            self.p = chainer.Variable(p)

    def __copy__(self):
        return self._copy_to(Bernoulli(self.p))

    @property
    def batch_shape(self):
        """Returns the shape of a sample.

        Returns:
            ~chainer.Variable: Output variable representing the shape of a
            sample.

        """
        return self.p.shape

    @property
    def entropy(self):
        """Returns entropy.

        Returns:
            ~chainer.Variable: Output variable representing entropy.

        """
        return -self.p * exponential.log(self.p) - \
            (numpy.float32(1.) - self.p) \
            * exponential.log(numpy.float32(1.) - self.p)

    @property
    def event_shape(self):
        return ()

    @property
    def _is_gpu(self):
        return isinstance(self.p.data, cuda.ndarray)

    def log_prob(self, x):
        """Returns logarithm of probability for a input variable.

        Args:
            x(:class:`~chainer.Variable` or :class:`numpy.ndarray` or \
            :class:`cupy.ndarray`): Input variable representing a random
            variable.

        Returns:
            ~chainer.Variable: Output variable representing logarithm of
            probability.

        """
        return x * exponential.log(broadcast.broadcast_to(self.p, x.shape)) \
            + (1. - x) \
            * exponential.log(1. - broadcast.broadcast_to(self.p, x.shape))

    @property
    def mean(self):
        """Returns mean value.

        Returns:
            ~chainer.Variable: Output variable representing mean value.

        """
        return self.p

    def prob(self, x):
        """Returns probability for a input variable.

        Args:
            x(:class:`~chainer.Variable` or :class:`numpy.ndarray` or \
            :class:`cupy.ndarray`): Input variable representing a random
            variable.

        Returns:
            ~chainer.Variable: Output variable representing probability.

        """
        return x * broadcast.broadcast_to(self.p, x.shape) \
            + (1 - x) * (1 - broadcast.broadcast_to(self.p, x.shape))

    def _sample_n(self, n):
        """Samples from this distribution.

        Args:
            n(`int`): Sampling size.

        Returns:
            ~chainer.Variable: Output variable representing sampled random
            variable.
        """
        if self._is_gpu:
            rand = cuda.cupy.random.uniform(size=(n,)+self.p.shape)
        else:
            rand = numpy.random.uniform(size=(n,)+self.p.shape)

        criteria = self.p.data

        print(type(criteria), criteria.shape, rand.shape, self._is_gpu)
        if self._is_gpu:
            criteria = cuda.cupy.broadcast_to(criteria, rand.shape)
        else:
            criteria = numpy.broadcast_to(criteria, rand.shape)
        return chainer.Variable((rand < criteria) * 1.0)

    @property
    def stddev(self):
        """Returns standard deviation.

        Returns:
            ~chainer.Variable: Output variable representing standard deviation.

        """
        return (self.p * (1 - self.p)) ** 0.5

    @property
    def support(self):
        """Returns support.

        Returns:
            string: Output string that means support of this distribution.

        """
        return '{0, 1}'

    @property
    def variance(self):
        """Returns variance.

        Returns:
            ~chainer.Variable: Output variable representing variance.

        """
        return (self.p * (1 - self.p))