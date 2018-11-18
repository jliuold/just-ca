# -*- coding: utf-8 -*-
'简化openssl 证书的生成过程，通过简单的命令生成证书，参考HTTPS权威指南相关内容'
__author__ = 'jliu666 <jliu666@hotmail.com>'
import argparse
import os
import getpass

CA_PATH = os.path.realpath('root')
SERVER_PATH = os.path.realpath('server')
ALT_NAME  = 'altname'
CA_PASS = "123456"
SERVER_CA_HOSTNAME='localhost'
CREATE_ROOT_CA_CMD='''
# Create the root CA csr
export CA_PS_ENV=CA_PASS
openssl genrsa -out CA_PATH/ca/private/ca.key -passout env:CA_PS_ENV 4096
chmod 0400 CA_PATH/ca/private/ca.key
touch CA_PATH/ca/db/certificate.db
echo 1001 > CA_PATH/ca/db/crl.srl
openssl rand -hex 16 > CA_PATH/ca/db/crt.srl
# Create the root CA csr
openssl req -new -batch \
            -config CA_PATH/conf/ca.conf \
            -key CA_PATH/ca/private/ca.key \
            -out CA_PATH/ca/ca.csr \
            -passin env:CA_PS_ENV

# Create the root CA certificate
openssl ca -selfsign -batch -notext \
           -config CA_PATH/conf/ca.conf \
           -in CA_PATH/ca/ca.csr \
           -out CA_PATH/ca/ca.crt \
           -days 3652 \
           -extensions root_ca_ext \
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

'获取主机名'
def input_server_hostname():
    while True:
        hostname = input('Please input hostname['+SERVER_CA_HOSTNAME+']:')
        if len(hostname)==0:
            hostname = SERVER_CA_HOSTNAME
            break
        return hostname

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


    cmd = CREATE_ROOT_CA_CMD.replace('CA_PATH', ca_path)
    cmd = cmd.replace('CA_PASS', ca_pass)
    cmd = cmd.replace('ALT_NAME', alt_name)
    os.makedirs(CA_PATH)
    os.makedirs(CA_PATH+"/ca")
    os.makedirs(CA_PATH+"/ca/archive")
    os.makedirs(CA_PATH+"/ca/db")
    os.makedirs(CA_PATH+"/ca/private")
    os.makedirs(CA_PATH+"/conf")
    os.makedirs(CA_PATH+"/crl")

    with open("./temp/root.conf.temp","r",encoding="utf-8") as f:
        lines = f.readlines() 
        with open(ca_path+"/conf/ca.conf","w",encoding="utf-8") as f_w:
            for line in lines:
                line = line.replace("CA_PATH",ca_path)
                line = line.replace("ALT_NAME",alt_name)
                f_w.write(line)
    os.system(cmd)

def create_server_ca():
    print("Issue server ca:")


parser = argparse.ArgumentParser(description="just ca!!!")
parser.add_argument('-t','--type',default='server',help='root:create root ca;server:issue a server cert by root ca')
args = parser.parse_args()
caType = (args.type)

if caType == 'root':
    create_root_ca()
if caType == 'server':
    create_server_ca()

