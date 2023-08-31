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
import mvp


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
    inputs = ["hll6", "hll8", "ull"]
    pvals = [8, 12, 16]

    fig, axs = plt.subplots(len(pvals), len(inputs), sharex=True, sharey="row")
    fig.set_size_inches(5, 6)

    for p_idx in range(len(pvals)):
        p = pvals[p_idx]
        d = read_data("results/compression/compression" + str(p) + ".csv")
        values = d[1]
        headers = d[0]

        distinct_counts = values["true distinct count"]

        for input_idx in range(len(inputs)):
            ax = axs[p_idx][input_idx]
            input = inputs[input_idx]

            ax.set_xscale("log", base=10)
            ax.set_xlim([1, distinct_counts[-1]])
            if p_idx + 1 == len(pvals):
                ax.set_xlabel("distinct count")
            if input_idx == 0:
                ax.set_ylabel("inverse compression ratio")

            if input == "ull":
                best_compression_size = (
                    mvp.calculate_entropy(d=2, b=2) / 8.0 * pow(2, p)
                )
            else:
                best_compression_size = (
                    mvp.calculate_entropy(d=0, b=2) / 8.0 * pow(2, p)
                )

            if input == "ull":
                uncompressed_size = pow(2, p)
            else:
                uncompressed_size = pow(2, p) * 6 / 8

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
                desc = "HLL\n$\symPrecision=" + str(p) + "$"
            elif input == "hll8":
                desc = "HLL*\n$\symPrecision=" + str(p) + "$"
            elif input == "ull":
                desc = "ULL\n$\symPrecision=" + str(p) + "$"
            else:
                assert False

            ax.text(
                0.52,
                0.08,
                desc,
                transform=ax.transAxes,
                verticalalignment="bottom",
                horizontalalignment="center",
                bbox=dict(facecolor="wheat"),
            )

    for p_idx in range(len(pvals)):
        for input_idx in range(len(inputs)):
            ax = axs[p_idx][input_idx]
            ax.set_ylim([0, ax.get_ylim()[1]])

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, columnspacing=1.2)
    fig.subplots_adjust(
        left=0.105, bottom=0.13, right=0.99, top=0.99, wspace=0.08, hspace=0.06
    )

    fig.savefig(
        "paper/compression.pdf",
        format="pdf",
        dpi=1200,
        metadata={"creationDate": None},
    )
    plt.close(fig)


plot()
