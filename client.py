#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import random
import sys
import threading
from time import sleep

serv_ip = '127.0.0.1'
serv_port = 6667
serv_addr = (serv_ip, serv_port)

class Client():
    def __init__(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_ip = '127.0.0.1'
            client_port = random.randint(10000, 65535)
            client_addr = (client_ip, client_port)
            self.client.bind(client_addr)
            self.Serv_Addr = serv_addr
            print  'Client initialized!'
        except:
            print 'Initialization failed. Please try again.'
            sys.exit()

    def recv_msg(self):
        BUFSIZE = 2048
        msg, addr = self.client.recvfrom(BUFSIZE)
        print 'Received from ' + str(addr[0]) + ' : ' + msg
        return msg, addr

    def send_msg(self, msg):
        self.client.sendto(msg, self.Serv_Addr)
        print 'Message sent to server'

client = Client()

def clin_read():
    while True:
        client.recv_msg()

def clin_send():
    while True:
        msg = raw_input()
        if not msg:
            break
        client.send_msg(msg)

threads = []

if __name__ == '__main__':
    print """Hey!! Welcome to the E-Mall! You can use the following commands:

/login UserName: log in to the server with UserName. The server will give you an ID, and your shop(if there is one) shares the same ID.
/logout UserName: Log out. You can go back anytime and we reserve your Name and ID.
/shops: View all the shops in the E-Mall so that you can enjoy your shopping.
/enter ShopID: Enter a shop and view the goods.
/goods: View the goods in the shop. If you are a shop owner and not in others' shop, you can view the goods in your shop.
/customers: View the customers in the(your) shop.(similar to '/goods')
/buy goodsID: Buy one product in the shop.
/leave: Leave a shop.
/addgoods goodsID [goodsName] [goodsPrice]: Add new goods to your shop. If there has been any product in our E-Mall directory, just input the ID.

Hope you have a good time!
Copyright: CHEN Xinkai
"""
    send = threading.Thread(target= clin_send)
    threads.append(send)
    read = threading.Thread(target= clin_read)
    threads.append(read)

    for t in threads:
        t.start()
