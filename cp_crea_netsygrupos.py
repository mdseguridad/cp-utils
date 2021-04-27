#!/usr/bin/env python3

# -*- coding: utf-8 -*


#Formato de entrada red/mask

import sys,random,time,argparse
from netaddr import *


def prettyGroup(objects):
    tmpList = objects
    if (len(tmpList) > 1):
        groupString = "'["
        for i in tmpList[0:-1]:
            groupString = groupString + '"'+ i + '", '
        groupString = groupString + '"'+ tmpList[-1] + '"'
        groupString = groupString + "]'"
    elif (len(tmpList) == 1):
        groupString = '"' + tmpList[0] + '"'
    else:
        groupString = '"ErrorRaro"'
    return groupString

colors = [ 'aquamarine', 'black', 'blue', 'crete blue', 'burlywood', 'cyan', 'dark green', 'khaki', 'orchid', 'dark orange', \
'dark sea green', 'pink', 'turquoise', 'dark blue', 'firebrick', 'brown', 'forest green', 'gold', 'dark gold', \
'gray', 'dark gray', 'light green', 'lemon chiffon', 'coral', 'sea green', 'sky blue', 'magenta', 'purple', 'slate blue',\
 'violet red', 'navy blue', 'olive', 'orange', 'red', 'sienna', 'yellow']

color = random.choice(colors)
parser = argparse.ArgumentParser(description='Creamios un grupo de redes a partir de un ficheros de texto\
 ,una red por linea X.Y.Z.W/M')
parser.add_argument('-t','--tag', help='tag', default='python')
parser.add_argument('-n','--subname', help='', default='scriptmade')
args = parser.parse_args()
tag = args.tag
subname = args.subname

commandTail ='ignore-warnings true -s id.txt'
fecha = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
fechaName = time.strftime('%Y%m%d',time.localtime())


listadoObjectos = []
for line in sys.stdin:
  line = line.strip()
  try: 
    ip = IPNetwork(line)
  except:
    print ('### Error en la IP "', line, '", linea numero: ', len(listadoObjectos)," ===")
    break
  subNet = str(ip.ip)
  maskLength = str(ip.prefixlen)
  subNetMask = str(ip.netmask)
  # mount parts
  
  if (maskLength == '32'):
    # Host
    name = 'host_' + subname +'_'+ subNet
    comments = 'Host ' + subname + ' ' + subNet + ' --  fecha: ' + fecha
    command = 'mgmt_cli add-host name "' + name + '" ip-address ' + \
    subNet + ' tags "' + tag + '" color "' + color + '" comments "' +  comments +'" ' + commandTail  
  else:
    # Network  
    name = 'net_' + subname +'_'+ subNet + '_' + maskLength
    comments = ' Red de ' + subname + ' ' + subNet +'/'+maskLength + ' con mascara= ' \
    + subNetMask + ' --  fecha: ' + fecha
    
    command = 'mgmt_cli add-network name "' + name +'" subnet ' + \
    subNet + ' mask-length '+ maskLength + ' tags "' + tag +\
    '" color "' + color + '" comments "' + comments + '" ' + commandTail
  
  print (command)
  listadoObjectos.append(name)
print ('')
print ('### Fin de los Objetos')
print ('')
print ("sleep 60")
print ("mgmt_cli -s id.txt publish")
print ("sleep 60")
print ('###Grupo')
comments = 'Grupo ' + subname + ' creado ' + fecha
print ('mgmt_cli add group name "Gr_' + subname + '_' + fechaName+ '" members ' + prettyGroup(listadoObjectos) +\
               ' tags "' + tag +'" color "' + color + '" comments "'+ comments + '" ' + commandTail)
print ("mgmt_cli -s id.txt publish")
print ("sleep 60")
print ("###End")
