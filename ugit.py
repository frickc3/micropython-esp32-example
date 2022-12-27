# ugit
# micropython OTA update from github
# Created by TURFPTAx for the openmuscle project
# Check out https://openmuscle.org for more info
#
# Pulls files and folders from open github repository

import os
import urequests
import json
import hashlib
import machine
import time
import network
import binascii

global internal_tree

#### -------------User Variables----------------####
#### 
# Default Network to connect using wificonnect()
ssid = ""
password = ""

# CHANGE TO YOUR REPOSITORY INFO
# Repository must be public
user = ''
#repository = 'ugit_test'
repository = ''

# Don't remove ugit.py from the ignore_files unless you know what you are doing :D
# Put the files you don't want deleted or updated here use '/filename.ext'
ignore_files = ['/ugit.py','/boot.py','/test.py']
ignore = ignore_files
### -----------END OF USER VARIABLES ----------####

# Static URLS
# GitHub uses 'main' instead of master for python repository trees
giturl = 'https://github.com/{user}/{repository}'
call_trees_url = f'https://api.github.com/repos/{user}/{repository}/git/trees/master?recursive=1'
raw = f'https://raw.githubusercontent.com/{user}/{repository}/master/'

def pull(f_path,raw_url):
  print(f'pulling {f_path} from github')
  #files = os.listdir()
  r = urequests.get(raw_url)
  try:
    new_file = open(f_path, 'w')
    new_file.write(r.content.decode('utf-8'))
    new_file.close()
  except:
    print('decode fail try adding non-code files to .gitignore')
    try:
      new_file.close()
    except:
      print('tried to close new_file to save memory durring raw file decode')
  
def pull_all(tree=call_trees_url,raw = raw,ignore = ignore,isconnected=False,rep=None,usr=None):
  global repository, user  
  print('Version: 1.0.1')
  if not isconnected:
      wlan = wificonnect()
  b = 0
  if repository == '' or user == '':
      b = 1
  if rep != None:
    repository=rep
  if usr != None:
    user = usr
  print('Using: '+repository+' User: '+user)
  os.chdir('/')
  if b == 1:
    my_tree_url = f'https://api.github.com/repos/{user}/{repository}/git/trees/master?recursive=1'
    my_raw_url  = f'https://raw.githubusercontent.com/{user}/{repository}/master/'
    tree = pull_git_tree(tree_url=my_tree_url,raw=my_raw_url)  
  else:    
    tree = pull_git_tree()
  print(tree)
  internal_tree = build_internal_tree()
  internal_tree = remove_ignore(internal_tree)
  print(' ignore removed ----------------------')
  print(internal_tree)
  log = []
  # download and save all files
  for i in tree['tree']:
    if i['type'] == 'tree':
      try:
        os.mkdir(i['path'])
      except:
        print(f'failed to {i["path"]} dir may already exist')
    elif i['path'] not in ignore:
      try:
        os.remove(i['path'])
        log.append(f'{i["path"]} file removed from int mem')
        internal_tree = remove_item(i['path'],internal_tree)
      except:
        log.append(f'{i["path"]} del failed from int mem')
        print('failed to delete old file')
      try:
        pull(i['path'],raw + i['path'])
        log.append(i['path'] + ' updated')
      except:
        log.append(i['path'] + ' failed to pull')
  # delete files not in Github tree
  if len(internal_tree) > 0:
      print(internal_tree, ' leftover!')
      for i in internal_tree:
          os.remove(i)
          log.append(i + ' removed from int mem')
  logfile = open('ugit_log.py','w')
  logfile.write(str(log))
  logfile.close()
  time.sleep(10)
  print('resetting machine in 10: machine.reset()')
  machine.reset()
  #return check instead return with global

def wificonnect(ssid=ssid,password=password):
    print('Use: like ugit.wificonnect(SSID,Password)')
    print('otherwise uses ssid,password in top of ugit.py code')
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected() == True:
        return(wlan)
    wlan.active(False)
    wlan.active(True)
    wlan.config(txpower=8.5)
    wlan.connect(ssid,password)
    c = 0
    while not wlan.isconnected():
        time.sleep(1)
        c += 1
        print('Loop: %d' % c)
        pass
    print('Wifi Connected!!')
    print(f'SSID: {ssid}')
    print('Local Ip Address, Subnet Mask, Default Gateway, Listening on...')
    print(wlan.ifconfig())
    return wlan
  
def build_internal_tree():
  global internal_tree
  internal_tree = []
  os.chdir('/')
  for i in os.listdir():
    add_to_tree(i)
  return(internal_tree)

def add_to_tree(dir_item):
  global internal_tree
  print(dir_item)
  if is_directory(dir_item) and len(os.listdir(dir_item)) >= 1:
    os.chdir(dir_item)
    for i in os.listdir():
      add_to_tree(i)
    os.chdir('..')
  else:
    print(dir_item)
    if os.getcwd() != '/':
      subfile_path = os.getcwd() + '/' + dir_item
    else:
      subfile_path = os.getcwd() + dir_item
    try:
      print(f'sub_path: {subfile_path}')
      internal_tree.append([subfile_path,get_hash(subfile_path)])
    except OSError:
      print(f'{dir_item} could not be added to tree')


def get_hash(file):
  print('file: '+file)
  o_file = open(file)
  r_file = o_file.read()
  print('get_hash: '+str(r_file))
  sha1obj = hashlib.sha1(r_file)
  hash = sha1obj.digest()
  #return(hash.hex())
  return(binascii.hexlify(hash))

def get_data_hash(data):
    sha1obj = hashlib.sha1(data)
    hash = sha1obj.digest()
    #return(hash.hex())
    return(binascii.hexlify(hash))
  
def is_directory(file):
  directory = False
  try:
    #return (os.stat(file)[8] == 0)
     return ((os.stat(file)[0] & 0x4000) != 0)
  except:
    return directory
    
def pull_git_tree(tree_url=call_trees_url,raw = raw):
  print(tree_url)  
  r = urequests.get(tree_url,headers={'User-Agent': 'ugit-turfptax'})
  # ^^^ Github Requires user-agent header otherwise 403
  tree = json.loads(r.content.decode('utf-8'))
  return(tree)
  
def parse_git_tree():
  tree = pull_git_tree()
  dirs = []
  files = []
  for i in tree['tree']:
    if i['type'] == 'tree':
      dirs.append(i['path'])
    if i['type'] == 'blob':
      files.append([i['path'],i['sha'],i['mode']])
  print('dirs:',dirs)
  print('files:',files)
   
   
def check_ignore(tree=call_trees_url,raw = raw,ignore = ignore):
  os.chdir('/')
  tree = pull_git_tree()
  check = []
  # download and save all files
  for i in tree['tree']:
    if i['path'] not in ignore:
        print(i['path'] + ' not in ignore')
    if i['path'] in ignore:
        print(i['path']+ ' is in ignore')
        
def remove_ignore(internal_tree,ignore=ignore):
    clean_tree = []
    int_tree = []
    for i in internal_tree:
        int_tree.append(i[0])
    for i in int_tree:
        if i not in ignore:
            clean_tree.append(i)
    return(clean_tree)
        
def remove_item(item,tree):
    culled = []
    for i in tree:
        if item not in i:
            culled.append(i)
    return(culled)

def update():
    print('updates ugit.py to newest version')
    raw_url = 'https://raw.githubusercontent.com/turfptax/ugit/master/'
    pull('ugit.py',raw_url+'ugit.py')

def backup():
    int_tree = build_internal_tree()
    backup_text = "ugit Backup Version 1.0\n\n"
    for i in int_tree:
        data = open(i[0],'r')
        backup_text += f'FN:SHA1{i[0]},{i[1]}\n'
        backup_text += '---'+data.read()+'---\n'
        data.close()
    backup = open('ugit.backup','w')
    backup.write(backup_text)
    backup.close()