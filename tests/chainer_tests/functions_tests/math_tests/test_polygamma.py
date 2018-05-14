import unittest

import numpy
from scipy import special

import chainer
from chainer.backends import cuda
import chainer.functions as F
from chainer import gradient_check
from chainer import testing
from chainer.testing import attr


@testing.parameterize(*testing.product({
    'shape': [(), (3, 2)],
}))
class TestPolyGamma(unittest.TestCase):

    def setUp(self):
        self.x = \
            numpy.random.uniform(0.1, 0.9, self.shape).astype(numpy.float32)
        self.gy = numpy.random.uniform(-1, 1, self.shape).astype(numpy.float32)
        self.ggx = \
            numpy.random.uniform(-1, 1, self.shape).astype(numpy.float32)
        self.n = numpy.random.randint(5, size=self.shape).astype(numpy.int32)
        self.check_forward_options = {'atol': 1e-3, 'rtol': 1e-3}
        self.check_backward_options = {'eps': 1e-5, 'atol': 1e-2, 'rtol': 1e-2,
                                       'dtype': numpy.float64}
        self.check_double_backward_options = {'eps': 1e-5, 'atol': 1e-2,
                                              'rtol': 1e-2,
                                              'dtype': numpy.float64}

    def check_forward(self, n_data, x_data):
        x = chainer.Variable(x_data)
        n = chainer.Variable(n_data)
        y = F.polygamma(n, x)
        testing.assert_allclose(
            special.polygamma(self.n, self.x), y.data,
            **self.check_forward_options)

    def test_polygamma_forward_cpu(self):
        self.check_forward(self.n, self.x)

    @attr.gpu
    def test_polygamma_forward_gpu(self):
        self.check_forward(cuda.to_gpu(self.n), cuda.to_gpu(self.x))

    def check_backward(self, n_data, x_data, y_grad):
        gradient_check.check_backward(
            lambda x: F.polygamma(chainer.Variable(n_data), x), x_data, y_grad,
            **self.check_backward_options)

    def test_polygamma_backward_cpu(self):
        self.check_backward(self.n, self.x, self.gy)

    @attr.gpu
    def test_polygamma_backward_gpu(self):
        self.check_backward(cuda.to_gpu(self.n), cuda.to_gpu(self.x),
                            cuda.to_gpu(self.gy))

    def check_double_backward(self, n_data, x_data, y_grad, x_grad_grad):
        gradient_check.check_double_backward(
            lambda x: F.polygamma(chainer.Variable(n_data), x), x_data, y_grad,
            x_grad_grad, **self.check_double_backward_options)

    def test_polygamma_double_backward_cpu(self):
        self.check_double_backward(self.n, self.x, self.gy, self.ggx)

    @attr.gpu
    def test_polygamma_double_backward_gpu(self):
        self.check_double_backward(
            cuda.to_gpu(self.n), cuda.to_gpu(self.x), cuda.to_gpu(self.gy),
            cuda.to_gpu(self.ggx))


testing.run_module(__name__, __file__)