# -*- coding: utf-8 -*-
"""
@author: MinhZou
@date: 2022-10-11
@e-mail: 770445973@qq.com
"""

import csv
import unicodecsv
import os
import pandas as pd

from utils.path import mkdir_or_exist


def save_material_order_info(data_path, name, idx):
    data = pd.read_csv(data_path)
    # data = pd.read_csv('data/{}/data{}{}.csv'.format(str(name), str(name), str(idx)))
    material_header = ['item_order'] + list(data['item_material'].unique())
    material_order = []
    order_header = list(data['item_order'].unique())
    file_name = os.path.split(data_path)[0] + '/material_order_{}{}.csv'.format(str(name), str(idx))
    if not os.path.exists(file_name):
        for item in order_header:
            order_data = data.loc[data['item_order'] == item]
            tmp_m_order = [item]
            for m in material_header[1:]:
                m_count = len(order_data.loc[order_data['item_material'] == m])
                tmp_m_order.append(m_count)
            material_order.append(tmp_m_order)

        with open(file_name, 'a', encoding='utf-8', newline='') as fp:
            writer = csv.writer(fp)
            writer.writerow(material_header)
            writer.writerows(material_order)

    material_order = pd.read_csv(file_name)

    header = ['item_order', 'order_area', 'order_num']
    order_info = []
    order_info_file_name = os.path.split(data_path)[0] + '/order_info_{}{}.csv'.format(str(name), str(idx))
    if not os.path.exists(order_info_file_name):
        for item in order_header:
            order_data = data.loc[data['item_order'] == item]
            order_area = (order_data['item_width'] * order_data['item_length']).sum()
            order_num = order_data['item_num'].sum()
            tmp_info = [item, order_area, order_num]
            order_info.append(tmp_info)

        with open(order_info_file_name, 'a', encoding='utf-8', newline='') as fp:
            writer = csv.writer(fp)
            writer.writerow(header)
            writer.writerows(order_info)

    order_info = pd.read_csv(order_info_file_name)

    return material_order, order_info


def save_to_cut_program(raw_id, bins, path):
    mkdir_or_exist(path)
    file_name = path + '/cut_program.csv'
    header = ['原片材质', '原片序号', '产品id', '产品x坐标', '产品y坐标', '产品x方向长度', '产品y方向长度']
    data = []
    for rect in bins:
        tmp = [rect.material, raw_id, rect.idx, rect.x, rect.y, rect.width, rect.height]
        data.append(tmp)

    if not os.path.exists(file_name):
        fp = open(file_name, 'wb')
        w_fp = unicodecsv.writer(fp, encoding='utf-8-sig')
        w_fp.writerow(header)
        fp.close()
    with open(file_name, 'a', encoding='utf-8', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerows(data)


def save_to_sum_order(batch_id, raw_id, bins, path):
    mkdir_or_exist(path)
    file_name = path + '/sum_order.csv'
    header = ['批次序号', '原片材质', '原片序号', '产品id', '产品x坐标', '产品y坐标', '产品x方向长度', '产品y方向长度']
    data = []
    for rect in bins:
        tmp = [batch_id, rect.material, raw_id, rect.idx, rect.x, rect.y, rect.width, rect.height]
        data.append(tmp)

    if not os.path.exists(file_name):
        fp = open(file_name, 'wb')
        w_fp = unicodecsv.writer(fp, encoding='utf-8-sig')
        w_fp.writerow(header)
        fp.close()

    with open(file_name, 'a', encoding='utf-8', newline='') as fp:
        writer = csv.writer(fp)
        writer.writerows(data)


def save_efficiency(data, path):
    mkdir_or_exist(path)
    file_name = path + '/result.txt'
    with open(file_name, 'w') as f:
        f.write(data)