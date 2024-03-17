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
from math import sqrt
import matplotlib.pyplot as plt
import numpy
from labellines import labelLine, labelLines
from matplotlib.ticker import MultipleLocator
import matplotlib.ticker as mtick
import mvp
import matplotlib.patheffects as PathEffects


def plot_improvement(ax, ull, hll, b_pos, y_pos):
    ax.plot(
        [hll.b, max_b],
        [hll.mvp, hll.mvp],
        color=help_line_color,
        linestyle=help_linestyle,
        linewidth=help_linewidth,
    )
    ax.plot(
        [ull.b, max_b],
        [ull.mvp, ull.mvp],
        color=help_line_color,
        linestyle=help_linestyle,
        linewidth=help_linewidth,
    )
    improvement = round(100 * (ull.mvp / hll.mvp - 1))
    txt = ax.text(
        b_pos + 0.025,
        ull.mvp + y_pos * (hll.mvp - ull.mvp),
        "$" + str(improvement) + r"\%$",
        zorder=1.6,
    )
    txt.set_path_effects([PathEffects.withStroke(linewidth=5, foreground="w")])
    ax.annotate(
        "",
        xy=(b_pos, ull.mvp),
        xytext=(b_pos, hll.mvp),
        arrowprops=dict(arrowstyle="->", linewidth=help_linewidth, shrinkB=0.5),
        zorder=1.7,
    )


def print_result(r, coefficients_calculator=None):
    s = str(r)

    if r.q is not None:
        v = r.mvp / (r.q + r.d)
        efficiency = mvp.mvp_ml_func(r.q, r.d, r.b) / r.mvp

        s += ", v = " + str(v)
        s += ", efficiency = " + str(efficiency)
    if coefficients_calculator is not None:
        coefficients = coefficients_calculator(r)

        for i in range(0, min(len(coefficients), 8)):
            s += ", eta" + str(i) + " = " + str(float(coefficients[i]))

    print(s)


colors = ["C" + str(i) for i in range(0, 65)]
linestyles = ["solid"] * 66

bbox = None
outline_width = 6

marker = "x"
marker_size = 5

max_b = 3
b_values = numpy.linspace(1, max_b, 1000)
xtick_positions = numpy.linspace(1, max_b, 11)

help_line_color = "black"
help_linestyle = "dotted"
help_linewidth = 1


def make_chart_for_ml():
    q_values = [6, 7]
    d_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 18, 23, 30]

    fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 5.2)

    hll = mvp.mvp_ml(q=6, d=0, b=2)
    ehll = mvp.mvp_ml(q=6, d=1, b=2)
    ull = mvp.mvp_ml(q=6, d=2, b=2)

    for ax, q, i in zip(axs, q_values, range(len(q_values))):
        ax.grid()

        if q == 6:
            plot_improvement(ax, ull, hll, 2.5, 0.06)

        plotted_lines = []
        for d in d_values:
            plotted_lines += ax.plot(
                b_values,
                [mvp.mvp_ml(q, d, b).mvp for b in b_values],
                label=r"$\symNumExtraBits=" + str(d) + "$",
                color=colors[d],
                linestyle=linestyles[d],
            )

        ax.set_ylim([3.3, 8])
        ax.set_xlim([1, max_b])
        if i == len(q_values) - 1:
            ax.set_xlabel(r"base $\symBase$")
        ax.set_ylabel(r"memory-variance product")
        ax.yaxis.set_major_locator(MultipleLocator(0.5))

        if q == 6:
            offset_x = 0.05
            offset_y = 0.1

            ax.plot(
                [hll.b],
                [hll.mvp],
                color=colors[0],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                hll.b + offset_x,
                hll.mvp + offset_y,
                r"HLL",
                horizontalalignment="center",
            )

            ax.plot(
                [ehll.b],
                [ehll.mvp],
                color=colors[1],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                ehll.b + offset_x,
                ehll.mvp + offset_y,
                r"EHLL",
                horizontalalignment="center",
            )

            ax.plot(
                [ull.b],
                [ull.mvp],
                color=colors[2],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                ull.b + offset_x,
                ull.mvp + offset_y,
                "ULL",
                horizontalalignment="center",
            )

            labelLine(plotted_lines[0], 1.295, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[1], 1.29, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[2], 2.9, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[3], 2.85, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[4], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[5], 2.65, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[6], 2.54, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[7], 2.43, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[8], 2.325, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[9], 2.235, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[10], 2.15, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[11], 2.0, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[12], 1.86, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[13], 1.68, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[14], 1.535, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[15], 1.41, bbox=bbox, outline_width=outline_width)
        elif q == 7:
            labelLine(plotted_lines[0], 1.257, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[1], 1.27, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[2], 2.8, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[3], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[4], 2.64, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[5], 2.53, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[6], 2.42, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[7], 2.315, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[8], 2.225, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[9], 2.145, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[10], 2.065, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[11], 1.92, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[12], 1.81, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[13], 1.645, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[14], 1.51, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[15], 1.395, bbox=bbox, outline_width=outline_width)
        else:
            labelLines(plotted_lines, bbox=bbox, outline_width=outline_width)

        hllmvp = hll.mvp
        secax = ax.secondary_yaxis(
            "right",
            functions=(
                lambda x: (x - hllmvp) / hllmvp * 100,
                lambda x: (100 + x) * hllmvp / 100,
            ),
        )
        secax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

        ax.set_xticks(xtick_positions)

        ax.text(
            0.97,
            0.045,
            r"$\symBitsForMax=" + str(q) + r"$",
            transform=ax.transAxes,
            verticalalignment="bottom",
            horizontalalignment="right",
            bbox=dict(facecolor="wheat", boxstyle="square,pad=0.2"),
        )

    fig.subplots_adjust(top=0.99, bottom=0.08, left=0.092, right=0.915, hspace=0.04)

    fig.savefig(
        "paper/mvp_lower_bound.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def make_chart_for_ml_compressed():
    d_values = [0, 1, 2, 3, 4, 6, 9, 16, 24]

    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 2.6)
    ax.grid()

    hll = mvp.mvp_ml_compressed(d=0, b=2)
    ehll = mvp.mvp_ml_compressed(d=1, b=2)
    ull = mvp.mvp_ml_compressed(d=2, b=2)

    plot_improvement(ax, ull, hll, 2.7, 0.12)

    plotted_lines = []
    for d in d_values:
        plotted_lines += ax.plot(
            b_values,
            [mvp.mvp_ml_compressed(d=d, b=b).mvp for b in b_values],
            label=r"$\symNumExtraBits=" + str(d) + "$",
            color=colors[d],
            linestyle=linestyles[d],
        )

    ax.set_ylim([1.8, 4.5])
    ax.set_xlim([1, max_b])
    ax.set_xlabel(r"base $\symBase$")
    ax.set_ylabel(r"memory-variance product")

    offset_y = 0.02
    offset_x = 0.02

    ax.plot([hll.b], [hll.mvp], color=colors[0], marker=marker, markersize=marker_size)
    ax.text(hll.b + offset_x, hll.mvp + offset_y, r"HLL", horizontalalignment="left")

    ax.plot(
        [ehll.b], [ehll.mvp], color=colors[1], marker=marker, markersize=marker_size
    )
    ax.text(ehll.b + offset_x, ehll.mvp + offset_y, r"EHLL", horizontalalignment="left")

    ax.plot([ull.b], [ull.mvp], color=colors[2], marker=marker, markersize=marker_size)
    ax.text(ull.b + offset_x, ull.mvp + offset_y, "ULL", horizontalalignment="left")

    labelLine(plotted_lines[0], 1.66, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[1], 1.58, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[2], 1.53, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[3], 1.48, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[4], 1.46, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[5], 1.38, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[6], 1.27, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[7], 1.19, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[8], 1.1, bbox=bbox, outline_width=outline_width)

    hllmvp = hll.mvp
    secax = ax.secondary_yaxis(
        "right",
        functions=(
            lambda x: (x - hllmvp) / hllmvp * 100,
            lambda x: (100 + x) * hllmvp / 100,
        ),
    )
    secax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

    ax.set_xticks(xtick_positions)

    fig.subplots_adjust(top=0.98, bottom=0.15, left=0.092, right=0.915, hspace=0.08)

    fig.savefig(
        "paper/mvp_compressed.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def make_chart_for_martingale_compressed():
    d_values = [0, 1, 2, 3, 4, 6, 9, 16, 24]

    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 2.6)
    ax.grid()

    hll = mvp.mvp_martingale_compressed(d=0, b=2)
    ehll = mvp.mvp_martingale_compressed(d=1, b=2)
    ull = mvp.mvp_martingale_compressed(d=2, b=2)

    plot_improvement(ax, ull, hll, 2.7, 0.14)

    plotted_lines = []
    for d in d_values:
        plotted_lines += ax.plot(
            b_values,
            [mvp.mvp_martingale_compressed(d=d, b=b).mvp for b in b_values],
            label=r"$\symNumExtraBits=" + str(d) + "$",
            color=colors[d],
            linestyle=linestyles[d],
        )

    ax.set_ylim([1.6, 2.6])
    ax.set_xlim([1, max_b])
    ax.set_xlabel(r"base $\symBase$")
    ax.set_ylabel(r"memory-variance product")

    offset_y = 0.01
    offset_x = 0.02

    ax.plot([hll.b], [hll.mvp], color=colors[0], marker=marker, markersize=marker_size)
    ax.text(hll.b + offset_x, hll.mvp + offset_y, r"HLL", horizontalalignment="left")

    ax.plot(
        [ehll.b], [ehll.mvp], color=colors[1], marker=marker, markersize=marker_size
    )
    ax.text(ehll.b + offset_x, ehll.mvp + offset_y, r"EHLL", horizontalalignment="left")

    ax.plot([ull.b], [ull.mvp], color=colors[2], marker=marker, markersize=marker_size)
    ax.text(ull.b + offset_x, ull.mvp + offset_y, "ULL", horizontalalignment="left")

    labelLine(plotted_lines[0], 1.66, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[1], 1.58, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[2], 1.53, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[3], 1.48, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[4], 1.46, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[5], 1.38, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[6], 1.27, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[7], 1.19, bbox=bbox, outline_width=outline_width)
    labelLine(plotted_lines[8], 1.1, bbox=bbox, outline_width=outline_width)

    hllmvp = hll.mvp
    secax = ax.secondary_yaxis(
        "right",
        functions=(
            lambda x: (x - hllmvp) / hllmvp * 100,
            lambda x: (100 + x) * hllmvp / 100,
        ),
    )
    secax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

    ax.set_xticks(xtick_positions)

    fig.subplots_adjust(top=0.98, bottom=0.15, left=0.092, right=0.915, hspace=0.08)

    fig.savefig(
        "paper/mvp_compressed_martingale.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def make_chart_for_martingale():
    q_values = [6]
    d_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 18, 23, 30]

    fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)
    fig.set_size_inches(5, 2.6)

    hll = mvp.mvp_martingale(q=6, d=0, b=2)
    ehll = mvp.mvp_martingale(q=6, d=1, b=2)
    ull = mvp.mvp_martingale(q=6, d=2, b=2)

    for q, i in zip(q_values, range(len(q_values))):
        ax.grid()
        if q == 6:
            plot_improvement(ax, ull, hll, 2.7, 0.13)

        plotted_lines = []
        for d in d_values:
            plotted_lines += ax.plot(
                b_values,
                [mvp.mvp_martingale(q, d, b).mvp for b in b_values],
                label=r"$\symNumExtraBits=" + str(d) + "$",
                color=colors[d],
                linestyle=linestyles[d],
            )

        ax.set_ylim([2.4, 6])
        ax.set_xlim([1, max_b])
        if i == len(q_values) - 1:
            ax.set_xlabel(r"base $\symBase$")
        ax.set_ylabel(r"memory-variance product")

        if q == 6:
            offset_x = 0.05
            offset_y = 0.1

            ax.plot(
                [hll.b],
                [hll.mvp],
                color=colors[0],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                hll.b + offset_x,
                hll.mvp + offset_y,
                r"HLL",
                horizontalalignment="center",
            )

            ax.plot(
                [ehll.b],
                [ehll.mvp],
                color=colors[1],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                ehll.b + offset_x,
                ehll.mvp + offset_y,
                r"EHLL",
                horizontalalignment="center",
            )

            ax.plot(
                [ull.b],
                [ull.mvp],
                color=colors[2],
                marker=marker,
                markersize=marker_size,
            )
            ax.text(
                ull.b + offset_x,
                ull.mvp - offset_y,
                "ULL",
                horizontalalignment="center",
                verticalalignment="top",
            )

            labelLine(plotted_lines[0], 1.85, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[1], 1.85, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[2], 2.9, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[3], 2.85, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[4], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[5], 2.635, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[6], 2.505, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[7], 2.365, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[8], 2.235, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[9], 2.13, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[10], 2.029, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[11], 1.88, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[12], 1.755, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[13], 1.6, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[14], 1.475, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[15], 1.365, bbox=bbox, outline_width=outline_width)
        elif q == 7:
            labelLine(plotted_lines[0], 2.15, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[1], 2.15, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[2], 2.8, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[3], 2.75, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[4], 2.64, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[5], 2.525, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[6], 2.36, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[7], 2.23, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[8], 2.125, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[9], 2.04, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[10], 1.95, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[11], 1.88, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[12], 1.82, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[13], 1.7, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[14], 1.6, bbox=bbox, outline_width=outline_width)
            labelLine(plotted_lines[15], 1.5, bbox=bbox, outline_width=outline_width)
        else:
            labelLines(plotted_lines, bbox=bbox, outline_width=outline_width)

        hllmvp = hll.mvp
        secax = ax.secondary_yaxis(
            "right",
            functions=(
                lambda x: (x - hllmvp) / hllmvp * 100,
                lambda x: (100 + x) * hllmvp / 100,
            ),
        )
        secax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
        ax.set_xticks(xtick_positions)

        ax.text(
            0.97,
            0.05,
            r"$\symBitsForMax=" + str(q) + r"$",
            transform=ax.transAxes,
            verticalalignment="bottom",
            horizontalalignment="right",
            bbox=dict(facecolor="wheat", boxstyle="square,pad=0.2"),
        )

    fig.subplots_adjust(top=0.98, bottom=0.15, left=0.092, right=0.915, hspace=0.08)

    fig.savefig(
        "paper/mvp_martingale.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


print()
print("ML estimation:")
print_result(mvp.mvp_ml(6))
print_result(mvp.mvp_ml(6, b=2))
print_result(mvp.mvp_ml(8, b=2, d=0))
print_result(mvp.mvp_ml(6, d=2))
print_result(mvp.mvp_ml(6, d=0, b=2))
print_result(mvp.mvp_ml(6, d=2, b=2))
print_result(mvp.mvp_ml(7))
print_result(mvp.mvp_ml(7, d=17))
print_result(mvp.mvp_ml(7, b=sqrt(2.0)))
print_result(mvp.mvp_ml(7, d=9, b=sqrt(2.0)))
print_result(mvp.mvp_ml(7, d=9, b=pow(2.0, 1.0 / 3.0)))
print_result(mvp.mvp_ml(8, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml(8, d=8, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml(8, d=16, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml(8, d=20, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml(8, d=24, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml(8, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml(9, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml(9, b=sqrt(sqrt(sqrt(2.0)))))
print_result(mvp.mvp_ml(8))
print_result(mvp.mvp_ml(9))
print_result(mvp.mvp_ml(10))


print()
print("ML estimation (with optimal compression):")
print_result(mvp.mvp_ml_compressed(d=0, b=2))
print_result(mvp.mvp_ml_compressed(d=2, b=2))
print_result(mvp.mvp_ml_compressed(d=9, b=sqrt(2)))
print_result(mvp.mvp_ml_compressed(b=2))
print_result(mvp.mvp_ml_compressed(d=16, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml_compressed(d=24, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml_compressed(b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_ml_compressed(d=16, b=sqrt(sqrt(2))))
print_result(mvp.mvp_ml_compressed(d=20, b=sqrt(sqrt(2))))
print_result(mvp.mvp_ml_compressed(d=24, b=sqrt(sqrt(2))))


print()
print("GRA estimation:")
print_result(
    mvp.mvp_gra(6, d=0, b=2.0, t=1), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra(6, d=0, b=2.0, t=None), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra(8, d=0, b=2.0, t=1), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra(6, d=1, b=2.0, t=1), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra(6, d=1, b=2.0, t=None), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra(6, d=2, b=2.0, t=1), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra(6, d=2, b=2.0, t=None), mvp.calculate_contribution_coefficients_gra
)
print_result(
    mvp.mvp_gra(7, d=9, b=sqrt(2.0), t=None),
    mvp.calculate_contribution_coefficients_gra,
)
print_result(mvp.mvp_gra(6, b=2.0), mvp.calculate_contribution_coefficients_gra)
print_result(mvp.mvp_gra(7), mvp.calculate_contribution_coefficients_gra)
print_result(mvp.mvp_gra(6), mvp.calculate_contribution_coefficients_gra)
print_result(mvp.mvp_gra(5), mvp.calculate_contribution_coefficients_gra)

print_result(mvp.mvp_gra(16, d=0, b=1.001))
print_result(mvp.mvp_gra(16, d=0, b=1.001, t=1))


print()
print("FGRA estimation")
print_result(mvp.mvp_fgra(q=6, b=2, t=1), mvp.calculate_contribution_coefficients_fgra)
print_result(mvp.mvp_fgra(q=6, b=2), mvp.calculate_contribution_coefficients_fgra)


print()
print("Martingale estimation:")
print_result(mvp.mvp_martingale(6))
print_result(mvp.mvp_martingale(6, d=1, b=2))
print_result(mvp.mvp_martingale(6, d=2))
print_result(mvp.mvp_martingale(6, d=0, b=2))
print_result(mvp.mvp_martingale(6, d=2, b=2))
print_result(mvp.mvp_martingale(7))
print_result(mvp.mvp_martingale(7, d=17))
print_result(mvp.mvp_martingale(7, b=sqrt(2.0)))
print_result(mvp.mvp_martingale(7, d=9, b=sqrt(2.0)))
print_result(mvp.mvp_martingale(8, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_martingale(8, d=16, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_martingale(8, d=20, b=sqrt(sqrt(2.0))))
print_result(mvp.mvp_martingale(8, d=24, b=sqrt(sqrt(2.0))))


print()
print("Martingale estimation (with optimal compression):")
print_result(mvp.mvp_martingale_compressed())
print_result(mvp.mvp_martingale_compressed(d=1, b=2))
print_result(mvp.mvp_martingale_compressed(d=2))
print_result(mvp.mvp_martingale_compressed(d=0, b=2))
print_result(mvp.mvp_martingale_compressed(d=2, b=2))
print_result(mvp.mvp_martingale_compressed(d=16, b=sqrt(sqrt(2))))
print_result(mvp.mvp_martingale_compressed(d=20, b=sqrt(sqrt(2))))
print_result(mvp.mvp_martingale_compressed(d=24, b=sqrt(sqrt(2))))


# make figures

make_chart_for_martingale_compressed()
make_chart_for_ml_compressed()
make_chart_for_martingale()
make_chart_for_ml()
