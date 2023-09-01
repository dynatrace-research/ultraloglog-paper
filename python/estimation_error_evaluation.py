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
import csv
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import mvp
from math import sqrt


def read_data(data_file):
    info = {}

    with open(data_file, "r") as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=";")
        row_counter = 0
        headers = []
        values = []
        for r in reader:
            if row_counter == 0:
                for i in r:
                    if i != "":
                        g = i.split("=")
                        info[g[0]] = g[1]

            elif row_counter == 1:
                for i in r:
                    if i != "":
                        headers.append(i)
                        values.append([])
            elif row_counter >= 2:
                k = 0
                for i in r:
                    if i != "":
                        values[k].append(float(i))
                        k += 1
            row_counter += 1

    data = {h: v for h, v in zip(headers, values)}
    size = row_counter - 2
    return info, data, size


def to_percent(values):
    return [100.0 * v for v in values]


colors = ["C2", "C0", "C1"]

fig, axs = plt.subplots(3, 1, sharex=True)
fig.set_size_inches(5, 7)

pvals = [8, 12, 16]


# num_simulation_runs_unit = ""
# num_simulation_runs = int(headers["num_cycles"])
# if num_simulation_runs % 1000 == 0:
#     num_simulation_runs //= 1000
#     num_simulation_runs_unit = "k"
# if num_simulation_runs % 1000 == 0:
#     num_simulation_runs //= 1000
#     num_simulation_runs_unit = "M"


for pidx in range(len(pvals)):
    p = pvals[pidx]
    ax = axs[pidx]

    d = read_data(
        "hash4j/test-results/ultraloglog-estimation-error-p" + str(p).zfill(2) + ".csv"
    )

    values = d[1]
    headers = d[0]

    large_scale_simulation_mode_distinct_count_limit = int(
        headers["large_scale_simulation_mode_distinct_count_limit"]
    )

    ax.set_xscale("log", base=10)
    theory = to_percent(values["theoretical relative standard error default"])[0]

    ax.set_ylim([-theory * 0.1, theory * 1.25])
    ax.set_xlim([1, values["distinct count"][-1]])
    # ax.xaxis.grid(True)
    if pidx == len(pvals) - 1:
        ax.set_xlabel("distinct count")
    # ax.yaxis.grid(True)
    ax.set_ylabel("relative error (\%)")

    # draw transition
    ax.plot(
        [
            large_scale_simulation_mode_distinct_count_limit,
            large_scale_simulation_mode_distinct_count_limit,
        ],
        [-theory * 2, theory * 2],
        color="red",
        linestyle="dashed",
        linewidth=0.8,
    )

    rel_error_martingale_theory = sqrt(
        mvp.mvp_martingale_eval(b=2, d=2, q=6).mvp / (8 * pow(2, p))
    )
    rel_error_ml_theory = sqrt(
        mvp.mvp_lower_bound_eval(b=2, d=2, q=6).mvp / (8 * pow(2, p))
    )
    rel_error_fgra_theory = sqrt(mvp.mvp_gra_eval(b=2, d=2, q=6).mvp / (8 * pow(2, p)))

    ax.plot(
        values["distinct count"],
        to_percent([rel_error_martingale_theory] * len(values["distinct count"])),
        label="martingale theory",
        color=colors[2],
        linestyle="dotted",
    )
    ax.plot(
        values["distinct count"],
        to_percent([rel_error_ml_theory] * len(values["distinct count"])),
        label="ML theory",
        color=colors[2],
        linestyle="dashed",
    )
    ax.plot(
        values["distinct count"],
        to_percent([rel_error_fgra_theory] * len(values["distinct count"])),
        label="FGRA theory",
        color=colors[2],
    )

    ax.plot(
        values["distinct count"],
        to_percent(values["relative rmse martingale"]),
        label="martingale rmse",
        color=colors[1],
        linestyle="dotted",
    )
    ax.plot(
        values["distinct count"],
        to_percent(values["relative rmse maximum likelihood"]),
        label="ML rmse ML",
        color=colors[1],
        linestyle="dashed",
    )
    ax.plot(
        values["distinct count"],
        to_percent(values["relative rmse default"]),
        label="FGRA rmse",
        color=colors[1],
    )

    ax.plot(
        values["distinct count"],
        to_percent(values["relative bias martingale"]),
        label="martingale bias",
        color=colors[0],
        linestyle="dotted",
    )
    ax.plot(
        values["distinct count"],
        to_percent(values["relative bias maximum likelihood"]),
        label="ML bias",
        color=colors[0],
        linestyle="dashed",
    )
    ax.plot(
        values["distinct count"],
        to_percent(values["relative bias default"]),
        label="FGRA bias",
        color=colors[0],
    )

    ax.text(
        0.03,
        0.945,
        "$p=" + str(p) + "$",
        transform=ax.transAxes,
        verticalalignment="top",
        horizontalalignment="left",
        bbox=dict(facecolor="wheat"),
    )

legend_elements = [
    Line2D([0], [0], color=colors[0]),
    Line2D([0], [0], color=colors[1]),
    Line2D([0], [0], color=colors[2]),
    Line2D([0], [0], color=colors[0], linestyle="dashed"),
    Line2D([0], [0], color=colors[1], linestyle="dashed"),
    Line2D([0], [0], color=colors[2], linestyle="dashed"),
    Line2D([0], [0], color=colors[0], linestyle="dotted"),
    Line2D([0], [0], color=colors[1], linestyle="dotted"),
    Line2D([0], [0], color=colors[2], linestyle="dotted"),
]
fig.legend(
    legend_elements,
    [
        "FGRA bias",
        "FGRA RMSE",
        "FGRA theory",
        "ML bias",
        "ML RMSE",
        "ML theory",
        "martingale bias",
        "martingale RMSE",
        "martingale theory",
    ],
    loc="lower center",
    ncol=3,
)
fig.subplots_adjust(top=0.99, bottom=0.162, left=0.095, right=0.97, hspace=0.05)

fig.savefig(
    "paper/estimation_error.pdf",
    format="pdf",
    dpi=1200,
    metadata={"creationDate": None},
)
plt.close(fig)
