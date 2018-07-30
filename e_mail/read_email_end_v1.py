#coding:utf8
#author : dongmeng
#CreateDate : 2018-07-29
import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from email import message_from_string

import mimetypes
import datetime

import quopri
import base64

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
    
    def decode_chinese(self,str_mine_ch):
        str_list = str_mine_ch.split('?')
        if len(str_list) < 3:
            return str_mine_ch
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


    #递归打印信息
    def parseMeassage(self,message=None):
        if self.msg:
            message = self.msg
        else:
            print("get nothing")
            exit(2)
        maintype = message.get_content_maintype()
        content_type = message.get_content_type()

        if maintype == 'multipart':
            parts = message.get_payload()

            for n, part in enumerate(parts):
                self.parseMeassage(part)

        # elif maintype == 'text/plain' or maintype == 'text/html':
        elif maintype == 'text':
            mail_content = message.get_payload(decode=True).strip()
            charset = self.guess_charset(message)
            if charset:
                mail_content = mail_content.decode(charset)
            if content_type == 'text/plain':
                self.msg_body = mail_content.decode('utf8')
            if content_type == 'text/html':
                print('Html: %s' % str(mail_content))
        else:
            print('Attachment: %s' % maintype) 

    def parseMessageWalk(self,message=None):
        if not message:
            if self.msg :
                message = self.msg
            else:
                print('no message to parde, exit code 2')
                exit(2)
        counter = 1
        for part in message.walk():
            # multipart/* are just containers
            if part.get_content_maintype() == 'multipart':
                continue
            # Applications should really sanitize the given filename so that an
            # email message can't be used to overwrite important files
            filename = part.get_filename()
            if filename:
                filename = self.decode_chinese(filename)
            else:
                ext = mimetypes.guess_extension(part.get_content_type())
                if not ext:
                    # Use a generic bag-of-bits extension
                    ext = '.bin'
                filename = 'part-%03d%s' % (counter, ext)
            
            print('filename===',filename,counter)
            counter += 1
            # with open(os.path.join(args.directory, filename), 'wb') as fp:
            #     fp.write(part.get_payload(decode=True))



mye1 =MyEmail()

date_now = datetime.datetime.now().strftime("%d %b %Y")
part_subject = 'Raspberry_Internet_IP'
# mye1.parseMails(date_now,part_subject)
mye1.parseMails('30 Jul 2018','带文本附件，带MP3附件')

# print(mye1.mails_head_list)

mye1.parseMessageWalk()

# mye1.parseMeassage()
# print(mye1.msg_body)

