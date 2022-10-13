# -*- coding: utf-8 -*-
"""
BinManager

The main program interface for the package. BinPack manages
creation and ranking of bins and returns layout dictionaries
for packed bins.

@author: MinhZou
@date: 2022-10-11
@e-mail: 770445973@qq.com
@refer from: https://github.com/solomon-b/greedypacker
"""
from typing import List, Union, Any
from utils import item
from . import guillotine


# Type Aliases:
Algorithm = Union[guillotine.Guillotine]


class BinManager:
    """
    Interface Class.
    """
    def __init__(self, bin_width: int = 8,
                 bin_height: int = 4,
                 bin_algo: str = 'bin_best_fit',
                 pack_algo: str = 'guillotine',
                 heuristic: str = 'default',
                 split_heuristic: str = 'default',
                 rotation: bool = True,
                 rectangle_merge: bool = True,
                 waste_map: bool = True,
                 sorting: bool = True,
                 sorting_heuristic: str = 'DESCA',
                 init_split: int = 0) -> None:
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.items = []  # type: List[item.Item]
        self.bin_count = 0
        self.bin_algo = bin_algo
        self.pack_algo = pack_algo
        self.heuristic = heuristic
        self.init_split = init_split

        if bin_algo == 'bin_best_fit':
            self.bin_sel_algo = self._bin_best_fit
        elif bin_algo == 'bin_first_fit':
            self.bin_sel_algo = self._bin_first_fit
        self.algorithm = pack_algo

        self.split_heuristic = split_heuristic
        self.sorting = sorting
        self.sorting_heuristic = sorting_heuristic
        self.rotation = rotation
        self.rectangle_merge = rectangle_merge
        self.waste_map = waste_map

        default_bin = self._bin_factory()
        self.bins = [default_bin]

    def items_sort(self): 
        # By Area Ascending
        if self.sorting_heuristic == 'ASCA':
            key = lambda el: el.width*el.height
            self.items.sort(key=key, reverse=False)
        # By Area Descending
        elif self.sorting_heuristic == 'DESCA':
            key = lambda el: el.width*el.height
            self.items.sort(key=key, reverse=True)
        # By Shorter Side Ascending
        elif self.sorting_heuristic == 'ASCSS':
            key = lambda el: el.width if el.width < el.height else el.height
            self.items.sort(key=key, reverse=False)
        # By Shorter Side Descending
        elif self.sorting_heuristic == 'DESCSS':
            key = lambda el: el.width if el.width < el.height else el.height
            self.items.sort(key=key, reverse=True)
        # By Longer Side Ascending
        elif self.sorting_heuristic == 'ASCLS':
            key = lambda el: el.width if el.width > el.height else el.height
            self.items.sort(key=key, reverse=False)
        # By Longer Side Descending
        elif self.sorting_heuristic == 'DESCLS':
            key = lambda el: el.width if el.width > el.height else el.height
            self.items.sort(key=key, reverse=True)
        # By Perimiter Ascending
        elif self.sorting_heuristic == 'ASCPERIM':
            key = lambda el: (2*el.width)+(2*el.height)
            self.items.sort(key=key, reverse=False)
        # By Perimiter Descending
        elif self.sorting_heuristic == 'DESCPERIM':
            key = lambda el: (2*el.width)+(2*el.height)
            self.items.sort(key=key, reverse=True)
        # By Difference in Side Length Ascending
        elif self.sorting_heuristic == 'ASCDIFF':
            key = lambda el: abs(el.width-el.height)
            self.items.sort(key=key, reverse=False)
        # By Difference in Side Length Descending
        elif self.sorting_heuristic == 'DESCDIFF':
            key = lambda el: abs(el.width-el.height)
            self.items.sort(key=key, reverse=True)
        # By Side Ratio Ascending
        elif self.sorting_heuristic == 'ASCRATIO':
            key = lambda el: el.width/el.height
            self.items.sort(key=key, reverse=False)
        # By Side Ratio Descending
        elif self.sorting_heuristic == 'DESCRATIO':
            key = lambda el: el.width/el.height
            self.items.sort(key=key, reverse=True)
        # Default to DESCA
        else:
            key = lambda el: el.width*el.height
            self.items.sort(key=key, reverse=True)

    def add_items(self, *items: item.Item) -> None:
        for item in items:
            self.items.append(item)
        if self.sorting:
            self.items_sort()

    def _bin_factory(self) -> Any:
        """
        Returns a bin with the specificed algorithm,
        heuristic, and dimensions
        """
        if self.algorithm == 'guillotine':
            return guillotine.Guillotine(self.bin_width, self.bin_height, self.rotation, self.heuristic,
                                         self.rectangle_merge, self.split_heuristic, self.init_split)
        raise ValueError('Error: No such Algorithm')

    def _bin_first_fit(self, item: item.Item) -> None:
        """
        Insert into the first bin that fits the item
        """
        result = False
        for binn in self.bins:
            result = binn.insert(item, self.heuristic)
            if result:
                break
        if not result:
            self.bins.append(self._bin_factory())
            self.bins[-1].insert(item, self.heuristic)

    def _bin_best_fit(self, item: item.Item) -> bool:
        """
        Insert into the bin that best fits the item
        """
        # Ensure item can theoretically fit the bin
        item_fits = False
        if item.width <= self.bin_width and item.height <= self.bin_height:
            item_fits = True
        if self.rotation and (item.height <= self.bin_width and item.width <= self.bin_height):
            item_fits = True
        if not item_fits:
            raise ValueError("Error! item too big for bin")

        scores = []
        for binn in self.bins:
            s, _, _ = binn._find_best_score(item)[:3]
            if s is not None:
                scores.append((s, binn))
        if scores:
            _, best_bin = min(scores, key=lambda x: x[0])
            return best_bin.insert(item)

        new_bin = self._bin_factory()
        new_bin.insert(item, self.heuristic)
        self.bins.append(new_bin)
        return True

    def execute(self) -> None:
        """
        Loop over all items and attempt insertion
        """
        for ite in self.items:
            self.bin_sel_algo(ite)
