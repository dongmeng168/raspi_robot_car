#coding:utf8
from random import random,choice
from copy import deepcopy
d1 = {0:0,90:1,180:2,270:3}

# # for key,value in d1.items():
# #     print(key,value)

# for i in range(40,100+1):
#     print(40+100-i)
d2 = deepcopy(d1)

print(d1)

d2[0] = 100

print(d1)