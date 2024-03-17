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
import json
import matplotlib.pyplot as plt
from labellines import labelLine
import mvp
from math import sqrt

colors = ["C" + str(i + 1) for i in range(0, 21)]

bbox = None

bits_per_register = {"UltraLogLog": 8, "HyperLogLog": 6}


def plot_estimation_chart(ax, data, sketch, estimator, title):
    outline_width = 4
    d = {}

    for r in data:
        if (
            r["benchmark"]
            != "com.dynatrace.ullpaper."
            + sketch
            + "PerformanceTest.distinctCountEstimation"
        ):
            continue
        if r["params"]["estimator"] != estimator:
            continue

        n = int(r["params"]["numElements"])
        p = int(r["params"]["precision"])

        memorySizeForExamplesInBytes = int(r["params"]["memorySizeForExamplesInBytes"])

        sketch_size_in_bytes = 2**p * bits_per_register[sketch] // 8
        num_examples = memorySizeForExamplesInBytes // sketch_size_in_bytes

        time = float(r["primaryMetric"]["score"]) / num_examples / 1e6

        if not p in d:
            d[p] = {}
        d[p][n] = time

    ax.set_xscale("log", base=10)
    ax.set_yscale("log", base=10)
    ax.set_xlim(1, 1e7)
    ax.set_ylim(3e-7, 8e-4)
    ax.grid()

    for p in sorted(d):
        dd = d[p]

        xvals = sorted(dd)
        yvals = [dd[x] for x in xvals]

        ax.plot(xvals, yvals, label="$" + str(p) + "$", color=colors[p])
    for l in reversed(ax.get_lines()):
        labelLine(l, x=2.5, bbox=bbox, outline_width=outline_width, align=False)

    ax.text(
        0.03,
        0.96,
        title,
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="left",
        bbox=dict(facecolor="wheat", boxstyle="square,pad=0.2"),
    )


def plot_estimation(data):
    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True)
    fig.set_size_inches(5, 4)

    plot_estimation_chart(
        axs[0][0], data, "HyperLogLog", "MAXIMUM_LIKELIHOOD_ESTIMATOR", "HLL ML"
    )

    plot_estimation_chart(
        axs[1][0], data, "HyperLogLog", "CORRECTED_RAW_ESTIMATOR", "HLL CR"
    )

    plot_estimation_chart(
        axs[0][1], data, "UltraLogLog", "MAXIMUM_LIKELIHOOD_ESTIMATOR", "ULL ML"
    )

    plot_estimation_chart(
        axs[1][1], data, "UltraLogLog", "OPTIMAL_FGRA_ESTIMATOR", "ULL FGRA"
    )

    axs[0][0].set_ylabel(r"estimation time (s)")
    axs[1][0].set_ylabel(r"estimation time (s)")
    axs[1][0].set_xlabel(r"distinct count $\symCardinality$")
    axs[1][1].set_xlabel(r"distinct count $\symCardinality$")

    fig.subplots_adjust(
        top=0.985, bottom=0.10, left=0.11, right=0.99, hspace=0.04, wspace=0.05
    )

    fig.savefig(
        "paper/estimation_performance.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def plot_estimation_performance_over_theoretical_estimation_error_line(
    ax, data, distinct_count_weights, sketch, estimator, title, mvp, color, linestyle
):
    avgs = {}
    for r in data:
        if (
            r["benchmark"]
            != "com.dynatrace.ullpaper."
            + sketch
            + "PerformanceTest.distinctCountEstimation"
        ):
            continue
        if r["params"]["estimator"] != estimator:
            continue

        n = int(r["params"]["numElements"])
        if n not in distinct_count_weights:
            continue
        weight = 1 / len(distinct_count_weights)

        p = int(r["params"]["precision"])
        if p not in avgs:
            avgs[p] = 0

        memorySizeForExamplesInBytes = int(r["params"]["memorySizeForExamplesInBytes"])

        sketch_size_in_bytes = 2**p * bits_per_register[sketch] // 8
        num_examples = memorySizeForExamplesInBytes // sketch_size_in_bytes

        time = float(r["primaryMetric"]["score"]) / num_examples / 1e6
        avgs[p] += weight * time

    pvals = sorted(avgs)
    xvals = [100.0 * sqrt(mvp / (pow(2, p) * bits_per_register[sketch])) for p in pvals]
    yvals = [avgs[p] for p in pvals]

    ax.plot(xvals, yvals, label=title, marker=".", color=color, linestyle=linestyle)


def plot_estimation_performance_over_theoretical_estimation_error_subplot(
    data, ax, distinct_count_weights, label
):
    ax.set_xscale("log", base=10)
    ax.set_yscale("log", base=10)
    ax.set_xlim([2.5e-1, 1e1])

    plot_estimation_performance_over_theoretical_estimation_error_line(
        ax,
        data,
        distinct_count_weights,
        "HyperLogLog",
        "MAXIMUM_LIKELIHOOD_ESTIMATOR",
        "HLL ML",
        mvp=mvp.mvp_ml(b=2, d=0, q=6).mvp,
        color="C13",
        linestyle="dotted",
    )
    plot_estimation_performance_over_theoretical_estimation_error_line(
        ax,
        data,
        distinct_count_weights,
        "HyperLogLog",
        "CORRECTED_RAW_ESTIMATOR",
        "HLL CR",
        mvp=mvp.mvp_gra(b=2, d=0, q=6, t=1).mvp,
        color="C11",
        linestyle="dashed",
    )
    plot_estimation_performance_over_theoretical_estimation_error_line(
        ax,
        data,
        distinct_count_weights,
        "UltraLogLog",
        "MAXIMUM_LIKELIHOOD_ESTIMATOR",
        "ULL ML",
        mvp=mvp.mvp_ml(b=2, d=2, q=6).mvp,
        color="C15",
        linestyle="dashdot",
    )
    plot_estimation_performance_over_theoretical_estimation_error_line(
        ax,
        data,
        distinct_count_weights,
        "UltraLogLog",
        "OPTIMAL_FGRA_ESTIMATOR",
        "ULL FGRA",
        mvp=mvp.mvp_fgra(b=2, q=6).mvp,
        color="C9",
        linestyle="solid",
    )

    ax.text(
        0.97,
        0.95,
        label,
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(facecolor="wheat", boxstyle="square,pad=0.2"),
    )


def plot_estimation_performance_over_theoretical_estimation_error(data):
    fig = plt.figure(figsize=(5, 1.5))
    ax_max = fig.add_subplot(1, 2, 1)
    ax_avg = fig.add_subplot(1, 2, 2)
    ax_max.sharey(ax_avg)
    ax_avg.tick_params(labelleft=False)
    ax_max.set_xlabel(r"theoretical relative error (\%)")
    ax_avg.set_xlabel(r"theoretical relative error (\%)")
    ax_max.set_ylabel(r"estimation time (s)")
    distinct_counts = [
        10000000,
        5000000,
        2000000,
        1000000,
        500000,
        200000,
        100000,
        50000,
        20000,
        10000,
        5000,
        2000,
        1000,
        500,
        200,
        100,
        50,
        20,
        10,
        5,
        2,
        1,
    ]

    plot_estimation_performance_over_theoretical_estimation_error_subplot(
        data,
        ax_max,
        [10**6],
        r"$\symCardinality=10^6$",
    )
    plot_estimation_performance_over_theoretical_estimation_error_subplot(
        data, ax_avg, distinct_counts, r"average"
    )
    ax_avg.set_xticks([1, 10], [r"1", r"10"])
    ax_max.set_xticks([1, 10], [r"1", r"10"])
    ax_avg.grid()
    ax_max.grid()

    handles, labels = ax_avg.get_legend_handles_labels()
    legend_order = [3, 2, 1, 0]
    fig.legend(
        [handles[i] for i in legend_order],
        [labels[i] for i in legend_order],
        loc="center right",
        columnspacing=1,
        labelspacing=0.2,
        borderpad=0.2,
        handletextpad=0.4,
        fancybox=False,
        framealpha=1,
    )

    fig.subplots_adjust(top=0.985, bottom=0.275, left=0.11, right=0.77, wspace=0.04)
    fig.savefig(
        "paper/estimation_performance_over_error.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def plot_add_chart(ax, data, test_name, sketch, title):
    outline_width = 3.5
    d = {}

    allocation_time = {}
    for r in data:
        if (
            r["benchmark"]
            != "com.dynatrace.ullpaper." + sketch + "PerformanceTest." + test_name
        ):
            continue

        n = int(r["params"]["numElements"])
        p = int(r["params"]["precision"])

        if n == 0:
            allocation_time[p] = float(r["primaryMetric"]["score"]) / 1e6

    for r in data:
        if (
            r["benchmark"]
            != "com.dynatrace.ullpaper." + sketch + "PerformanceTest." + test_name
        ):
            continue

        n = int(r["params"]["numElements"])
        p = int(r["params"]["precision"])

        if n == 0:
            continue

        time = (float(r["primaryMetric"]["score"]) / 1e6) / n

        if not p in d:
            d[p] = {}
        d[p][n] = time

    ax.set_xscale("log", base=10)
    ax.set_yscale("log", base=10)
    ax.set_xlim(1, 1e7)
    ax.set_ylim(4e-9, 1e-5)
    ax.grid()

    for p in sorted(d):
        if p % 2 != 0:
            continue
        dd = d[p]

        xvals = sorted(dd)
        yvals = [dd[x] for x in xvals]

        ax.plot(xvals, yvals, label="$" + str(p) + "$", color=colors[p])
    for i, l in enumerate(reversed(ax.get_lines())):
        labelLine(
            l,
            1.8,
            bbox=bbox,
            outline_width=outline_width,
            align=False,
            yoffset_logspace=True,
            yoffset=-(i - 2) * 0.05,
        )

    ax.text(
        0.96,
        0.95,
        title,
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(facecolor="wheat", boxstyle="square,pad=0.2"),
    )


def plot_add(data):
    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True)
    fig.set_size_inches(5, 2.8)

    plot_add_chart(axs[0][0], data, "distinctCountAdd", "HyperLogLog", "HLL")
    plot_add_chart(axs[0][1], data, "distinctCountAdd", "UltraLogLog", "ULL")
    plot_add_chart(
        axs[1][0],
        data,
        "distinctCountAddWithMartingaleEstimator",
        "HyperLogLog",
        "HLL + martingale estimator",
    )
    plot_add_chart(
        axs[1][1],
        data,
        "distinctCountAddWithMartingaleEstimator",
        "UltraLogLog",
        "ULL + martingale estimator",
    )

    axs[0][0].set_ylabel(r"time per element (s)")
    axs[1][0].set_ylabel(r"time per element (s)")
    axs[1][0].set_xlabel(r"distinct count $\symCardinality$")
    axs[1][1].set_xlabel(r"distinct count $\symCardinality$")

    fig.subplots_adjust(
        top=0.97, bottom=0.14, left=0.11, right=0.995, hspace=0.07, wspace=0.05
    )

    fig.savefig(
        "paper/add_performance.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


f = open("results/benchmark-results.json")
data = json.load(f)
plot_estimation_performance_over_theoretical_estimation_error(data)
plot_estimation(data)
plot_add(data)
