#!/usr/bin/python  
# -*- coding: utf-8 -*-  
import sqlite3

def Add_IP(myip):
    conn = sqlite3.connect('/mnt/Black_16G/share_pi/project/get_ip/all_ip.db')
    c = conn.cursor()
    # c.execute("CREATE TABLE out_IP (id integer primary key autoincrement,ip_addr char(16))")

    c.execute('SELECT * FROM out_IP where ip_addr=?',(myip,))
    all_ip = c.fetchall()
    # print(all_ip)

    if all_ip:
            print("IP in database")
            return 0
    else:
        c.execute("INSERT INTO out_IP VALUES (NULL,?)",(myip,))
        print("insert to database")

    conn.commit()
    conn.close()


def Show_IP():
    conn = sqlite3.connect('/mnt/Black_16G/share_pi/project/get_ip/all_ip.db')
    c = conn.cursor()

    c.execute('SELECT * FROM out_IP')
    all = c.fetchall()
    print("this is Show_IP")
    for one in all:
        print(one)

    conn.close()



if __name__ == '__main__':
    # Show_IP()
    # Add_IP("192.168.1.3")
    Show_IP()