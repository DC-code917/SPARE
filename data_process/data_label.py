import numpy as np
import os
import json


white_files_path = './data/white/'  
black_files_path = './data/black/' 


data_MD52label = {}

for file in os.listdir(white_files_path):
    if file.endswith('.json'):
        md5 = file.split('.')[0]  
        data_MD52label[md5] = 'Benign'


for file in os.listdir(black_files_path):
    if file.endswith('.json'):
        md5 = file.split('.')[0]
        data_MD52label[md5] = 'Malware'


np.savez('data_MD52label.npz', data_MD52label=data_MD52label)


print('data_MD52label.npz has been saved.')


white_files = sorted(os.listdir(white_files_path))
black_files = sorted(os.listdir(black_files_path))



detection_train_md5_white = [file.split('.')[0] for file in white_files[:15000]]
detection_train_md5_black = [file.split('.')[0] for file in black_files[:15000]]
detection_train_md5 = detection_train_md5_white + detection_train_md5_black


detection_test_md5_white = [file.split('.')[0] for file in white_files[-5000:]]
detection_test_md5_black = [file.split('.')[0] for file in black_files[-5000:]]
detection_test_md5 = detection_test_md5_white + detection_test_md5_black


dataset_split_md5_list = {
    'detection_train_md5': detection_train_md5,
    'detection_test_md5': detection_test_md5,
}


np.savez('dataset_split_md5_list.npz', **dataset_split_md5_list)


print('dataset_split_md5_list.npz has been saved.')