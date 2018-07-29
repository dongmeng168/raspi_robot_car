#coding:utf8
#author : dongmeng
#CreateDate : 2018-07-29
import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from email import message_from_string



class MyEmail(object):
    """docstring for MyEmail"""
    def __init__(self):
        self.my_email = '19921406014'
        self.password = 'dm_126@126.com'
        # self.pop3_server = 'imap.189.cn'
        self.pop3_server = 'pop.189.cn'

        self.setup()        

    def setup(self):
        self.server = poplib.POP3(self.pop3_server)
        self.server.set_debuglevel(0)
        self.welcome_info = self.server.getwelcome().decode('utf-8')
        self.server.user(self.my_email)
        self.server.pass_(self.password) 
        print('login ok')
    def parseMails(self,mail_Date=None,mail_Subject=None):
        #打印邮件数量和占用空间
        (self.mails_num,self.mails_size) = self.server.stat()
        resp, mails, octets = self.server.list()
        #解析邮件
        index = len(mails)
        self.mails_head_list = []
        self.msg = None
        for mail_index in range(1,index+1):
            head_info_dict = {}       
            resp, lines, octets = self.server.retr(mail_index)
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = message_from_string(msg_content)        
            for header in 'From', 'To', 'Subject', 'Date':
                if header in msg:
                    head_info_dict[header] = self.decode_str(msg[header])
            if (mail_Subject in  head_info_dict['Subject']) and (mail_Date in head_info_dict['Date']):
                self.msg = msg
            self.mails_head_list.append(head_info_dict)

    #这是检测编码部分，有点不懂
    def guess_charset(self,msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset
    #这里只取出第一发件人
    def decode_str(self,s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value
 
    #递归打印信息
    def parseMeassage(self, message=None ,indent = 0):
        if self.msg:
            message = self.msg
        maintype = message.get_content_maintype()
        content_type = message.get_content_type()

        if maintype == 'multipart':
            parts = message.get_payload()

            for n, part in enumerate(parts):
                print('%spart %s' % ('  '*indent, n))
                print('%s--------------------' % ('   '*indent))
                self.parseMeassage(part, indent + 1)

        # elif maintype == 'text/plain' or maintype == 'text/html':
        elif maintype == 'text':
            mail_content = message.get_payload(decode=True).strip()
            charset = self.guess_charset(message)
            if charset:
                mail_content = mail_content.decode(charset)
            if content_type == 'text/plain':
                self.msg_body = mail_content.decode('utf8')
                # self.msg_body = str(mail_content)
                # print('%sText: %s' % ('  '*indent, str(mail_content) + '...'))
            if content_type == 'text/html':
                print('%sHtml: %s' % ('  '*indent, str(mail_content) + '...'))
        else:
            print('%sAttachment: %s' % ('  '*indent, maintype)) 


mye1 =MyEmail()

# mye1.parseMails('29 Jul 2018','测试')
mye1.parseMails('28 Jul 2018','Raspberry_Internet_IP')


mye1.parseMeassage()
print(mye1.msg_body)