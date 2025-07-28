import numpy as np
import os
import json

# 定义良性文件和恶意软件文件的路径
white_files_path = './data/white/'  # 良性文件所在路径
black_files_path = './data/black/'  # 恶意软件文件所在路径

# 初始化MD5到标签的映射字典
data_MD52label = {}

# 为良性文件添加标签
for file in os.listdir(white_files_path):
    if file.endswith('.json'):
        md5 = file.split('.')[0]  # 假设文件名格式为MD5.json
        data_MD52label[md5] = 'Benign'

# 为恶意软件文件添加标签
for file in os.listdir(black_files_path):
    if file.endswith('.json'):
        md5 = file.split('.')[0]
        data_MD52label[md5] = 'Malware'

# 保存到npz文件
np.savez('data_MD52label.npz', data_MD52label=data_MD52label)

# 输出文件路径提示
print('data_MD52label.npz has been saved.')


white_files = sorted(os.listdir(white_files_path))
black_files = sorted(os.listdir(black_files_path))


# 从每个列表中分别取前15000个文件名作为训练数据
detection_train_md5_white = [file.split('.')[0] for file in white_files[:15000]]
detection_train_md5_black = [file.split('.')[0] for file in black_files[:15000]]
detection_train_md5 = detection_train_md5_white + detection_train_md5_black

# 从每个列表中分别取后5000个文件名作为测试数据
detection_test_md5_white = [file.split('.')[0] for file in white_files[-5000:]]
detection_test_md5_black = [file.split('.')[0] for file in black_files[-5000:]]
detection_test_md5 = detection_test_md5_white + detection_test_md5_black

# 创建dataset_split_md5_list字典
dataset_split_md5_list = {
    'detection_train_md5': detection_train_md5,
    'detection_test_md5': detection_test_md5,
}

# 保存到npz文件
np.savez('dataset_split_md5_list.npz', **dataset_split_md5_list)

# 输出保存成功的消息
print('dataset_split_md5_list.npz has been saved.')