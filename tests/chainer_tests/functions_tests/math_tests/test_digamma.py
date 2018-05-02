import unittest

import numpy
from scipy import special

from chainer.backends import cuda
import chainer.functions as F
from chainer import testing


def _digamma_cpu(x, dtype):
    return numpy.vectorize(special.digamma, otypes=[dtype])(x)


def _digamma_gpu(x, dtype):
    return cuda.to_gpu(_digamma_cpu(cuda.to_cpu(x), dtype))


def _digamma_expected(x, dtype):
    if cuda.get_array_module(x) is numpy:
        return _digamma_cpu(x, dtype)
    else:
        return _digamma_gpu(x, dtype)


def make_data(shape, dtype):
    x = numpy.random.uniform(0.1, 0.9, shape).astype(dtype)
    gy = numpy.random.uniform(-1., 1., shape).astype(dtype)
    ggx = numpy.random.uniform(-1., 1., shape).astype(dtype)
    return x, gy, ggx


@testing.unary_math_function_unittest(
    F.digamma,
    func_expected=_digamma_expected,
    make_data=make_data,
    forward_options={'atol': 1e-3, 'rtol': 1e-3},
    backward_options={'eps': 1e-5, 'atol': 1e-2, 'rtol': 1e-2,
                      'dtype': numpy.float64},
    double_backward_options={'eps': 1e-5, 'atol': 1e-2, 'rtol': 1e-2,
                             'dtype': numpy.float64}
)
class TestDiGamma(unittest.TestCase):
    pass


testing.run_module(__name__, __file__)