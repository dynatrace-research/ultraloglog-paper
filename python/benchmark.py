#
# Copyright (c) 2023 Dynatrace LLC. All rights reserved.
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
import json
import matplotlib.pyplot as plt
from labellines import labelLine


def plot_add_performance_chart(data):
    relevant_data = filter(
        lambda x: x["benchmark"]
        == "com.dynatrace.ullpaper.HyperLogLogPerformanceTest.distinctCountAdd",
        data,
    )


bbox = None
outline_width = 4


def plot_estimation_chart(ax, data, sketch, estimator, title):
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
        num_examples = int(r["params"]["numExamples"])

        time = float(r["primaryMetric"]["score"]) / num_examples / 1e6

        if not p in d:
            d[p] = {}
        d[p][n] = time

    ax.set_xscale("log", base=10)
    ax.set_yscale("log", base=10)
    ax.set_xlim(1, 1e7)
    ax.set_ylim(3e-7, 1.2e-3)
    ax.grid()

    for p in sorted(d):
        dd = d[p]

        xvals = sorted(dd)
        yvals = [dd[x] for x in xvals]

        ax.plot(xvals, yvals, label="$" + str(p) + "$")
    for l in ax.get_lines():
        labelLine(l, 2.5, bbox=bbox, outline_width=outline_width, align=False)

    ax.text(
        0.06,
        0.93,
        title,
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="left",
        bbox=dict(facecolor="wheat"),
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
    axs[1][0].set_xlabel(r"distinct count")
    axs[1][1].set_xlabel(r"distinct count")

    fig.subplots_adjust(
        top=0.985, bottom=0.10, left=0.11, right=0.99, hspace=0.04, wspace=0.05
    )

    fig.savefig(
        "paper/estimation_performance.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


def plot_add_chart(ax, data, sketch, title):
    d = {}

    for r in data:
        if (
            r["benchmark"]
            != "com.dynatrace.ullpaper." + sketch + "PerformanceTest.distinctCountAdd"
        ):
            continue

        n = int(r["params"]["numElements"])
        p = int(r["params"]["precision"])

        time = float(r["primaryMetric"]["score"]) / 1e6 / n

        if not p in d:
            d[p] = {}
        d[p][n] = time

    ax.set_xscale("log", base=10)
    ax.set_yscale("log", base=10)
    ax.set_xlim(1, 1e7)
    # ax.set_ylim(3.5e-7, 1.1e-3)
    ax.grid()

    for p in sorted(d):
        if p % 2 != 0:
            continue
        dd = d[p]

        xvals = sorted(dd)
        yvals = [dd[x] for x in xvals]

        ax.plot(xvals, yvals, label="$" + str(p) + "$")
    for i, l in enumerate(ax.get_lines()):
        labelLine(l, 2.0, bbox=bbox, outline_width=outline_width, align=False)

    ax.text(
        0.96,
        0.95,
        title,
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(facecolor="wheat"),
    )


def plot_add(data):
    fig, axs = plt.subplots(1, 2, sharex=True, sharey=True)
    fig.set_size_inches(5, 2)

    plot_add_chart(axs[0], data, "HyperLogLog", "HLL")
    plot_add_chart(axs[1], data, "UltraLogLog", "ULL")

    axs[0].set_ylabel(r"time per element (s)")
    axs[0].set_xlabel(r"distinct count")
    axs[1].set_xlabel(r"distinct count")

    fig.subplots_adjust(
        top=0.985, bottom=0.20, left=0.11, right=0.99, hspace=0.04, wspace=0.05
    )

    fig.savefig(
        "paper/add_performance.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


f = open("results/benchmark-results.json")
data = json.load(f)
plot_estimation(data)
plot_add(data)
