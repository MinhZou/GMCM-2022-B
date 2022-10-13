# -*- coding: utf-8 -*-
"""
@author: MinhZou
@date: 2022-10-11
@e-mail: 770445973@qq.com
@refer from: https://github.com/kotarot/rectangle-packing-solver
"""

from typing import Tuple
import matplotlib.patches as patches
from matplotlib import pylab as plt

from utils.path import mkdir_or_exist


class Visualizer:
    """
    A floorplan visualizer.
    """
    def __init__(self) -> None:
        plt.rcParams["font.size"] = 14

    def visualize(self, batch, num, bins, bb_w=2440, bb_h=1220, prefix_path=None, title: str = "floor_plan") -> None:

        # Figure settings
        bb_width = bb_w
        bb_height = bb_h
        fig = plt.figure(figsize=(10, 10 * bb_height / bb_width + 0.5))
        ax = plt.axes()
        ax.set_aspect("equal")
        plt.xlim([0, bb_width])
        plt.ylim([0, bb_height])
        plt.xlabel("width")
        plt.ylabel("height")
        plt.title(title)

        # Plot every rectangle
        colors = []
        front_colors = []
        for i in range(3):
            color, fontcolor = self.get_color(i)
            colors.append(color)
            front_colors.append(fontcolor)
        for i, rect in enumerate(bins):
            # color, fontcolor = self.get_color(i)
            r = patches.Rectangle(
                xy=(rect.x, rect.y),
                width=rect.width,
                height=rect.height,
                edgecolor="#000000",
                facecolor=colors[rect.stage],
                alpha=1.0,
                fill=True,
            )
            ax.add_patch(r)

            # Add text label
            centering_offset = 0.011
            center_x = rect.x + rect.width / 2 - bb_width * centering_offset
            center_y = rect.y + rect.height / 2 - bb_height * centering_offset
            ax.text(x=center_x, y=center_y, s=rect.idx, fontsize=18, color=front_colors[rect.stage])

        # Output
        if prefix_path is None:
            plt.show()
        else:
            prefix_path = prefix_path + '/fig/'
            mkdir_or_exist(prefix_path)
            path = prefix_path + '/floor_plan_{}_{}_{}.png'.format(bins[0].material, batch, num)
            fig.savefig(path)

        plt.close()

    @classmethod
    def get_color(cls, i: int = 0) -> Tuple[str, str]:
        """
        Gets rectangle face color (and its font color) from matplotlib cmap.
        """
        cmap = plt.get_cmap("tab10") # tab10
        color = cmap(i % cmap.N)
        brightness = max(color[0], color[1], color[2])

        if 0.85 < brightness:
            fontcolor = "#000000"
        else:
            fontcolor = "#ffffff"

        return color, fontcolor
