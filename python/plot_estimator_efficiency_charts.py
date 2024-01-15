#
# Copyright (c) 2022-2024 Dynatrace LLC. All rights reserved.
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
from labellines import labelLine
import mvp
from matplotlib.patches import ConnectionPatch

colors = ["C" + str(i) for i in range(0, 65)]
gra_color = colors[2]
fgra_color = "black"
linestyles = ["solid"] * 66

bbox = None
outline_width = 6
outline_width_2 = 8

marker = "x"
marker_size = 5


def make_gra_efficiency_chart():
    q = 6
    d_ull = 2
    b_ull = 2
    d_values = reversed([0, 1, 2, 3, 4, 5, 8, 16, 32, 64])
    b_values = numpy.linspace(1, 4, 1000)
    t_values = numpy.linspace(0.001, 2, 1000)

    fig = plt.figure(figsize=(5, 2.6))
    ax_base = fig.add_subplot(1, 3, (1, 2))
    ax_comp = fig.add_subplot(1, 3, 3)
    ax_base.sharey(ax_comp)

    optimal_mvp = mvp.mvp_ml(q, d=d_ull, b=b_ull).mvp
    gra_opt = mvp.mvp_gra(q, d=d_ull, b=b_ull)
    new_opt = mvp.mvp_fgra(q, b=b_ull)

    con = ConnectionPatch(
        xyA=(b_ull, optimal_mvp / gra_opt.mvp),
        xyB=(gra_opt.t, optimal_mvp / gra_opt.mvp),
        coordsA="data",
        coordsB="data",
        axesA=ax_base,
        axesB=ax_comp,
        color=gra_color,
        linestyle="dashed",
    )
    fig.add_artist(con)

    for d in d_values:
        ax_base.plot(
            b_values,
            [mvp.mvp_ml(q, d, b).mvp / mvp.mvp_gra(q, d, b).mvp for b in b_values],
            label=r"$\symNumExtraBits=" + str(d) + "$",
            color=colors[d],
            linestyle=linestyles[d],
        )

    ax_base.set_ylim([0.7, 1.025])
    ax_base.set_xlim([1, 2.1])
    ax_base.set_xlabel(r"base $\symBase$")
    ax_base.set_ylabel(r"estimator efficiency")
    ax_base.grid()

    fig.text(
        0.01,
        0.99,
        r"a)",
        transform=ax_base.transAxes,
        verticalalignment="top",
        horizontalalignment="left",
    )

    labelLine(ax_base.get_lines()[9], 1.2, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[8], 1.5, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[7], 1.4, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[6], 1.35, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[5], 1.32, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[4], 1.25, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[3], 1.58, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[2], 1.32, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[1], 1.198, bbox=bbox, outline_width=outline_width)
    labelLine(ax_base.get_lines()[0], 1.119, bbox=bbox, outline_width=outline_width)

    ax_comp.plot(
        t_values,
        [optimal_mvp / mvp.mvp_gra(q, d=d_ull, b=b_ull, t=t).mvp for t in t_values],
        label="GRA estimator",
        color=gra_color,
    )

    ax_comp.plot(
        t_values,
        [optimal_mvp / mvp.mvp_fgra(q, b=b_ull, t=t).mvp for t in t_values],
        label="FGRA estimator (new)",
        color=fgra_color,
    )

    ax_comp.set_xlim([0, 2])
    ax_comp.set_xlabel(r"$\symGRA$")
    ax_comp.grid()
    ax_comp.tick_params(labelleft=False)

    ax_comp.plot(
        gra_opt.t,
        optimal_mvp / gra_opt.mvp,
        color=gra_color,
        marker=marker,
        markersize=marker_size,
    )

    ax_base.plot(
        b_ull,
        optimal_mvp / gra_opt.mvp,
        color=gra_color,
        marker=marker,
        markersize=marker_size,
    )

    ax_comp.plot(
        new_opt.t,
        optimal_mvp / new_opt.mvp,
        color=fgra_color,
        marker=marker,
        markersize=marker_size,
    )

    fig.text(
        0.5,
        0.03,
        r"$\symBase=2, \symNumExtraBits=2$",
        transform=ax_comp.transAxes,
        verticalalignment="bottom",
        horizontalalignment="center",
        bbox=dict(facecolor="wheat", boxstyle="square,pad=0.2"),
    )

    fig.text(
        0.5,
        0.03,
        r"optimal $\symGRA$",
        transform=ax_base.transAxes,
        verticalalignment="bottom",
        horizontalalignment="center",
        bbox=dict(facecolor="wheat", boxstyle="square,pad=0.2"),
    )

    fig.text(
        0.01,
        0.99,
        r"b)",
        transform=ax_comp.transAxes,
        verticalalignment="top",
        horizontalalignment="left",
    )

    labelLine(ax_comp.get_lines()[0], 1.37, bbox=bbox, outline_width=outline_width_2)
    labelLine(ax_comp.get_lines()[1], 1.57, bbox=bbox, outline_width=outline_width_2)

    fig.subplots_adjust(top=0.99, bottom=0.15, left=0.105, right=0.99, wspace=0.06)

    fig.savefig(
        "paper/gra_efficiency.pdf",
        format="pdf",
        dpi=1200,
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


make_gra_efficiency_chart()
