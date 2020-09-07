import sys
import time
from datetime import datetime
import socket
import threading
import requests
import zmq
import json
host = '0.0.0.0'
port = 6500
INVALID_DATA=False



def get_nodes():
    base_url="http://dns.dotscoin.com/get_nodes/"
    nodes = requests.get(base_url)
    print(nodes)
    print(nodes.json()['nodes'])

udpsock= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
udpsock.bind((host,port))

def broadcast(data,host,port):
    udpsock.sendto(data.encode('utf-8'),(host,port))

#reciever 
def reciever():
    context = zmq.Context()
    zsocket = context.socket(zmq.REP)
    zsocket.bind("tcp://127.0.0.1:5558")
    while True:
        # print("r")
        data = json.loads(zsocket.recv_string())
        print(data)
        zsocket.send_string("recieved")