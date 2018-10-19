from scapy.all import *
import os
import sys
import datetime

all_data = dict()
file_names = dict()
target_ip = None

def printTcpPayload(pkg):
   if TCP not in pkg:
      return 
   name_key = pkg[IP].src + "-" + pkg[IP].dst
   if Raw in pkg[TCP]:
      if name_key in all_data:
         all_data[name_key] += pkg[Raw].load
      else :
         all_data[name_key] = pkg[Raw].load
      # print(os.getcwd())
   if pkg[TCP].flags & 0X01 == 1 and name_key in all_data:
      index = 1
      if name_key in file_names:
         file_names[name_key] += 1
      else:
         file_names[name_key] = 1
      index = file_names[name_key]
      suffix = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S")
      file = open(os.getcwd() + "/" + name_key + "-" + suffix+"-" +str(index) + ".dat", 'wb')
      file.write(all_data[name_key])
      file.close()
      del all_data[name_key]

def filter_func(pkg):
   if TCP not in pkg:
      return False
   if target_ip is not None:
      return pkg[IP].src == target_ip or pkg[IP].dst == target_ip
   return True

if __name__ == '__main__':
   filter = "tcp"
   if len(sys.argv) > 1:
      target_ip = sys.argv[1]
      filter = "tcp and (dst host "+sys.argv[1]+" or src host "+sys.argv[1]+" )"
   print('sniff-filter:' + filter)
   p = sniff(lfilter=filter_func, prn=printTcpPayload, store=0)