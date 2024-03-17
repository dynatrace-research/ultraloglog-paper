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
import preamble
import numpy
import math
from math import expm1, exp, log1p
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt
import mvp


def xdiv1memx(x):
    if x == 0:
        return 1
    else:
        return x / -expm1(-x)


def onemxlnonemx(x):
    if x >= 1:
        return 0
    else:
        return (1 - x) * log1p(-x)


def calculate_fisher_information_series_term(d, b, u_plus_x):
    y = pow(b, -u_plus_x)
    z = exp(-y)
    return pow(z, 1 + pow(b, -d) / (b - 1)) * y * xdiv1memx(y)


def calculate_fisher_information_series(d, b, x):
    # print(x)
    assert x >= 0 and x <= 1
    sum = calculate_fisher_information_series_term(d=d, b=b, u_plus_x=x)
    u = 0
    while True:
        u += 1
        oldsum = sum
        sum += calculate_fisher_information_series_term(d=d, b=b, u_plus_x=u + x)
        if oldsum == sum:
            break
    u = 0
    while True:
        u -= 1
        oldsum = sum
        sum += calculate_fisher_information_series_term(d=d, b=b, u_plus_x=u + x)
        if oldsum == sum:
            break
    assert not numpy.isnan(sum)
    # if (sum <= 0):
    #     print("d: " + str(d) + " b: " + str(b) + " x: " + str(x))
    #     print(sum)
    assert sum > 0
    return sum


def find_max_for_function_with_period_1(f):
    max = 0
    num_intervals = 100
    for i in range(0, num_intervals):
        result = minimize_scalar(
            lambda x: -f(x),
            bounds=(i / num_intervals, (i + 1) / num_intervals),
            method="bounded",
            options={"xatol": 1e-18},
        )
        assert result.success
        if -result.fun > max:
            max = -result.fun
    return max


def calculate_fisher_information_max_relative_error(d, b):
    approx = float(mvp.calculate_fisher_information(d=d, b=b))
    return math.sqrt(
        find_max_for_function_with_period_1(
            lambda x: pow(
                approx / calculate_fisher_information_series(d=d, b=b, x=x) - 1, 2
            )
        )
    )


def calculate_entropy_series_term(d, b, u_plus_x):
    y = pow(b, -u_plus_x)
    z = exp(-y)
    z_b = pow(z, 1 / (b - 1))
    return z_b * (1 - z * b) * (-y) / (b - 1) + pow(z, pow(b, -d) / (b - 1)) * (
        -z * y + onemxlnonemx(z)
    )


def calculate_entropy_series(d, b, x):
    assert x >= 0 and x <= 1
    sum = calculate_entropy_series_term(d=d, b=b, u_plus_x=x)
    u = 0
    while True:
        u += 1
        oldsum = sum
        sum += calculate_entropy_series_term(d=d, b=b, u_plus_x=u + x)
        if oldsum == sum:
            break
    u = 0
    while True:
        u -= 1
        oldsum = sum
        sum += calculate_entropy_series_term(d=d, b=b, u_plus_x=u + x)
        if oldsum == sum:
            break
    assert not numpy.isnan(sum)
    assert -sum > 0
    return -sum / math.log(2)


def calculate_entropy_max_relative_error(d, b):
    approx = float(mvp.calculate_entropy(d=d, b=b))
    return math.sqrt(
        find_max_for_function_with_period_1(
            lambda x: pow(approx / calculate_entropy_series(d=d, b=b, x=x) - 1, 2)
        )
    )


def plot_relative_error(ax, relative_error_function, title):
    bases = numpy.linspace(1.2, 5, 100)

    ax.set_title(title)

    ax.set_yscale("log", base=10)
    ax.set_ylim([1e-8, 1e-1])
    ax.set_xlim([1, 5])
    ax.set_yticks([1e-8, 1e-6, 1e-4, 1e-2])

    ax.set_xlabel(r"$\symBase$")

    ax.plot(
        bases,
        [relative_error_function(b=b, d=float("inf")) for b in bases],
        label=r"$\symNumExtraBits\rightarrow\infty$",
        linewidth=1,
        color="red",
        linestyle="solid",
    )
    ax.plot(
        bases,
        [relative_error_function(b=b, d=2) for b in bases],
        label=r"$\symNumExtraBits=2$",
        linewidth=1,
        color="blue",
        linestyle="dashed",
    )
    ax.plot(
        bases,
        [relative_error_function(b=b, d=0) for b in bases],
        label=r"$\symNumExtraBits=0$",
        linewidth=1,
        color="black",
        linestyle="dotted",
    )
    ax.grid(True)

    ax.legend(
        loc="lower right",
        columnspacing=1,
        labelspacing=0.2,
        borderpad=0.2,
        handletextpad=0.4,
        fancybox=False,
        framealpha=1,
    )


def print_relative_error_charts():
    fig, ax = plt.subplots(1, 2, sharex=True, sharey=True)
    fig.set_size_inches(5, 2)

    plot_relative_error(
        ax[0],
        lambda b, d: calculate_fisher_information_max_relative_error(d=d, b=b),
        "Fisher information",
    )
    plot_relative_error(
        ax[1],
        lambda b, d: calculate_entropy_max_relative_error(d=d, b=b),
        "Shannon entropy",
    )

    ax[0].set_ylabel("max. relative approx. error")

    fig.subplots_adjust(top=0.89, bottom=0.19, left=0.11, right=0.993, wspace=0.1)

    fig.savefig(
        "paper/relative_approximation_error.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


print(
    f"calculate_fisher_information_max_relative_error(d=0, b=2) = {calculate_fisher_information_max_relative_error(d=0, b=2)}"
)
print(
    f"calculate_fisher_information_max_relative_error(d=2, b=2) = {calculate_fisher_information_max_relative_error(d=2, b=2)}"
)
print(
    f"calculate_fisher_information_max_relative_error(d=inf, b=2) = {calculate_fisher_information_max_relative_error(d=float('inf'), b=2)}"
)

print(
    f"calculate_entropy_max_relative_error(d=0, b=2) = {calculate_entropy_max_relative_error(d=0, b=2)}"
)
print(
    f"calculate_entropy_max_relative_error(d=2, b=2) = {calculate_entropy_max_relative_error(d=2, b=2)}"
)
print(
    f"calculate_entropy_max_relative_error(d=inf, b=2) = {calculate_entropy_max_relative_error(d=float('inf'), b=2)}"
)

print_relative_error_charts()
