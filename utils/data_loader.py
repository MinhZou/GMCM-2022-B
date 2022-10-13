# -*- coding: utf-8 -*-
"""
@author: MinhZou
@date: 2022-10-11
@e-mail: 770445973@qq.com
"""

import pandas as pd
import algo as g
import collections
from collections import Counter
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans

from utils.save_results import save_material_order_info
from algo.conditional_dbscan import ConditionalDbscan


def load_data(name, idx):
    '''
    load data as fixed format.
    '''
    items = []
    data = pd.read_csv('data/{}/data{}{}.csv'.format(str(name), str(name), str(idx)))
    row_num = len(data)
    for i in range(row_num):
        id = int(data.iloc[i, 0])
        x = 0
        y = 0
        width = int(data.iloc[i, 3])
        height = int(data.iloc[i, 4])
        num = int(data.iloc[i, 2])
        material = data.iloc[i, 1]
        order = int(data.iloc[i, 5][5:])
        # rect['rotatable'] = True
        items.append(g.Item(id, width, height, (x, y), material=material, order=order, num=num))
    return items


def data_batched(name, idx):
    max_item_num = 1000
    max_item_area = 250 * 1000000
    batch_data = collections.defaultdict(list)
    # data_path = '../data/{}/data{}{}.csv'.format(str(name), str(name), str(idx))
    data_path = 'data/{}/data{}{}.csv'.format(str(name), str(name), str(idx))
    data = pd.read_csv(data_path)
    order_count = Counter(data['item_order'])

    sorted_order_count = dict(sorted(dict(order_count).items(), key=lambda x: x[1], reverse=True))
    batch_info = {}
    batch = 0

    def generate_new_batch_info(batch_info, batch):
        it = {'batch_num': 0, 'batch_area': 0}
        batch_info[batch] = it
        return

    generate_new_batch_info(batch_info, batch)
    material_dic = collections.defaultdict(list)
    for i, item in enumerate(sorted_order_count.items()):
        order_data = data.loc[data['item_order'] == (str(item[0]))]
        order_area = (order_data['item_length'] * order_data['item_length']).sum()
        order_num = order_data['item_num'].sum()
        if batch_info[batch]['batch_num'] + order_num < max_item_num and \
                batch_info[batch]['batch_area'] + order_area < max_item_area:
            batch_info[batch]['batch_num'] += order_num
            batch_info[batch]['batch_area'] += order_area
        else:
            batch_data[batch].append(material_dic)
            batch += 1
            generate_new_batch_info(batch_info, batch)
            batch_info[batch]['batch_num'] += order_num
            batch_info[batch]['batch_area'] += order_area
            material_dic = collections.defaultdict(list)

        for j in range(len(order_data)):
            idx = int(order_data.iloc[j, 0])
            x, y = 0, 0
            width = int(order_data.iloc[j, 3])
            height = int(order_data.iloc[j, 4])
            num = int(order_data.iloc[j, 2])
            material = order_data.iloc[j, 1]
            order = int(order_data.iloc[j, 5][5:])
            material_dic[material].append(g.Item(idx, width, height, (x, y), material=material, order=order, num=num))
    batch_data[batch].append(material_dic)
    return batch_data, batch_info


def data_batched_cluster(name, idx):
    max_item_num = 1000
    max_item_area = 250 * 1000000
    data_path = 'data/{}/data{}{}.csv'.format(str(name), str(name), str(idx))
    # data_path = '../data/{}/data{}{}.csv'.format(str(name), str(name), str(idx))
    data = pd.read_csv(data_path)
    material_order, order_info = save_material_order_info(data_path, name, idx)
    order_info = np.array(order_info)
    x = np.array(material_order)[:, 1:]
    X = normalize(x, axis=1, norm='l2')  # 'max' # l1 0.5
    # X = np.where(x > 0, 1, 0)

    # model = DBSCAN(eps=1, min_samples=1)
    # model.fit(X)
    # # print(model.labels_)
    # # print(np.unique(model.labels_))
    # y_pred = model.labels_

    num_cluster = 80
    max_iteration = 1000
    model = KMeans(n_clusters=num_cluster, max_iter=max_iteration, verbose=False)
    y_pred = model.fit_predict(X)
    batch_info = {}
    for i in range(len(y_pred)):
        batch_id = y_pred[i]
        if batch_id in batch_info:
            batch_info[batch_id]['batch_num'] += order_info[i, 2]
            batch_info[batch_id]['batch_area'] += order_info[i, 1]
            batch_info[batch_id]['orders'].append(order_info[i, 0])
        else:
            it = {'batch_num': 0, 'batch_area': 0, 'orders': []}
            batch_info[batch_id] = it
            batch_info[batch_id]['batch_num'] = order_info[i, 2]
            batch_info[batch_id]['batch_area'] += order_info[i, 1]
            batch_info[batch_id]['orders'].append(order_info[i, 0])

    # print(batch_info)
    for i in range(len(batch_info)):
        if batch_info[i]['batch_num'] > max_item_num or batch_info[i]['batch_area'] > max_item_area:
            print(batch_info[i])

    batch_data = collections.defaultdict(list)
    for batch_item in batch_info.items():
        batch = batch_item[0]
        batch_orders = batch_item[1]['orders']
        material_dic = collections.defaultdict(list)
        for i, item in enumerate(batch_orders):
            order_data = data.loc[data['item_order'] == item]
            # batch_data[batch].append(material_dic)
            # material_dic = collections.defaultdict(list)
            for j in range(len(order_data)):
                idx = int(order_data.iloc[j, 0])
                x = 0
                y = 0
                width = int(order_data.iloc[j, 3])
                height = int(order_data.iloc[j, 4])
                num = int(order_data.iloc[j, 2])
                material = order_data.iloc[j, 1]
                order = int(order_data.iloc[j, 5][5:])
                material_dic[material].append(
                    g.Item(idx, width, height, (x, y), material=material, order=order, num=num))
        batch_data[batch].append(material_dic)
    return batch_data, batch_info


def data_batched_conditional_dbscan(name, idx):
    max_item_num = 1000
    max_item_area = 250 * 1000000
    data_path = 'data/{}/data{}{}.csv'.format(str(name), str(name), str(idx))
    data = pd.read_csv(data_path)
    material_order, order_info = save_material_order_info(data_path, name, idx)
    order_info = np.array(order_info)
    x = np.array(material_order)[:, 1:]

    # X = x / x.max(axis=1)
    x = np.where(x > 0, 1, 0)
    X = normalize(x, axis=1, norm='l2')  # 'max' # l1 0.5
    # X = np.where(x > 0, 1, 0)
    min_points = 1
    eps = 1
    batch_pred = ConditionalDbscan(X, order_info, eps, min_points, max_item_num, max_item_area).conditional_dbscan()
    batch_info = {}
    for i in range(len(batch_pred)):
        batch_id = batch_pred[i]
        if batch_id in batch_info:
            batch_info[batch_id]['batch_num'] += order_info[i, 2]
            batch_info[batch_id]['batch_area'] += order_info[i, 1]
            batch_info[batch_id]['orders'].append(order_info[i, 0])
        else:
            it = {'batch_num': 0, 'batch_area': 0, 'orders': []}
            batch_info[batch_id] = it
            batch_info[batch_id]['batch_num'] = order_info[i, 2]
            batch_info[batch_id]['batch_area'] += order_info[i, 1]
            batch_info[batch_id]['orders'].append(order_info[i, 0])

    for i in range(len(batch_info)):
        if batch_info[i]['batch_num'] > max_item_num or batch_info[i]['batch_area'] > max_item_area:
            print(batch_info[i])

    batch_data = collections.defaultdict(list)
    for batch_item in batch_info.items():
        batch = batch_item[0]
        batch_orders = batch_item[1]['orders']
        material_dic = collections.defaultdict(list)
        for i, item in enumerate(batch_orders):
            order_data = data.loc[data['item_order'] == item]
            for j in range(len(order_data)):
                id = int(order_data.iloc[j, 0])
                x = 0
                y = 0
                width = int(order_data.iloc[j, 3])
                height = int(order_data.iloc[j, 4])
                num = int(order_data.iloc[j, 2])
                material = order_data.iloc[j, 1]
                order = int(order_data.iloc[j, 5][5:])
                material_dic[material].append(
                    g.Item(id, width, height, (x, y), material=material, order=order, num=num))
        batch_data[batch].append(material_dic)
    return batch_data, batch_info


# if __name__ == '__main__':
#     data_batched_cluster('B', 1)