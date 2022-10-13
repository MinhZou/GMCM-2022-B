"""
Three-Stage Guillotine Style 2D Bin Algorithm

@author: MinhZou
@date: 2022-10-11
@e-mail: 770445973@qq.com
@refer from: https://github.com/solomon-b/greedypacker
"""

import typing
from typing import List, Tuple
from sortedcontainers import SortedListWithKey  # type: ignore

from utils.item import Item


class FreeRectangle(typing.NamedTuple('FreeRectangle',
                                      [('width', int), ('height', int), ('x', int),
                                       ('y', int), ('stage', int), ('split', int)])):
    __slots__ = ()

    @property
    def area(self):
        return self.width * self.height


class Guillotine:
    def __init__(self, x: int = 8,
                 y: int = 4,
                 rotation: bool = True,
                 heuristic: str = 'best_area_fit',
                 rectangle_merge: bool = True,
                 split_heuristic: str = 'SplitSameAsPreviousAxis',
                 init_split: int = 0) -> None:
        self.x = x
        self.y = y
        self.area = self.x * self.y
        self.free_area = self.x * self.y
        self.rMerge = rectangle_merge
        self.split_heuristic = split_heuristic
        self.stage = 0
        self.init_split = init_split  # True

        if heuristic == 'best_area':
            self._score = score_baf
        elif heuristic == 'best_short_side':
            self._score = score_bssf
        elif heuristic == 'best_long_side':
            self._score = score_blsf
        elif heuristic == 'worst_area':
            self._score = score_waf
        elif heuristic == 'worst_short_side':
            self._score = score_wssf
        elif heuristic == 'worst_long_side':
            self._score = score_wlsf
        else:
            raise ValueError('No such heuristic!')

        if x == 0 or y == 0:
            # self.free_rects = [] # type: List[FreeRectangle]
            self.free_rects = SortedListWithKey(iterable=None, key=lambda x: x.area)
        else:
            self.free_rects = SortedListWithKey([FreeRectangle(self.x, self.y, 0, 0, 0, self.init_split)],
                                                key=lambda x: x.area)
        self.items = []  # type: List[Item]
        self.rotation = rotation

    def __repr__(self) -> str:
        return "Guillotine({})".format(self.items)

    @staticmethod
    def _item_fits_rect(item: Item, rect: FreeRectangle, rotation: bool = False) -> bool:
        if rect.stage <= 1:
            if not rotation and item.width <= rect.width and item.height <= rect.height:
                return True
            if rotation and item.height <= rect.width and item.width <= rect.height:
                return True
        else:
            if not rotation and rect.split == 0 and item.height <= rect.height and item.width == rect.width:
                return True
            if not rotation and rect.split == 1 and item.width <= rect.width and item.height == rect.height:
                return True
            if rotation and rect.split == 0 and item.width <= rect.height and item.height == rect.width:
                return True
            if rotation and rect.split == 1 and item.height <= rect.width and item.width == rect.height:
                return True
        return False

    @staticmethod
    def _split_along_axis(free_rect: FreeRectangle, item: Item, split: bool) -> List[FreeRectangle]:
        top_x = free_rect.x
        top_y = free_rect.y + item.height
        top_h = free_rect.height - item.height

        right_x = free_rect.x + item.width
        right_y = free_rect.y
        right_w = free_rect.width - item.width

        # horizontal split
        if split:
            top_w = free_rect.width
            right_h = item.height
        # vertical split
        else:
            top_w = item.width
            right_h = free_rect.height

        result = []
        tmp_stage = free_rect.stage
        tmp_split = free_rect.split
        if tmp_stage == 0:
            if right_w > 0 and right_h > 0:
                if split:
                    right_rect = FreeRectangle(right_w, right_h, right_x, right_y, tmp_stage + 1, tmp_split)
                else:
                    right_rect = FreeRectangle(right_w, right_h, right_x, right_y, tmp_stage, tmp_split)
                result.append(right_rect)

            if top_w > 0 and top_h > 0:
                if not split:
                    top_rect = FreeRectangle(top_w, top_h, top_x, top_y, tmp_stage + 1, tmp_split)
                else:
                    top_rect = FreeRectangle(top_w, top_h, top_x, top_y, tmp_stage, tmp_split)
                result.append(top_rect)

        elif tmp_stage == 1:
            if free_rect.split == 0:
                # vertical split
                top_w = item.width
                right_h = free_rect.height
                if top_w > 0 and top_h > 0:
                    top_rect = FreeRectangle(top_w, top_h, top_x, top_y, tmp_stage + 1, tmp_split)
                    result.append(top_rect)
                if right_w > 0 and right_h > 0:
                    right_rect = FreeRectangle(right_w, right_h, right_x, right_y, tmp_stage, tmp_split)
                    result.append(right_rect)
            else:
                # horizontal split
                top_w = free_rect.width
                right_h = item.height
                if top_w > 0 and top_h > 0:
                    top_rect = FreeRectangle(top_w, top_h, top_x, top_y, tmp_stage, tmp_split)
                    result.append(top_rect)
                if right_w > 0 and right_h > 0:
                    tmp_stage += 1
                    right_rect = FreeRectangle(right_w, right_h, right_x, right_y, tmp_stage, tmp_split)
                    result.append(right_rect)

        elif tmp_stage == 2:
            if free_rect.split == 1:
                # vertical split
                top_w = item.width
                right_h = free_rect.height
                if top_w > 0 and top_h > 0:
                    top_rect = FreeRectangle(top_w, top_h, top_x, top_y, tmp_stage + 1, tmp_split)
                    result.append(top_rect)
                if right_w > 0 and right_h > 0:
                    right_rect = FreeRectangle(right_w, right_h, right_x, right_y, tmp_stage, tmp_split)
                    result.append(right_rect)
            else:
                # horizontal split
                top_w = free_rect.width
                right_h = item.height
                if top_w > 0 and top_h > 0:
                    top_rect = FreeRectangle(top_w, top_h, top_x, top_y, tmp_stage, tmp_split)
                    result.append(top_rect)
                if right_w > 0 and right_h > 0:
                    tmp_stage += 1
                    right_rect = FreeRectangle(right_w, right_h, right_x, right_y, tmp_stage, tmp_split)
                    result.append(right_rect)
        return result

    def _split_free_rect(self, item: Item, free_rect: FreeRectangle) -> List[FreeRectangle]:
        """
        Determines the split axis based upon the split heuristic then calls
        _split_along_axis  with the appropriate axis to return a List[FreeRectangle].
        """
        # Leftover lengths
        w = free_rect.width - item.width
        h = free_rect.height - item.height

        if self.split_heuristic == 'SplitShorterLeftoverAxis':
            split = (w <= h)
        elif self.split_heuristic == 'SplitLongerLeftoverAxis':
            split = (w > h)
        elif self.split_heuristic == 'SplitMinimizeArea':
            split = (item.width * h > w * item.height)
        elif self.split_heuristic == 'SplitMaximizeArea':
            split = (item.width * h <= w * item.height)
        elif self.split_heuristic == 'SplitShorterAxis':
            split = (free_rect.width <= free_rect.height)
        elif self.split_heuristic == 'SplitLongerAxis':
            split = (free_rect.width > free_rect.height)
        elif self.split_heuristic == 'SplitSameAsPreviousAxis':
            split = True if free_rect.split == 0 else False
        else:
            split = True
        return self._split_along_axis(free_rect, item, split)

    def _add_item(self, item: Item, x: int, y: int, stage: int, rotate: bool = False) -> None:
        """ Helper method for adding items to the bin """
        if rotate:
            item.rotate()
        item.x, item.y, item.stage = x, y, stage
        self.items.append(item)
        self.free_area -= item.area

    def rectangle_merge(self) -> None:
        """
        Rectangle Merge optimization
        Finds pairs of free rectangles and merges them if they are mergable.
        """
        for free_rect in self.free_rects:
            widths_func = lambda r: (r.width == free_rect.width and
                                     r.x == free_rect.x and r != free_rect)
            matching_widths = list(filter(widths_func, self.free_rects))
            heights_func = lambda r: (r.height == free_rect.height and
                                      r.y == free_rect.y and r != free_rect)
            matching_heights = list(filter(heights_func, self.free_rects))
            if matching_widths:
                widths_adjacent = list(filter(lambda r: r.y == free_rect.y + free_rect.height, matching_widths))
                # type: List[FreeRectangle]

                if widths_adjacent:
                    match_rect = widths_adjacent[0]
                    merged_rect = FreeRectangle(free_rect.width,
                                                free_rect.height + match_rect.height,
                                                free_rect.x,
                                                free_rect.y,
                                                free_rect.stage,
                                                free_rect.split)
                    self.free_rects.remove(free_rect)
                    self.free_rects.remove(match_rect)
                    self.free_rects.add(merged_rect)

            if matching_heights:
                heights_adjacent = list(filter(lambda r: r.x == free_rect.x + free_rect.width, matching_heights))
                if heights_adjacent:
                    match_rect = heights_adjacent[0]
                    merged_rect = FreeRectangle(free_rect.width + match_rect.width,
                                                free_rect.height,
                                                free_rect.x,
                                                free_rect.y,
                                                free_rect.stage,
                                                free_rect.split)
                    self.free_rects.remove(free_rect)
                    self.free_rects.remove(match_rect)
                    self.free_rects.add(merged_rect)

    def _find_best_score(self, item: Item):
        rects = []
        for rect in self.free_rects:
            if self._item_fits_rect(item, rect):
                rects.append((self._score(rect, item), rect, False))
            if self.rotation and self._item_fits_rect(item, rect, rotation=True):
                rects.append((self._score(rect, item), rect, True))
        try:
            _score, rect, rot = min(rects, key=lambda x: x[0])
            return _score, rect, rot
        except ValueError:
            return None, None, False

    def insert(self, item: Item, heuristic: str = 'best_area') -> bool:
        """
        Add items to the bin. Public Method.
        """
        _, best_rect, rotated = self._find_best_score(item)
        if best_rect:
            self._add_item(item, best_rect.x, best_rect.y, best_rect.stage, rotated)
            self.free_rects.remove(best_rect)
            splits = self._split_free_rect(item, best_rect)
            for rect in splits:
                self.free_rects.add(rect)
            if self.rMerge:
                self.rectangle_merge()
            return True
        return False

    def bin_stats(self) -> dict:
        """
        Returns a dictionary with compiled stats on the bin tree
        """

        stats = {
            'width': self.x,
            'height': self.y,
            'area': self.area,
            'free_area': self.free_area,
            'efficiency': (self.area - self.free_area) / self.area,
            'items': self.items,
        }

        return stats


def score_baf(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Best Area Fit """
    return rect.area - item.area, min(rect.width - item.width, rect.height - item.height)


def score_bssf(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Best Short side Fit """
    return min(rect.width - item.width, rect.height - item.height), max(rect.width - item.width,
                                                                        rect.height - item.height)


def score_blsf(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Best Long side Fit """
    return max(rect.width - item.width, rect.height - item.height), min(rect.width - item.width,
                                                                        rect.height - item.height)


def score_waf(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Worst Area Fit """
    return (0 - (rect.area - item.area)), (0 - min(rect.width - item.width, rect.height - item.height))


def score_wssf(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Worst Short side Fit """
    return (0 - min(rect.width - item.width, rect.height - item.height)), \
           (0 - max(rect.width - item.width, rect.height - item.height))


def score_wlsf(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Worst Long side Fit """
    return (0 - max(rect.width - item.width, rect.height - item.height)), \
           (0 - min(rect.width - item.width, rect.height - item.height))
