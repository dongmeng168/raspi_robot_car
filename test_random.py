#coding:utf8
from random import random,choice
from copy import deepcopy,copy

angle_status_dict = {0:1,90:1,180:1,270:1}
angle_list = []

print(angle_status_dict)

for key,value in angle_status_dict.items():
    if value == 1:
        angle_list.append(angle_status_dict[key]) 
# 如果角度列表为空，表示被围着了，应该停止

print(angle_list)

if not angle_list:
    print("angle_list call stop")