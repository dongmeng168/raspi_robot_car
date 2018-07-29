#!/usr/bin/python  
# -*- coding: utf-8 -*-  

#author: moden 
#date: 2018-07-12 
#function: 获取自己的外网IP，并且发送到指定邮箱


import os
import smtplib  
import sqlite3
import time

def Add_IP(myip,now_date):
    """
    在指定的数据库中加入myip这个IP地址
    如果数据库中存在myip这个IP地址就不加入，并且函数返回 0
    不存则加入这个IP地址到数据库，并且函数返回 1
    """
    conn = sqlite3.connect('/mnt/Black_16G/share_pi/project/get_ip/all_ip.db')
    c = conn.cursor()
    c.execute("CREATE TABLE  if not exists out_IP (id integer primary key autoincrement,ip_addr char(16),add_date char(11),add_num int default 0)")

    c.execute('SELECT add_num FROM out_IP where ip_addr=? and add_date=?',(myip,now_date))
    all_num = c.fetchone()
    
    # print(all_num)

    if all_num:
        # print("today IP in database")
        add_num = all_num[0]
        # print(add_num)
        c.execute('update out_IP set add_num=? where ip_addr=? and add_date=?',(add_num+1,myip,now_date))
        conn.commit()
        return 0
    else:
        c.execute('INSERT INTO out_IP (ip_addr,add_date) VALUES (?,?)',(myip,now_date))
        conn.commit()
        # print("insert today IP to database",myip,now_date)
        return 1
    conn.close()

def GetOuterIP():
    """
    获得外网的IP地址
    """
    # curl的-s选项阻止显示下载信息
    message = os.popen('curl -s members.3322.org/dyndns/getip').readlines()
    out_IP = message[0].strip('\n')
    return out_IP

def sendMail(body):  
    """
    发送邮件到指定的邮箱
    """
    smtp_server = 'smtp.126.com'  
    from_mail = 'dm_126@126.com'  
    mail_pass = 'dmlove400'  
    to_mail = ['19921406014@189.cn']
    # cc_mail = ['410832962@qq.com']  
    from_name = 'dm_126'   
    # subject = u'Raspberry_Internet_IP'.encode('gbk')   # 以gbk编码发送，一般邮件客户端都能识别  
    subject = time.strftime('%Y-%m-%d',time.localtime()) + ' Raspberry_Internet_IP'
#     msg = '''\  
# From: %s <%s>  
# To: %s  
# Subject: %s  
# %s''' %(from_name, from_mail, to_mail_str, subject, body)  # 这种方式必须将邮件头信息靠左，也就是每行开头不能用空格，否则报SMTP 554  
    mail = [  
        "From: %s <%s>" % (from_name, from_mail),  
        "To: %s" % ','.join(to_mail),   # 转成字符串，以逗号分隔元素  
        "Subject: %s" % subject,  
        # "Cc: %s" % ','.join(cc_mail),  
        "",  
        body  
        ]  
    msg = '\n'.join(mail)  # 这种方式先将头信息放到列表中，然后用join拼接，并以换行符分隔元素，结果就是和上面注释一样了  
    try:  
        s = smtplib.SMTP()  
        s.connect(smtp_server, '25')  
        # print("connect ok")
        s.login(from_mail, mail_pass)  
        # print("login ok")
        s.sendmail(from_mail, to_mail, msg)     
        # s.sendmail(from_mail, to_mail+cc_mail, msg)    
        s.quit()  
        # print("sendmail ok")
    except smtplib.SMTPException as e:  
        print("Error: %s" %e)

if __name__ == '__main__':
    """
    获得IP地址后，Add_IP函数如果返回1,则数据库中不存在新获得的
    """
    MyIP = GetOuterIP()
    now_date = time.strftime('%Y-%m-%d',time.localtime())

    # MyIP = r'60.252.111.18'
    # now_date = r'2015-05-15'
    

    add_result = Add_IP(MyIP,now_date)
    # print(add_result)

    if add_result == 1:
        sendMail(now_date + " Raspberry IP is " + MyIP)
