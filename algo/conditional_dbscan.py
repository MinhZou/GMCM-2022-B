# -*- coding: utf-8 -*-
"""
Implemented based on "Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise"
Martin Ester, Hans-Peter Kriegel, Jörg Sander, Xiaowei Xu

conditional_dbscan: "density based spatial clustering of applications with nosie(dbscan)" with additional constraint
@author: MinhZou
@date: 2022-10-11
@e-mail: 770445973@qq.com
"""

import numpy as np
import math
import random


class ConditionalDbscan:
    def __init__(self, data, data_info, eps, min_points, max_item_num, max_item_area):
        assert type(data) == np.ndarray
        self.num_points = data.shape[0]
        self.data = data
        self.data_info = data_info
        self.eps = eps
        self.min_points = min_points
        self.max_item_num = max_item_num
        self.max_item_area = max_item_area
        self.cluster_info = {}
        self.cluster_pred = [-1 for _ in range(self.num_points)]

    @staticmethod
    def distance(point_a, point_b):
        return math.sqrt(np.power(point_a - point_b, 2).sum())
        # return math.sqrt(np.absolute(point_a - point_b).sum())

    def generate_new_cluster_info(self, idx):
        it = {'batch_num': 0, 'batch_area': 0}
        self.cluster_info[idx] = it

    def add_cluster_info(self, idx, point):
        self.cluster_info[idx]['batch_num'] += self.data_info[point, 2]
        self.cluster_info[idx]['batch_area'] += self.data_info[point, 1]

    def conditional_dbscan(self):
        # np.random.seed(10)
        unvisited_points = [i for i in range(self.num_points)]
        visited_points = []
        idx = -1
        new_point = -1
        while len(unvisited_points) > 0:
            # curr_point = random.choice(unvisited_points)
            # curr_point could be chose randomly, here to obtain similar neighbors when the constraint is unsatisfied,
            # we choose the first one in unvisited points.
            if new_point != -1 and new_point in unvisited_points:  # and new_point in unvisited_points
                curr_point = new_point
            else:
                curr_point = random.choice(unvisited_points)
                # curr_point = unvisited_points[0]
            # curr_point = unvisited_points[0]
            # curr_point = random.choice(unvisited_points)
            unvisited_points.remove(curr_point)
            visited_points.append(curr_point)
            neighborhoods = []
            for i in range(self.num_points):
                if self.distance(self.data[i, :], self.data[curr_point, :]) <= self.eps:
                    neighborhoods.append(i)
            if len(neighborhoods) >= self.min_points:
                idx = idx + 1
                self.generate_new_cluster_info(idx)
                self.cluster_pred[curr_point] = idx
                self.add_cluster_info(idx, curr_point)
                for next_neighbor_point in neighborhoods:
                    if next_neighbor_point in unvisited_points:
                        if self.cluster_info[idx]['batch_num'] + self.data_info[next_neighbor_point, 2] > \
                                self.max_item_num or self.cluster_info[idx]['batch_area'] + \
                                self.data_info[next_neighbor_point, 1] > self.max_item_area:
                            new_point = next_neighbor_point
                            break
                        unvisited_points.remove(next_neighbor_point)
                        visited_points.append(next_neighbor_point)
                        new_neighborhoods = []
                        for j in range(self.num_points):
                            if self.distance(self.data[j, :], self.data[next_neighbor_point, :]) <= self.eps:
                                new_neighborhoods.append(j)
                        if len(new_neighborhoods) >= self.min_points:
                            for new_next_neighbor_point in new_neighborhoods:
                                if new_next_neighbor_point not in neighborhoods:
                                    neighborhoods.append(new_next_neighbor_point)
                    if self.cluster_pred[next_neighbor_point] == -1:
                        self.cluster_pred[next_neighbor_point] = idx
                        self.add_cluster_info(idx, next_neighbor_point)
            else:
                idx = idx + 1
                self.generate_new_cluster_info(idx)
                self.cluster_pred[curr_point] = idx
                self.add_cluster_info(idx, curr_point)
                # # or
                # self.cluster_pred[curr_point] = -1
        return self.cluster_pred
