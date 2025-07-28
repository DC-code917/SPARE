#!/usr/bin/env python
# coding: utf-8
# code
# In[2]:


import numpy as np
import os
import torch
from torch_geometric.data import Data, DataLoader, Dataset

# In[3]:




data_MD52label = np.load('data_MD52label.npz', allow_pickle=True)
data_MD52label = data_MD52label['data_MD52label'][()]

dataset_split_md5_list = np.load('dataset_split_md5_list.npz', allow_pickle=True)
detection_train_md5 = dataset_split_md5_list['detection_train_md5']
detection_test_md5 = dataset_split_md5_list['detection_test_md5']



# In[7]:


# def loadnpz(md5):
#     graph = np.load('./data/graph/' + md5 + '_graph.npz', allow_pickle=True)
#     node_feature = graph['node_feature']
#     edge_set = graph['edge_set']
#     edge_label = graph['edge_label']
#     d = Data()
#     d.x = torch.tensor(node_feature)
#     d.edge_type = torch.tensor(edge_label)
#     d.edge_index = torch.tensor(edge_set).T
#     return d

def loadnpz(md5):
    try:
        graph = np.load('./data/graph/' + md5 + '_graph.npz', allow_pickle=True)
        node_feature = graph['node_feature']
        edge_set = graph['edge_set']
        edge_label = graph['edge_label']
        d = Data()
        d.x = torch.tensor(node_feature)
        d.edge_type = torch.tensor(edge_label)
        d.edge_index = torch.tensor(edge_set).T
        return d
    except FileNotFoundError:
        print(f"File for {md5} not found. Skipping.")
        return None
# In[11]:


datalist_detection_train = []
datalist_detection_test = []

num = 1
for md5 in list(data_MD52label.keys()):
    print('{} / {}'.format(num, len(data_MD52label)))
    num += 1
    data = loadnpz(md5)
    if data is None:  # 检查data是否为None
        continue  # 如果是None，则跳过当前循环的剩余部分
    if data_MD52label[md5] == 'Benign':
        data.y = torch.tensor([0])
        if md5 in detection_train_md5:
            datalist_detection_train.append(data)
        else:
            datalist_detection_test.append(data)
    else:
        data.y = torch.tensor([1])
        if md5 in detection_train_md5:
            datalist_detection_train.append(data)
        else:
            datalist_detection_test.append(data)

# In[13]:


torch.save(datalist_detection_train, './data/datalist_detection_train.pt')
torch.save(datalist_detection_test, './data/datalist_detection_test.pt')


# In[ ]:
