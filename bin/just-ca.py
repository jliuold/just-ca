# -*- coding: utf-8 -*-
'简化openssl 证书的生成过程，通过简单的命令生成证书，参考HTTPS权威指南相关内容'
__author__ = 'jliu666 <jliu666@hotmail.com>'
import argparse
import os
import sys
import getpass

BIN_PATH=sys.path[0]

CA_PATH = os.path.realpath(BIN_PATH+'/../out')
SERVER_NAME = 'localhost'
ALT_NAME  = 'DNS:localhost'
CA_PASS = "123456"
CREATE_ROOT_CA_CMD='''
# Create the root CA csr
export CA_PS_ENV=__CA_PASS__
openssl genrsa -out __CA_PATH__/ca/private/ca.key -passout env:CA_PS_ENV 4096
chmod 0400 __CA_PATH__/ca/private/ca.key
touch __CA_PATH__/ca/db/certificate.db
echo 1001 > __CA_PATH__/ca/db/crl.srl
openssl rand -hex 16 > __CA_PATH__/ca/db/crt.srl
# Create the root CA csr
openssl req -new -batch \
            -config __CA_PATH__/conf/ca.conf \
            -key __CA_PATH__/ca/private/ca.key \
            -out __CA_PATH__/ca/ca.csr \
            -passin env:CA_PS_ENV

# Create the root CA certificate
openssl ca -selfsign -batch -notext \
           -config __CA_PATH__/conf/ca.conf \
           -in __CA_PATH__/ca/ca.csr \
           -out __CA_PATH__/ca/ca.crt \
           -days 3652 \
           -extensions root_ca_ext \
           -passin env:CA_PS_ENV
'''

CREATE_SERVER_CA_CMD='''
export CA_PS_ENV=__CA_PASS__
mkdir -p __CA_PATH__/ca/certs
# Create the server key and csr
openssl req -new -nodes \
            -config __CA_PATH__/conf/__SERVER_NAME__.server.conf \
            -keyout __CA_PATH__/ca/private/__SERVER_NAME__.server.key \
            -out __CA_PATH__/ca/__SERVER_NAME__.server.csr

chmod 0400 __CA_PATH__/ca/private/__SERVER_NAME__.server.key

# Create the server certificate
openssl ca -batch -notext \
           -config __CA_PATH__/conf/ca.conf \
           -in __CA_PATH__/ca/__SERVER_NAME__.server.csr \
           -out __CA_PATH__/ca/certs/__SERVER_NAME__.server.crt \
           -days 730 \
           -extensions server_ext \
           -passin env:CA_PS_ENV
'''

'获取证书路径'
def input_ca_path():
    while True:
        caPath = input("Please input target directory["+CA_PATH+"]:")
        if len(caPath)==0:
            caPath=CA_PATH
        if os.path.exists(caPath):
            print("path",os.path.realpath(caPath),"exist")
        else:
            return os.path.realpath(caPath)

'获取altName'
def input_alt_name():
    while True:
        altname = input("Please input subject altName["+ALT_NAME+"]:")
        if len(altname)==0:
            altname=ALT_NAME
        return altname

'获取密码'
def input_password():
    while True:
        caPass = getpass.getpass("Please input password for ca["+CA_PASS+"]:")
        if len(caPass)==0:
            caPass=CA_PASS
        return caPass

'获取server name'
def input_server_name():
    while True:
        servername = input("Please input server name["+SERVER_NAME+"]:")
        if len(servername)==0:
            servername=SERVER_NAME
        return servername


'''
创建根证书
'''
def create_root_ca():

    ca_path = CA_PATH
    alt_name = ALT_NAME
    ca_pass = CA_PASS

    while True:
        ca_path = input_ca_path()
        alt_name = input_alt_name()
        ca_pass = input_password()
        check = input("Target directory is "+ ca_path+";subjet altName is "+alt_name+' [Y/N]?')
        if check == 'Y':
            break
        if check == 'N':
            continue


    cmd = CREATE_ROOT_CA_CMD.replace('__CA_PATH__', ca_path)
    cmd = cmd.replace('__CA_PASS__', ca_pass)
    cmd = cmd.replace('__ALT_NAME__', alt_name)
    os.makedirs(ca_path)
    os.makedirs(ca_path+"/ca")
    os.makedirs(ca_path+"/ca/archive")
    os.makedirs(ca_path+"/ca/db")
    os.makedirs(ca_path+"/ca/private")
    os.makedirs(ca_path+"/conf")

    with open(BIN_PATH+"/../temp/root.conf.temp","r",encoding="utf-8") as f:
        lines = f.readlines() 
        with open(ca_path+"/conf/ca.conf","w",encoding="utf-8") as f_w:
            for line in lines:
                line = line.replace("__CA_PATH__",ca_path)
                line = line.replace("__ALT_NAME__",alt_name)
                f_w.write(line)
    os.system(cmd)

def create_server_ca():
    print("Issue server ca:")
    server_name = SERVER_NAME
    ca_path = CA_PATH
    alt_name = ALT_NAME

    while True:
        server_name = input_server_name()
        alt_name = input_alt_name()
        ca_pass = input_password()
        check = input("Subjet altName is "+alt_name+' [Y/N]?')
        if check == 'Y':
            break
        if check == 'N':
            continue

    
    cmd = CREATE_SERVER_CA_CMD.replace('__CA_PATH__', ca_path)
    cmd = cmd.replace('__CA_PASS__', ca_pass)
    cmd = cmd.replace('__SERVER_NAME__', server_name)
    cmd = cmd.replace('__ALT_NAME__', alt_name)
    with open(BIN_PATH+"/../temp/server.conf.temp","r",encoding="utf-8") as f:
        lines = f.readlines() 
        with open(ca_path+"/conf/"+server_name+".server.conf","w",encoding="utf-8") as f_w:
            for line in lines:
                line = line.replace("__CA_PATH__",ca_path)
                line = line.replace("__ALT_NAME__",alt_name)
                f_w.write(line)
    os.system(cmd)

parser = argparse.ArgumentParser(description="just ca!!!")
parser.add_argument('-t','--type',default='server',help='root:create root ca;server:issue a server cert by root ca')
args = parser.parse_args()
caType = (args.type)

if caType == 'root':
    create_root_ca()
if caType == 'server':
    create_server_ca()

