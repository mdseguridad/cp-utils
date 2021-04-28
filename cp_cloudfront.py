#!/usr/bin/env python3

# -*- coding: utf-8 -*


#Formato de entrada red/mask

import sys,random,time,argparse,requests,json
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

def getNetList(url):
    print ('Descargando de: ', url)
    response = requests.get(url)
    masterList = json.loads(response.content)
    networkList = []
    for i in masterList:
        print ('Adding ',i,' networks')
        networkList.extend(masterList[i])
    return networkList

colors = [ 'aquamarine', 'black', 'blue', 'crete blue', 'burlywood', 'cyan', 'dark green', 'khaki', 'orchid', 'dark orange', \
'dark sea green', 'pink', 'turquoise', 'dark blue', 'firebrick', 'brown', 'forest green', 'gold', 'dark gold', \
'gray', 'dark gray', 'light green', 'lemon chiffon', 'coral', 'sea green', 'sky blue', 'magenta', 'purple', 'slate blue',\
 'violet red', 'navy blue', 'olive', 'orange', 'red', 'sienna', 'yellow']

color = random.choice(colors)
fechaName = time.strftime('%Y%m%d',time.localtime())

parser = argparse.ArgumentParser(description='Descargamos las redes de la URL de Cloudfront y generamos un\
script para CheckPoint')
parser.add_argument('-t','--tag', help='tag', default='cloudfrontOrigin')
parser.add_argument('-n','--subname', help='', default='cloudfront')
parser.add_argument('-o','--outfile', help='', default='checkpoint-script-'+fechaName+'.txt')
args = parser.parse_args()
tag = args.tag
subname = args.subname
outFile = args.outfile
urlClodfront = 'http://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips'

commandTail ='ignore-warnings true -s id.txt'
fecha = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
fechaName = time.strftime('%Y%m%d',time.localtime())

print ('Writing output to: ', outFile)
f = open (outFile,'w',encoding='utf8')

f.write ('# Script for Check Point API to add Cloudfront IP ranges\n')
f.write ('\n')
f.write ('# Fecha:'+ fecha + '\n')
f.write ('# Descargado de: '+ urlClodfront + '\n\n')
listadoObjectos = []
for line in getNetList(urlClodfront):
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
  
  f.write (command + '\n')
  listadoObjectos.append(name)
f.write ('\n')
f.write ('### Fin de los Objetos\n')
f.write ('\n')
f.write ("sleep 60\n")
f.write ("mgmt_cli -s id.txt publish\n")
f.write ("sleep 60\n")
f.write ('###Grupo\n')
comments = 'Grupo ' + subname + ' creado ' + fecha
f.write ('mgmt_cli add group name "Gr_' + subname + '_' + fechaName+ '" members ' + prettyGroup(listadoObjectos) +\
               ' tags "' + tag +'" color "' + color + '" comments "'+ comments + '" ' + commandTail + '\n')
f.write ("mgmt_cli -s id.txt publish\n")
f.write ("sleep 60\n")
f.write ("###End\n")

print ('Close file: ', outFile)
