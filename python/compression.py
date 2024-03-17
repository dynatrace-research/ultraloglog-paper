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
import csv
import matplotlib.pyplot as plt
import mvp
from functools import partial


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
                        d = i.split("=")
                        info[d[0].strip()] = d[1].strip()

            elif row_counter == 1:
                for i in r:
                    if i != "":
                        headers.append(i.strip())
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


def plot():
    colors = ["C3", "C1", "C0", "C2"]
    linestyles = ["solid", "solid", "dashed", "dotted"]

    compression_algorithms = {
        "lzma": "LZMA",
        "deflate": "Deflate",
        "zstd": "zstd",
        "bzip2": "bzip2",
    }
    inputs = ["ull", "hll6", "hll8"]
    pvals = [8, 12, 16]

    fig, axs = plt.subplots(
        len(pvals), len(inputs), sharex=True, sharey="row"
    )  # "row")
    fig.set_size_inches(5, 5.2)

    for p_idx in range(len(pvals)):
        p = pvals[p_idx]
        data = read_data("results/compression/compression" + str(p) + ".csv")
        values = data[1]

        distinct_counts = values["true distinct count"]

        for input_idx in range(len(inputs)):
            ax = axs[input_idx][p_idx]
            input = inputs[input_idx]

            ax.set_xscale("log", base=10)
            ax.set_xlim([1, distinct_counts[-1]])
            if input_idx + 1 == len(inputs):
                ax.set_xlabel(r"distinct count $\symCardinality$")
            if p_idx == 0:
                ax.set_ylabel("inverse compression ratio")

            if input == "ull":
                d = 2
            else:
                d = 0

            # fisher = mvp.calculate_fisher_information(d=d, b=2)
            entropy = mvp.calculate_entropy(d=d, b=2)
            uncompressed_size = (6.0 + d) * pow(2, p) / 8.0
            best_compression_size = entropy * pow(2, p) / 8
            theoretical_mvp = mvp.mvp_ml(q=6, d=d, b=2).mvp

            if p_idx == len(pvals) - 1:
                compratio2mvp = lambda x, factor: x * factor
                mvp2compratio = lambda x, factor: x / factor

                secax = ax.secondary_yaxis(
                    "right",
                    functions=(
                        partial(compratio2mvp, factor=theoretical_mvp),
                        partial(mvp2compratio, factor=theoretical_mvp),
                    ),
                )
                secax.set_ylabel("theoretical \\symMVP")
                secax.set_yticks([0, 1, 2, 3, 4, 5, 6, 7])
                ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2])
                ax.set_ylim([0, mvp2compratio(7.6, theoretical_mvp)])

            distinct_count_range = [
                values["true distinct count"][0],
                values["true distinct count"][-1],
            ]

            ax.plot(
                distinct_count_range,
                [
                    best_compression_size / uncompressed_size,
                    best_compression_size / uncompressed_size,
                ],
                label="theoretical limit",
                linestyle="dashed",
                color="gray",
            )

            ax.plot(
                distinct_count_range,
                [
                    1,
                    1,
                ],
                label="uncompressed",
                linestyle="solid",
                color="gray",
            )

            for compression_algorithm, linestyle, color in zip(
                compression_algorithms, linestyles, colors
            ):
                compressed_bytes = values[
                    "compressed bytes " + input + " " + compression_algorithm
                ]
                data = [
                    compressed_bytes[i] / uncompressed_size
                    for i in range(len(distinct_counts))
                ]
                ax.plot(
                    distinct_counts,
                    data,
                    label=compression_algorithms[compression_algorithm],
                    color=color,
                    linestyle=linestyle,
                )

            if input == "hll6":
                desc = r"HLL, $\symPrecision=" + str(p) + "$"
            elif input == "hll8":
                desc = r"HLL*, $\symPrecision=" + str(p) + "$"
            elif input == "ull":
                desc = r"ULL, $\symPrecision=" + str(p) + "$"
            else:
                assert False

            ax.text(
                0.3,
                0.06,
                desc,
                transform=ax.transAxes,
                verticalalignment="bottom",
                horizontalalignment="left",
                bbox=dict(facecolor="wheat", boxstyle="square,pad=0.2"),
            )

    for p_idx in range(len(pvals)):
        for input_idx in range(len(inputs)):
            ax = axs[input_idx][p_idx]
            # ax.set_ylim([0, 1.3])
            # ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
            ax.set_xticks([1, 1e6, 1e12, 1e18])

    handles, labels = ax.get_legend_handles_labels()
    legend_order = [1, 0, 2, 3, 4, 5]
    fig.legend(
        [handles[i] for i in legend_order],
        [labels[i] for i in legend_order],
        loc="upper center",
        ncol=3,
        bbox_to_anchor=(0.5, 0.998),
        columnspacing=1,
        labelspacing=0.2,
        borderpad=0.2,
        handletextpad=0.4,
        fancybox=False,
        framealpha=1,
    )

    fig.subplots_adjust(
        left=0.09, bottom=0.075, right=0.933, top=0.997, wspace=0.08, hspace=0.06
    )

    fig.savefig(
        "paper/compression.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


plot()
