#
# Copyright (c) 2024 Dynatrace LLC. All rights reserved.
#
# This software and associated documentation files (the "Software")
# are being made available by Dynatrace LLC for the sole purpose of
# illustrating the implementation of certain algorithms which have
# been published by Dynatrace LLC. Permission is hereby granted,
# free of charge, to any person obtaining a copy of the Software,
# to view and use the Software for internal, non-production,
# non-commercial purposes only – the Software may not be used to
# process live data or distributed, sublicensed, modified and/or
# sold either alone or as part of or in combination with any other
# software.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
from mpmath import mp
from collections import namedtuple
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize
import numpy

mp.dps = 50

Result = namedtuple("Result", ["q", "d", "b", "t", "mvp"])


def expm1divx(x):
    if x == 0.0:
        return mp.mpf("1")
    else:
        return mp.expm1(x) / x


def calculate_fisher_information(d, b):
    if b > 1:
        return mp.zeta(2.0, 1.0 + mp.power(b, -d) / (b - 1.0)) / mp.log(b)
    else:
        return mp.mpf("1")


def entropy_integrand(d, b, z):
    assert b > 1
    p = mp.power(b, -d) / (b - 1)
    return mp.power(z, p) * ((1 - z) * mp.log1p(-z) / (z * mp.log(z)))


def calculate_entropy(d, b):
    if b > 1:
        p = mp.power(b, -d) / (b - 1)
        i = mp.quad(lambda z: entropy_integrand(d=d, b=b, z=z), [0, 1])
        return (mp.mpf("1.0") / (1 + p) + i) / (mp.log(2) * mp.log(b))
    else:
        return mp.mpf("inf")


def mvp_ml_compressed_func(d, b):
    return float(calculate_entropy(d=d, b=b) / calculate_fisher_information(d=d, b=b))


def mvp_martingale_compressed_func(d, b):
    return float(
        calculate_entropy(d=d, b=b)
        * (b - 1.0 + mp.power(b, -d))
        / (2.0 * expm1divx(mp.log(b)))
    )


def mvp_ml_compressed(d=None, b=None):
    d_max = 100
    b_min = 1
    b_max = 5

    result = None
    if d is not None and b is not None:
        mvp = mvp_ml_compressed_func(d=d, b=b)
        result = Result(None, d, b, None, mvp)
    elif d is None:
        for d in range(0, d_max + 1):
            r = mvp_ml_compressed(d, b)
            if result is None or r.mvp < result.mvp:
                result = r
    elif d is not None and b is None:
        r = minimize_scalar(
            lambda x: mvp_ml_compressed_func(d=d, b=x),
            bounds=(b_min, b_max),
            method="Bounded",
            options={"xatol": 1e-20},
        )
        assert r.success
        result = Result(None, d, r.x, None, r.fun)

    assert result is not None
    assert result.mvp > 0
    return result


def mvp_martingale_compressed(d=None, b=None):
    d_max = 100
    b_min = 1
    b_max = 5

    result = None
    if d is not None and b is not None:
        mvp = mvp_martingale_compressed_func(d=d, b=b)
        result = Result(None, d, b, None, mvp)
    elif d is None:
        for d in range(0, d_max + 1):
            r = mvp_martingale_compressed(d, b)
            if result is None or r.mvp < result.mvp:
                result = r
    elif d is not None and b is None:
        r = minimize_scalar(
            lambda x: mvp_martingale_compressed_func(d=d, b=x),
            bounds=(b_min, b_max),
            method="Bounded",
            options={"xatol": 1e-20},
        )
        assert r.success
        result = Result(None, d, r.x, None, r.fun)

    assert result is not None
    assert result.mvp > 0
    return result


def omega0(b, t):
    result = mp.power(mp.power(b, 3) - b + 1, -t) - mp.power(b, -3 * t)
    assert result >= 0
    return result


def omega1(b, t):
    result = mp.power(mp.power(b, 2) - b + 1, -t) - mp.power(b, -2 * t) - omega0(b, t)
    assert result >= 0
    return result


def omega2(b, t):
    result = (
        mp.power(mp.power(b, 3) - mp.power(b, 2) + 1, -t)
        - mp.power(mp.power(b, 3) - mp.power(b, 2) + b, -t)
        - omega0(b, t)
    )
    assert result >= 0
    return result


def omega3(b, t):
    result = 1 - mp.power(b, -t) - omega0(b, t) - omega1(b, t) - omega2(b, t)
    assert result >= 0
    return result


def mvp_fgra_func(required_bits, b, t):
    sum = (
        mp.power(omega0(b, t), 2) / omega0(b, 2 * t)
        + mp.power(omega1(b, t), 2) / omega1(b, 2 * t)
        + mp.power(omega2(b, t), 2) / omega2(b, 2 * t)
        + mp.power(omega3(b, t), 2) / omega3(b, 2 * t)
    )
    return float(
        required_bits
        / mp.power(t, 2)
        * (mp.gamma(2 * t) * mp.log(b) / (mp.power(mp.gamma(t), 2) * sum) - 1)
    )


def mvp_fgra(q, b, t=None):
    assert b == 2

    t_min = 1e-3
    t_max = 5
    d = 2
    required_bits = q + d
    result = None
    if t is not None:
        mvp = mvp_fgra_func(required_bits, b, t)
        result = Result(q, d, b, t, mvp)
    else:
        r = minimize_scalar(
            lambda x: mvp_fgra_func(required_bits, b, x),
            bounds=(t_min, t_max),
            method="Bounded",
            options={"xatol": 1e-20},
        )
        assert r.success
        result = Result(q, d, b, r.x, r.fun)

    assert result is not None
    assert result.mvp > 0
    return result


def calculate_contribution_coefficients_fgra(r):
    assert r.d == 2
    b = mp.mpmathify(r.b)
    t = mp.mpmathify(r.t)

    sum = (
        mp.power(omega0(b, t), 2) / omega0(b, 2 * t)
        + mp.power(omega1(b, t), 2) / omega1(b, 2 * t)
        + mp.power(omega2(b, t), 2) / omega2(b, 2 * t)
        + mp.power(omega3(b, t), 2) / omega3(b, 2 * t)
    )

    x = numpy.array(
        [
            omega0(b, t) / omega0(b, 2 * t),
            omega1(b, t) / omega1(b, 2 * t),
            omega2(b, t) / omega2(b, 2 * t),
            omega3(b, t) / omega3(b, 2 * t),
        ]
    )

    coefficients = x * (mp.log(b) / (mp.gamma(t) * sum))
    return coefficients.astype(str)


def calculate_contribution_coefficients_gra(r):
    b = mp.mpmathify(r.b)
    t = mp.mpmathify(r.t)
    d = r.d

    size = 2**d
    x = numpy.zeros(size)
    for i in range(0, size):
        s = 1 / (mp.power(b, t) - 1)
        for j in range(1, d + 1):
            if i & (1 << (d - j)) == 0:
                s += mp.power(b, t * j)
        x[i] = s

    coefficients = x * mp.log(b) * mp.power(b - 1 + mp.power(b, -t), t) / mp.gamma(t)
    return coefficients.astype(str)


def mvp_gra_func(q, d, b, t):
    required_bits = q + d
    if t == 0:
        return required_bits
    sum = 0
    for s in range(1, d + 1):
        sum += (
            2.0
            * mp.log(b)
            * mp.power(b, -t * s)
            / mp.power(1 + (b - 1) * mp.power(b, -s) / (b - 1 + mp.power(b, -d)), 2 * t)
        )
    sum += mp.log(b)
    sum += 2 * mp.power(b, -t * d) / (t * expm1divx(t * mp.log(b)))
    sum *= mp.gamma(mp.mpmathify(2) * t) / mp.power(mp.gamma(t), 2)
    sum -= 1
    sum /= t * t
    result = sum * required_bits
    assert result > 0
    return float(result)


def mvp_gra(q, d=None, b=None, t=None):
    d_max = 100
    b_min = 1
    b_start = 2
    b_max = 5
    t_min = 1e-3
    t_start = 1
    t_max = 5

    result = None
    if d is not None and b is not None and t is not None:
        mvp = mvp_gra_func(q, d, b, t)
        result = Result(q, d, b, t, mvp)
    elif d is not None and b is not None and t is None:
        r = minimize_scalar(
            lambda x: mvp_gra_func(q, d, b, x),
            bounds=(t_min, t_max),
            method="Bounded",
            options={"xatol": 1e-20},
        )
        assert r.success
        result = Result(q, d, b, r.x, r.fun)
    elif d is not None and b is None and t is None:
        r = minimize(
            lambda x: mvp_gra_func(q, d, x[0], x[1]),
            numpy.array([b_start, t_start]),
            bounds=((b_min, b_max), (t_min, t_max)),
        )
        assert r.success
        result = Result(q, d, r.x[0], r.x[1], r.fun)
    elif d is None:
        for d in range(0, d_max + 1):
            r = mvp_gra(q, d, b, t)
            if result is None or r.mvp < result.mvp:
                result = r

    assert result is not None
    assert result.mvp > 0
    return result


def mvp_martingale_func(q, d, b):
    x = (b - 1.0 + mp.power(b, -d)) / (2.0 * expm1divx(mp.log(b)))
    required_bits = q + d
    return float(x * required_bits)


def mvp_martingale(q, d=None, b=None):
    d_max = 100
    b_min = 1
    b_max = 5

    result = None
    if d is not None and b is not None:
        mvp = mvp_martingale_func(q, d, b)
        result = Result(q, d, b, None, mvp)
    elif d is None:
        for d in range(0, d_max + 1):
            r = mvp_martingale(q, d, b)
            if result is None or r.mvp < result.mvp:
                result = r
    elif d is not None and b is None:
        r = minimize_scalar(
            lambda x: mvp_martingale_func(q, d, x),
            bounds=(b_min, b_max),
            method="Bounded",
            options={"xatol": 1e-20},
        )
        assert r.success
        result = Result(q, d, r.x, None, r.fun)

    assert result is not None
    assert result.mvp > 0
    return result


def mvp_ml_func(q, d, b):
    required_bits = q + d
    if b > 1.0:
        return float(
            required_bits * mp.log(b) / mp.zeta(2.0, 1.0 + mp.power(b, -d) / (b - 1.0))
        )
    else:
        return required_bits


def mvp_ml(q, d=None, b=None):
    d_max = 100
    b_min = 1
    b_max = 5

    result = None
    if d is not None and b is not None:
        mvp = mvp_ml_func(q, d, b)
        result = Result(q, d, b, None, mvp)
    elif d is None:
        for d in range(0, d_max + 1):
            r = mvp_ml(q, d, b)
            if result is None or r.mvp < result.mvp:
                result = r
    elif d is not None and b is None:
        r = minimize_scalar(
            lambda x: mvp_ml_func(q, d, x),
            bounds=(b_min, b_max),
            method="Bounded",
            options={"xatol": 1e-20},
        )
        assert r.success
        result = Result(q, d, r.x, None, r.fun)

    assert result is not None
    assert result.mvp > 0
    return result
