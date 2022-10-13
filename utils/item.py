# -*- coding: utf-8 -*-
"""
@author: MinhZou
@date: 2022-10-11
@e-mail: 770445973@qq.com

2D Item class.
"""


class Item:
    """
    Items class for rectangles to be inserted.
    """
    def __init__(self, idx, width, height, corner_point: tuple = (0, 0),
                 material='', order='', num='') -> None:
        self.width = width
        self.height = height
        self.x = corner_point[0]
        self.y = corner_point[1]
        self.area = self.width * self.height
        self.rotated = False
        self.idx = idx
        self.num = num
        self.material = material
        self.order = order
        self.stage = 0

    def __repr__(self):
        return 'Item(id={}, width={}, height={}, x={}, y={}, material={}, order={}, stage={})'.format(
            self.idx, self.width, self.height, self.x, self.y, self.material, self.order, self.stage)

    def rotate(self) -> None:
        self.width, self.height = self.height, self.width
        # self.rotated = False if self.rotated is True else True
        self.rotated = True
