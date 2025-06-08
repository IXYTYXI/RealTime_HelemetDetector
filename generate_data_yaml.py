# -*- coding: utf-8 -*-
"""
Created on Sat Jun  7 07:45:43 2025

@author: IXYTY
生成 data.yaml
第四步生成 data.yaml 配置文件
"""

output_dir = r'D:\code\workspace\python\yolo\set\ds\yolo_dataset'

yaml_content = f"""train: {output_dir}\\images\\train
val: {output_dir}\\images\\val

nc: 2
names: ['helmet', 'head']
"""

with open(f'{output_dir}\\data.yaml', 'w') as f:
    f.write(yaml_content)