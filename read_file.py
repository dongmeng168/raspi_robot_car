# import os
# file_object = open('hosts','rU')
# try:
#     for line in file_object:
#          # do_somthing_with(line)//line带"\n"
#          new_ip = "12.30.4.99"
#          if line.find("lemon.com") >= 0 :
#             line = "how are you"
#          # print(line,end="")
# finally:
#      file_object.close()

import os
import  re
f_path = r'hosts'
f = open (f_path, "r+")
open('hosts_edit', 'w').write(re.sub(r'.*com', '1.3.4.5 lemon.com', f.read()))
