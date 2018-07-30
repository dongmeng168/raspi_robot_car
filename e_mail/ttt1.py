#coding:utf8
import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from email import message_from_string

import mimetypes
import datetime

import quopri
import base64

import logging

def decode_chinese(str_mine_ch):
    str_list = str_mine_ch.split('?')
    if len(str_list) < 3:
        return str_mine_ch

    print(str_list)
    print(str_mine_ch)

    charset = str_list[1]
    code_method = str_list[2]
    str_ch = str_list[3]

    if code_method == 'B':
        str_ch_code = str(base64.b64decode(str_ch),encoding =charset)
    elif code_method == 'Q':
        str_ch_code = str(quopri.decodestring(str_ch),encoding =charset)
    else:
        str_ch_code = str_ch
    return str_ch_code


aa = decode_chinese('dd22.txt')
# aa = decode_chinese('=?GBK?Q?unix=B4=AB=C6=E62.txt?=')
print(aa)
