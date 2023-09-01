#
# Copyright (c) 2022-2023 Dynatrace LLC. All rights reserved.
#
# This software and associated documentation files (the "Software")
# are being made available by Dynatrace LLC for purposes of
# illustrating the implementation of certain algorithms which have
# been published by Dynatrace LLC. Permission is hereby granted,
# free of charge, to any person obtaining a copy of the Software,
# to view and use the Software for internal, non-productive,
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
from math import sqrt
import matplotlib.pyplot as plt
import numpy
from labellines import labelLine, labelLines
from matplotlib.ticker import MultipleLocator
import mvp


def print_result(r, coefficients_calculator=None):
    s = str(r)

    if r.q is not None:
        v = r.mvp / (r.q + r.d)
        efficiency = mvp.mvp_lower_bound_func(r.q, r.d, r.b) / r.mvp

        s += ", v = " + str(v)
        s += ", efficiency = " + str(efficiency)
    if coefficients_calculator is not None:
        coefficients = coefficients_calculator(r)

        for i in range(0, min(len(coefficients), 8)):
            s += ", eta" + str(i) + " = " + str(coefficients[i])

    print(s)


colors = ["C" + str(i) for i in range(0, 65)]
linestyles = ["solid"] * 66

bbox = None
outline_width = 6

marker = "x"
marker_size = 5


def make_chart_for_b_fixed(b, q):
    d_values = [0, 1, 2, 3, 4, 5, 6, 7]
    t_values = numpy.linspace(1e-3, 1.5, 1000)

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(5, 3)

    for d in d_values:
        ax.plot(
            t_values,
            [mvp.mvp_gra_eval(q, d, b, t).mvp for t in t_values],
            label="$\symNumExtraBits=" + str(d) + "$",
            color=colors[d],
            linestyle=linestyles[d],
        )

    ax.set_ylim([4.5, 8])
    ax.set_xlim([0, 1.5])
    ax.set_xlabel(r"estimation parameter $\symGRA$")
    ax.set_ylabel(r"memory-variance product")
    ax.grid()
    if b == 2:
        labelLine(ax.get_lines()[0], 0.3, bbox=bbox, outline_width=outline_width)
        labelLine(ax.get_lines()[1], 0.2, bbox=bbox, outline_width=outline_width)
        labelLine(ax.get_lines()[2], 0.1, bbox=bbox, outline_width=outline_width)
        labelLine(ax.get_lines()[3], 1.4, bbox=bbox, outline_width=outline_width)
        labelLine(ax.get_lines()[4], 1.35, bbox=bbox, outline_width=outline_width)
        labelLine(ax.get_lines()[5], 1.3, bbox=bbox, outline_width=outline_width)
        labelLine(ax.get_lines()[6], 1.25, bbox=bbox, outline_width=outline_width)
        labelLine(ax.get_lines()[7], 1.2, bbox=bbox, outline_width=outline_width)

        hll = mvp.mvp_gra_eval(6, d=0, b=2, t=1)
        hll_opt = mvp.mvp_gra_eval(6, d=0, b=2)
        ehll = mvp.mvp_gra_eval(6, d=1, b=2, t=1)
        ehll_opt = mvp.mvp_gra_eval(6, d=1, b=2)
        ull = mvp.mvp_gra_eval(6, d=2, b=2)
        offset_x = 0
        offset_y = 0.1

        ax.plot(
            [hll.t],
            [hll.mvp],
            color=colors[0],
            marker=marker,
            markersize=marker_size,
        )
        ax.text(
            hll.t + 0.01,
            hll.mvp + offset_y,
            "HLL*",
            horizontalalignment="center",
        )

        ax.plot(
            [hll_opt.t],
            [hll_opt.mvp],
            color=colors[0],
            marker=marker,
            markersize=marker_size,
        )
        ax.text(
            hll_opt.t - 0.01,
            hll_opt.mvp + offset_y,
            r"HLL",
            horizontalalignment="center",
        )

        ax.plot(
            [ehll.t],
            [ehll.mvp],
            color=colors[1],
            marker=marker,
            markersize=marker_size,
        )
        ax.text(
            ehll.t + 0.02,
            ehll.mvp + offset_y,
            "EHLL*",
            horizontalalignment="center",
        )

        ax.plot(
            [ehll_opt.t],
            [ehll_opt.mvp],
            color=colors[1],
            marker=marker,
            markersize=marker_size,
        )
        ax.text(
            ehll_opt.t - 0.02,
            ehll_opt.mvp + offset_y,
            r"EHLL",
            horizontalalignment="center",
        )

        ax.plot(
            [ull.t],
            [ull.mvp],
            color=colors[2],
            marker=marker,
            markersize=marker_size,
        )
        ax.text(ull.t, ull.mvp + offset_y, "ULL", horizontalalignment="center")

        ax.text(
            0.975,
            0.045,
            "$\symBitsForMax=" + str(q) + r"$" + ", " + "$\symBase=" + str(b) + "$",
            transform=ax.transAxes,
            verticalalignment="bottom",
            horizontalalignment="right",
            bbox=dict(facecolor="wheat"),
        )

    else:
        labelLines(ax.get_lines(), bbox=bbox, outline_width=outline_width)

    fig.subplots_adjust(top=0.98, bottom=0.14, left=0.092, right=0.99)

    fig.savefig(
        "paper/mvp_gra(q=" + str(q) + ", b=" + str(b) + ").pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


def make_chart_for_optimal_tau():
    q_values = [6, 7]
    d_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    b_values = numpy.linspace(1, 4, 1000)

    fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 6)

    for ax, q, i in zip(axs, q_values, range(len(q_values))):
        for d in d_values:
            ax.plot(
                b_values,
                [mvp.mvp_gra_eval(q, d, b).mvp for b in b_values],
                label="$\symNumExtraBits=" + str(d) + "$",
                color=colors[d],
                linestyle=linestyles[d],
            )

        ax.set_ylim([4, 8])
        ax.set_xlim([1, 3])
        if i == len(q_values) - 1:
            ax.set_xlabel(r"base $\symBase$")
        ax.set_ylabel(r"memory-variance product")
        ax.grid()

        if q == 6:
            hll_opt = mvp.mvp_gra_eval(6, d=0, b=2)
            ehll_opt = mvp.mvp_gra_eval(6, d=1, b=2)
            ull = mvp.mvp_gra_eval(6, d=2, b=2)
            offset_y = 0.1

            ax.plot(
                [2],
                [hll_opt.mvp],
                color=colors[0],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(2, hll_opt.mvp + offset_y, r"HLL", horizontalalignment="center")

            ax.plot(
                [2],
                [ehll_opt.mvp],
                color=colors[1],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                2,
                ehll_opt.mvp + offset_y,
                r"EHLL",
                horizontalalignment="center",
            )

            ax.plot(
                [2],
                [ull.mvp],
                color=colors[2],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(2, ull.mvp + offset_y, "ULL", horizontalalignment="center")

            labelLine(ax.get_lines()[0], 1.5, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[1], 1.5, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[2], 2.9, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[3], 2.85, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[4], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[5], 2.65, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[6], 2.54, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[7], 2.43, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[8], 2.32, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[9], 2.22, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[10], 2.13, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[11], 2.05, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[12], 1.97, bbox=bbox, outline_width=outline_width)
        elif q == 7:
            labelLine(ax.get_lines()[0], 1.5, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[1], 1.5, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[2], 2.8, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[3], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[4], 2.64, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[5], 2.53, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[6], 2.42, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[7], 2.31, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[8], 2.21, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[9], 2.13, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[10], 2.05, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[11], 1.97, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[12], 1.90, bbox=bbox, outline_width=outline_width)
        else:
            labelLines(ax.get_lines(), bbox=bbox, outline_width=outline_width)

        ax.set_xticks(numpy.linspace(1, 3, 11))

        ax.text(
            0.97,
            0.045,
            "$\symBitsForMax=" + str(q) + r"$" + ", " + "optimal choice of $\symGRA$",
            transform=ax.transAxes,
            verticalalignment="bottom",
            horizontalalignment="right",
            bbox=dict(facecolor="wheat"),
        )

    fig.subplots_adjust(top=0.99, bottom=0.07, left=0.092, right=0.98, hspace=0.08)

    fig.savefig(
        "paper/mvp_gra_optimal.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


def make_efficiency_chart_for_gra():
    q = 6
    d_values = [0, 1, 2, 3, 4, 5, 8, 16, 32, 64]
    b_values = numpy.linspace(1, 4, 1000)

    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 3.2)

    for d in d_values:
        ax.plot(
            b_values,
            [
                mvp.mvp_lower_bound_eval(q, d, b).mvp / mvp.mvp_gra_eval(q, d, b).mvp
                for b in b_values
            ],
            label="$\symNumExtraBits=" + str(d) + "$",
            color=colors[d],
            linestyle=linestyles[d],
        )

    ax.set_ylim([0.7, 1.02])
    ax.set_xlim([1, 3])
    ax.set_xlabel(r"base $\symBase$")
    ax.set_ylabel(r"estimator efficiency")
    ax.grid()

    hll_opt = mvp.mvp_gra_eval(6, d=0, b=2)
    ehll_opt = mvp.mvp_gra_eval(6, d=1, b=2)
    ull = mvp.mvp_gra_eval(6, d=2, b=2)
    offset_y = 0.1

    ax.plot(
        [2],
        [hll_opt.mvp],
        color=colors[0],
        marker=marker,
        markersize=marker_size,
    )
    ax.text(2, hll_opt.mvp + offset_y, r"HLL", horizontalalignment="center")

    ax.plot(
        [2],
        [ehll_opt.mvp],
        color=colors[1],
        marker=marker,
        markersize=marker_size,
    )
    ax.text(
        2,
        ehll_opt.mvp + offset_y,
        r"EHLL",
        horizontalalignment="center",
    )

    ax.plot(
        [2],
        [ull.mvp],
        color=colors[2],
        marker=marker,
        markersize=marker_size,
    )
    ax.text(2, ull.mvp + offset_y, "ULL", horizontalalignment="center")

    labelLine(ax.get_lines()[0], 1.2, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[1], 1.5, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[2], 1.4, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[3], 1.35, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[4], 1.32, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[5], 1.25, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[6], 1.58, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[7], 1.32, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[8], 1.197, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[9], 1.118, bbox=bbox, outline_width=outline_width)

    ax.set_xticks(numpy.linspace(1, 3, 11))
    fig.subplots_adjust(top=0.98, bottom=0.12, left=0.105, right=0.98, hspace=0.08)

    fig.savefig(
        "paper/gra_efficiency.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


def make_efficiency_gra_vs_new():
    q = 6
    d = 2
    b = 2
    t_values = numpy.linspace(0.001, 2, 1000)

    optimal_mvp = mvp.mvp_lower_bound_eval(q, d=d, b=b).mvp

    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 2.5)

    ax.plot(
        t_values,
        [optimal_mvp / mvp.mvp_gra_eval(q, d=d, b=b, t=t).mvp for t in t_values],
        label="GRA estimator",
    )

    ax.plot(
        t_values,
        [optimal_mvp / mvp.mvp_fgra_eval(q, b=b, t=t).mvp for t in t_values],
        label="FGRA estimator (new)",
    )

    ax.set_ylim([0.5, 1.02])
    ax.set_xlim([0, 2])
    ax.set_xlabel(r"$\symGRA$")
    ax.set_ylabel(r"estimator efficiency")
    ax.grid()

    gra_opt = mvp.mvp_gra_eval(q, d=2, b=2)
    new_opt = mvp.mvp_fgra_eval(q, b=2)

    ax.plot(
        gra_opt.t,
        [optimal_mvp / gra_opt.mvp],
        color=colors[0],
        marker=marker,
        markersize=marker_size,
    )

    ax.plot(
        new_opt.t,
        [optimal_mvp / new_opt.mvp],
        color=colors[1],
        marker=marker,
        markersize=marker_size,
    )

    labelLine(ax.get_lines()[0], 1.6, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[1], 1.6, bbox=bbox, outline_width=outline_width)

    fig.subplots_adjust(top=0.98, bottom=0.16, left=0.095, right=0.975, hspace=0.08)

    fig.savefig(
        "paper/efficiency_comparison.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


def make_chart_for_lower_bound():
    q_values = [6, 7]
    d_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 18, 23, 30]
    b_values = numpy.linspace(1, 4, 1000)

    fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 6)

    for ax, q, i in zip(axs, q_values, range(len(q_values))):
        for d in d_values:
            ax.plot(
                b_values,
                [mvp.mvp_lower_bound_eval(q, d, b).mvp for b in b_values],
                label="$\symNumExtraBits=" + str(d) + "$",
                color=colors[d],
                linestyle=linestyles[d],
            )

        ax.set_ylim([3, 8])
        ax.set_xlim([1, 3])
        if i == len(q_values) - 1:
            ax.set_xlabel(r"base $\symBase$")
        ax.set_ylabel(r"memory-variance product")
        ax.yaxis.set_major_locator(MultipleLocator(0.5))
        ax.grid()

        if q == 6:
            hll = mvp.mvp_lower_bound_eval(6, d=0, b=2).mvp
            ehll = mvp.mvp_lower_bound_eval(6, d=1, b=2).mvp
            ull = mvp.mvp_lower_bound_eval(6, d=2, b=2).mvp
            offset_x = 0.05
            offset_y = 0.1

            ax.plot([2], [hll], color=colors[0], marker=marker, markersize=marker_size)
            ax.text(2 + offset_x, hll + offset_y, r"HLL", horizontalalignment="center")

            ax.plot([2], [ehll], color=colors[1], marker=marker, markersize=marker_size)
            ax.text(
                2 + offset_x, ehll + offset_y, r"EHLL", horizontalalignment="center"
            )

            ax.plot([2], [ull], color=colors[2], marker=marker, markersize=marker_size)
            ax.text(2 + offset_x, ull + offset_y, "ULL", horizontalalignment="center")

            labelLine(ax.get_lines()[0], 1.295, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[1], 1.29, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[2], 2.9, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[3], 2.85, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[4], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[5], 2.65, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[6], 2.54, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[7], 2.43, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[8], 2.325, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[9], 2.235, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[10], 2.15, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[11], 2.0, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[12], 1.86, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[13], 1.68, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[14], 1.535, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[15], 1.41, bbox=bbox, outline_width=outline_width)
        elif q == 7:
            labelLine(ax.get_lines()[0], 1.257, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[1], 1.27, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[2], 2.8, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[3], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[4], 2.64, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[5], 2.53, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[6], 2.42, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[7], 2.315, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[8], 2.225, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[9], 2.145, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[10], 2.065, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[11], 1.92, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[12], 1.81, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[13], 1.645, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[14], 1.51, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[15], 1.395, bbox=bbox, outline_width=outline_width)
        else:
            labelLines(ax.get_lines(), bbox=bbox, outline_width=outline_width)

        ax.set_xticks(numpy.linspace(1, 3, 11))

        ax.text(
            0.97,
            0.045,
            "$\symBitsForMax=" + str(q) + r"$",
            transform=ax.transAxes,
            verticalalignment="bottom",
            horizontalalignment="right",
            bbox=dict(facecolor="wheat"),
        )

    fig.subplots_adjust(top=0.99, bottom=0.07, left=0.092, right=0.98, hspace=0.08)

    fig.savefig(
        "paper/mvp_lower_bound.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


def make_chart_for_compressed():
    d_values = [0, 1, 2, 3, 4, 6, 9, 16, 24]
    b_values = numpy.linspace(1, 4, 1000)

    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 3)

    for d in d_values:
        ax.plot(
            b_values,
            [mvp.mvp_compressed_eval(d=d, b=b).mvp for b in b_values],
            label="$\symNumExtraBits=" + str(d) + "$",
            color=colors[d],
            linestyle=linestyles[d],
        )

    ax.set_ylim([1.5, 5])
    ax.set_xlim([1, 3])
    ax.set_xlabel(r"base $\symBase$")
    ax.set_ylabel(r"memory-variance product")
    ax.grid()

    hll = mvp.mvp_compressed_eval(d=0, b=2).mvp
    ehll = mvp.mvp_compressed_eval(d=1, b=2).mvp
    ull = mvp.mvp_compressed_eval(d=2, b=2).mvp
    offset_y = 0.1

    ax.plot([2], [hll], color=colors[0], marker=marker, markersize=marker_size)
    ax.text(2, hll + offset_y, r"HLL", horizontalalignment="center")

    ax.plot([2], [ehll], color=colors[1], marker=marker, markersize=marker_size)
    ax.text(2, ehll + offset_y, r"EHLL", horizontalalignment="center")

    ax.plot([2], [ull], color=colors[2], marker=marker, markersize=marker_size)
    ax.text(2, ull + offset_y, "ULL", horizontalalignment="center")

    labelLine(ax.get_lines()[0], 1.66, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[1], 1.58, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[2], 1.53, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[3], 1.48, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[4], 1.46, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[5], 1.38, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[6], 1.27, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[7], 1.19, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[8], 1.1, bbox=bbox, outline_width=outline_width)
    ax.set_xticks(numpy.linspace(1, 3, 11))

    fig.subplots_adjust(top=0.98, bottom=0.13, left=0.092, right=0.98, hspace=0.08)

    fig.savefig(
        "paper/mvp_compressed.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


def make_chart_for_compressed_martingale():
    d_values = [0, 1, 2, 3, 4, 6, 9, 16, 24]
    b_values = numpy.linspace(1, 4, 1000)

    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 3)

    for d in d_values:
        ax.plot(
            b_values,
            [mvp.mvp_compressed_martingale_eval(d=d, b=b).mvp for b in b_values],
            label="$\symNumExtraBits=" + str(d) + "$",
            color=colors[d],
            linestyle=linestyles[d],
        )

    ax.set_ylim([1.6, 2.8])
    ax.set_xlim([1, 3])
    ax.set_xlabel(r"base $\symBase$")
    ax.set_ylabel(r"memory-variance product")
    ax.grid()

    hll = mvp.mvp_compressed_martingale_eval(d=0, b=2).mvp
    ehll = mvp.mvp_compressed_martingale_eval(d=1, b=2).mvp
    ull = mvp.mvp_compressed_martingale_eval(d=2, b=2).mvp
    offset_y = 0.01
    offset_x = 0.08

    ax.plot([2], [hll], color=colors[0], marker=marker, markersize=marker_size)
    ax.text(2 + offset_x, hll + offset_y, r"HLL", horizontalalignment="center")

    ax.plot([2], [ehll], color=colors[1], marker=marker, markersize=marker_size)
    ax.text(2 + offset_x, ehll + offset_y, r"EHLL", horizontalalignment="center")

    ax.plot([2], [ull], color=colors[2], marker=marker, markersize=marker_size)
    ax.text(2 + offset_x, ull + offset_y, "ULL", horizontalalignment="center")

    labelLine(ax.get_lines()[0], 1.66, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[1], 1.58, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[2], 1.53, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[3], 1.48, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[4], 1.46, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[5], 1.38, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[6], 1.27, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[7], 1.19, bbox=bbox, outline_width=outline_width)
    labelLine(ax.get_lines()[8], 1.1, bbox=bbox, outline_width=outline_width)
    ax.set_xticks(numpy.linspace(1, 3, 11))

    fig.subplots_adjust(top=0.98, bottom=0.13, left=0.092, right=0.98, hspace=0.08)

    fig.savefig(
        "paper/mvp_compressed_martingale.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


def make_chart_for_martingale():
    q_values = [6]
    d_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 18, 23, 30]
    b_values = numpy.linspace(1, 4, 1000)

    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 3.2)

    for q, i in zip(q_values, range(len(q_values))):
        for d in d_values:
            ax.plot(
                b_values,
                [mvp.mvp_martingale_eval(q, d, b).mvp for b in b_values],
                label="$\symNumExtraBits=" + str(d) + "$",
                color=colors[d],
                linestyle=linestyles[d],
            )

        ax.set_ylim([2, 6])
        ax.set_xlim([1, 3])
        if i == len(q_values) - 1:
            ax.set_xlabel(r"base $\symBase$")
        ax.set_ylabel(r"memory-variance product")
        ax.grid()

        if q == 6:
            offset_x = 0.05
            offset_y = 0.1

            hll_mvp = mvp.mvp_martingale_eval(q, d=0, b=2)
            ehll_mvp = mvp.mvp_martingale_eval(q, d=1, b=2)
            ull_mvp = mvp.mvp_martingale_eval(q, d=2, b=2)

            ax.plot(
                [hll_mvp.b],
                [hll_mvp.mvp],
                color=colors[0],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                hll_mvp.b + offset_x,
                hll_mvp.mvp + offset_y,
                r"HLL",
                horizontalalignment="center",
            )

            ax.plot(
                [ehll_mvp.b],
                [ehll_mvp.mvp],
                color=colors[1],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                ehll_mvp.b + offset_x,
                ehll_mvp.mvp + offset_y,
                r"EHLL",
                horizontalalignment="center",
            )

            ax.plot(
                [ull_mvp.b],
                [ull_mvp.mvp],
                color=colors[2],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                ull_mvp.b + offset_x,
                ull_mvp.mvp - offset_y,
                "ULL",
                horizontalalignment="center",
                verticalalignment="top",
            )

            labelLine(ax.get_lines()[0], 1.85, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[1], 1.85, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[2], 2.9, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[3], 2.85, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[4], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[5], 2.635, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[6], 2.505, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[7], 2.365, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[8], 2.235, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[9], 2.13, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[10], 2.029, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[11], 1.885, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[12], 1.755, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[13], 1.6, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[14], 1.475, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[15], 1.365, bbox=bbox, outline_width=outline_width)
        elif q == 7:
            labelLine(ax.get_lines()[0], 2.15, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[1], 2.15, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[2], 2.8, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[3], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[4], 2.64, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[5], 2.525, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[6], 2.36, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[7], 2.23, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[8], 2.125, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[9], 2.04, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[10], 1.95, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[11], 1.88, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[12], 1.82, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[13], 1.7, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[14], 1.6, bbox=bbox, outline_width=outline_width)
            labelLine(ax.get_lines()[15], 1.5, bbox=bbox, outline_width=outline_width)
        else:
            labelLines(ax.get_lines(), bbox=bbox, outline_width=outline_width)

        ax.set_xticks(numpy.linspace(1, 3, 11))

        ax.text(
            0.97,
            0.05,
            "$\symBitsForMax=" + str(q) + r"$",
            transform=ax.transAxes,
            verticalalignment="bottom",
            horizontalalignment="right",
            bbox=dict(facecolor="wheat"),
        )

    fig.subplots_adjust(top=0.98, bottom=0.12, left=0.092, right=0.98, hspace=0.08)

    fig.savefig(
        "paper/mvp_martingale.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


print()
print("ML estimation:")
print_result(mvp.mvp_lower_bound_eval(6))
print_result(mvp.mvp_lower_bound_eval(6, b=2))
print_result(mvp.mvp_lower_bound_eval(8, b=2, d=0))
print_result(mvp.mvp_lower_bound_eval(6, d=2))
print_result(mvp.mvp_lower_bound_eval(6, d=0, b=2))
print_result(mvp.mvp_lower_bound_eval(6, d=2, b=2))
print_result(mvp.mvp_lower_bound_eval(7))
print_result(mvp.mvp_lower_bound_eval(7, d=17))
print_result(mvp.mvp_lower_bound_eval(7, b=sqrt(2.0)))
print_result(mvp.mvp_lower_bound_eval(7, d=9, b=sqrt(2.0)))
print_result(mvp.mvp_lower_bound_eval(7, d=9, b=pow(2.0, 1.0 / 3.0)))
print_result(mvp.mvp_lower_bound_eval(8, d=8, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_lower_bound_eval(8, d=16, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_lower_bound_eval(8, d=24, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_lower_bound_eval(8, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_lower_bound_eval(9, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_lower_bound_eval(9, b=sqrt(sqrt(sqrt(2.0)))))
print_result(mvp.mvp_lower_bound_eval(8))
print_result(mvp.mvp_lower_bound_eval(9))
print_result(mvp.mvp_lower_bound_eval(10))


print()
print("ML estimation (with optimal compression):")
print_result(mvp.mvp_compressed_eval(d=0, b=2))
print_result(mvp.mvp_compressed_eval(d=2, b=2))
print_result(mvp.mvp_compressed_eval(d=9, b=sqrt(2)))
print_result(mvp.mvp_compressed_eval(b=2))
print_result(mvp.mvp_compressed_eval(d=16, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_compressed_eval(d=24, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_compressed_eval(b=sqrt(sqrt(2.0))))


print()
print("GRA estimation:")
print_result(
    mvp.mvp_gra_eval(6, d=0, b=2.0, t=1), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra_eval(6, d=0, b=2.0, t=None), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra_eval(8, d=0, b=2.0, t=1), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra_eval(6, d=1, b=2.0, t=1), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra_eval(6, d=1, b=2.0, t=None), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra_eval(6, d=2, b=2.0, t=1), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra_eval(6, d=2, b=2.0, t=None), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra_eval(7, d=9, b=sqrt(2.0), t=None),
    mvp.calculate_contribution_coefficients_gra,
)
print_result(mvp.mvp_gra_eval(6, b=2.0), mvp.calculate_contribution_coefficients_gra)
print_result(mvp.mvp_gra_eval(7), mvp.calculate_contribution_coefficients_gra)
print_result(mvp.mvp_gra_eval(6), mvp.calculate_contribution_coefficients_gra)
print_result(mvp.mvp_gra_eval(5), mvp.calculate_contribution_coefficients_gra)

print_result(mvp.mvp_gra_eval(16, d=0, b=1.001))
print_result(mvp.mvp_gra_eval(16, d=0, b=1.001, t=1))


print()
print("FGRA estimation")
print_result(
    mvp.mvp_fgra_eval(q=6, b=2, t=1), mvp.calculate_contribution_coefficients_fgra
)
print_result(mvp.mvp_fgra_eval(q=6, b=2), mvp.calculate_contribution_coefficients_fgra)


print()
print("Martingle estimation:")
print_result(mvp.mvp_martingale_eval(6))
print_result(mvp.mvp_martingale_eval(6, d=1, b=2))
print_result(mvp.mvp_martingale_eval(6, d=2))
print_result(mvp.mvp_martingale_eval(6, d=0, b=2))
print_result(mvp.mvp_martingale_eval(6, d=2, b=2))
print_result(mvp.mvp_martingale_eval(7))
print_result(mvp.mvp_martingale_eval(7, d=17))
print_result(mvp.mvp_martingale_eval(7, b=sqrt(2.0)))
print_result(mvp.mvp_martingale_eval(7, d=9, b=sqrt(2.0)))


print()
print("Martingle estimation (with optimal compression):")
print_result(mvp.mvp_compressed_martingale_eval())
print_result(mvp.mvp_compressed_martingale_eval(d=1, b=2))
print_result(mvp.mvp_compressed_martingale_eval(d=2))
print_result(mvp.mvp_compressed_martingale_eval(d=0, b=2))
print_result(mvp.mvp_compressed_martingale_eval(d=2, b=2))


# make figures
make_efficiency_gra_vs_new()
make_efficiency_chart_for_gra()
make_chart_for_compressed_martingale()
make_chart_for_compressed()
make_chart_for_martingale()
make_chart_for_lower_bound()
