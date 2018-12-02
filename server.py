#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket
import sys
import threading

userName = {} # addr : name
userID = {} # name : id

shopID = [] # shop_id == owner_id
in_Shops = {} # user_addr : shop_id(owner_id)
customers = {} # shop_id(owner_id) : customer_name
Goods = {} # shop_id(owner_id) : goods_id

goodsID = [] # list of all the goods in the Mall
goodsName = {} # goods_id : name
goodsPrice = {} # goods_id : price

in_Shops['admin'] = -1

# determine if a user has shop
def has_Shop(owner_id):
    for id in shopID:
        if owner_id == id:
            return True
    return False

# for owners to get their shop id
def get_shopID(name):
    owner_id = userID[name]
    if owner_id in shopID:
        return True
    return False

# get user's address, given his/her name
def get_address(name):
    for addr in userName.keys():
        if userName[addr] == name:
            return addr
    return False

# get user's name, given his/her ID
def get_name(id):
    for name in userID.keys():
        if userID[name] == id:
            return name
    return False

class Server():
    def __init__(self):
        try:
            loc_ip = '127.0.0.1'
            loc_port = 6667
            loc_addr = (loc_ip, loc_port)
            self.serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.serv.bind(loc_addr)
            print 'E-Mall Server Initialized!\n'

        except:
            print 'E-Mall server initialization failed. Please try again.\n'
            sys.exit()

    def recv_msg(self):
        BUFSIZE = 2048
        msg, addr = self.serv.recvfrom(BUFSIZE)
        print 'Received from ' + str(addr[0]) + ':\n'+ msg + '\n'
        return msg, addr

    def send_msg(self, msg, addr):
        self.serv.sendto(msg, addr)
        print 'Message sent to:' + str(addr) + '\n'

    def broadcast(self, msg, client_addrs):
        if len(client_addrs):
            print 'Broadcasting...\n'
            for client_addr in client_addrs:
                # leave out the users that are offline
                if client_addr not in userName.keys():
                    print client_addr + ' has logged out.\n'
                    continue
                self.send_msg('[Server]: ' + msg + '\n', client_addr)
            print 'Broadcast Ending...\n'
        else:
            print 'No user. Broadcast Failed.\n'

    def handle_client_command(self, msg, addr):
        commd = msg.split(' ')
        if commd[0] in ['/login', '/logout', '/shops', '/enter', '/goods', '/customers', '/buy', '/leave', '/addgoods']:
            if commd[0] == '/login':
                try:
                    # logged in or not?
                    if commd[1] in userID.keys() and get_address(commd[1]) != False and addr != get_address(commd[1]):
                        self.send_msg('You have logged in somewhere else. Log out first!\n', addr)
                    else:
                        if addr in userName.keys():
                            self.send_msg(str(addr) + ', you have already logged in!\n', addr)
                        else:
                            userName[addr] = (commd[1])
                            # one user name corresponds to one id
                            if commd[1] not in userID.keys():
                                # user id starts from 00000
                                userID[commd[1]] = '%05d' % len(userID.keys())
                            # make sure that this address in not in any shop
                            in_Shops[addr] = -1
                            self.send_msg(commd[1] + ' successfully logged in! Your ID is ' + userID[commd[1]] + '.\n',
                                          addr)
                            print commd[1] + ' logged in from ' + str(addr) + '\n'

                except:
                    self.send_msg('Invalid input!!', addr)

            if commd[0] == '/logout':
                try:
                    # determine if the user/address has logged in
                    if (addr not in userName.keys()) or (commd[1] not in userID.keys()):
                        self.send_msg('Hello ' + commd[1] + ', you have not logged in.\n', addr)
                    else:
                        if addr != get_address(commd[1]):
                            self.send_msg('Please input your own name.\n', addr)
                        else:
                            # if the user is in a shop, kick him/her out!
                            if in_Shops[addr] >= 0:
                                shop_id = in_Shops[addr]
                                if customers.has_key(shop_id):
                                    if len(customers[shop_id]) > 0:
                                        customers[shop_id].remove(commd[1])
                                # notify the owner
                                owner_name = get_name(shop_id)
                                owner_addr = get_address(owner_name)
                                if owner_addr != False and owner_addr != addr:
                                    self.send_msg('User ' + userName[addr] + ' has left your shop.\n', owner_addr)
                                del in_Shops[addr]
                            self.send_msg('Dear ' + commd[1] + ', you logged out successfully!\n', addr)
                            # delete the key 'addr' and its value(username) in userName
                            del userName[addr]
                            print commd[1] + ' logged out from ' + str(addr) + '\n'

                except:
                    self.send_msg('Invalid input!!', addr)


            if commd[0] == '/shops':
                try:
                    if len(shopID) == 0:
                        self.send_msg('There is currently no shop. You can create one.\n', addr)
                    else:
                        for shop in shopID:
                            # The 'Shops' dictionary stores shop IDs and the corresponding names of the owners
                            name = get_name(shopID)
                            self.send_msg('Shop: ' + shop + '  Owner name: ' + name + '  Owner ID: ' + userID[name],
                                          addr)

                except:
                    self.send_msg('Invalid input!!\n', addr)

            if commd[0] == '/enter':
                try:
                    # see if the shop exists
                    if (commd[1] in shopID) is False:
                        self.send_msg('There is no Shop ' + commd[1] + '. Please try again.' + '\n', addr)
                    # see if the user already in one shop
                    elif in_Shops[addr] != -1:
                        if in_Shops[addr] == commd[1]:
                          self.send_msg('You have already in Shop ' + commd[1], addr)
                        else:
                            self.send_msg('You cannot enter another shop before leaving one.\n', addr)
                    else:
                        # if the user is the first customer, create a list
                        if customers.has_key(commd[1]) is False:
                            customers[commd[1]] = []
                        customers[commd[1]].append(userName[addr])
                        self.send_msg('You have entered Shop ' + commd[1] + '\n', addr)
                        in_Shops[addr] = commd[1]
                        # if there is any goods in shop, show them
                        if Goods.has_key(commd[1]):
                            for goods_id in Goods[commd[1]]:
                                goods_name = goodsName[goods_id]
                                goods_price = goodsPrice[goods_id]
                                self.send_msg(
                                    'Product ' + goods_id + ': Name: ' + goods_name + ' Price: ' + goods_price + '\n',
                                    addr)
                        else:
                            self.send_msg('No goods in shop.\n', addr)
                        # notify the owner
                        owner_name = get_name(commd[1])
                        owner_addr = get_address(owner_name)
                        customer_name = userName[addr]
                        if owner_addr != False:
                            self.send_msg('User ' + customer_name + ' has entered your shop\n', owner_addr)

                except:
                    self.send_msg('Invalid input!!\n', addr)

            if commd[0] == '/leave':
                try:
                    # see if the user is not in any shop
                    if in_Shops[addr] == -1:
                        self.send_msg('You are not in any shop', addr)
                    else:
                        shop_id = in_Shops[addr]
                        user_name = userName[addr]
                        if len(customers[shop_id]) == 1:
                            del customers[shop_id]
                        else:
                            customers[shop_id].remove(user_name)
                        in_Shops[addr] = -1
                        # notify the owner
                        owner_name = get_name(shop_id)
                        owner_addr = get_address(owner_name)
                        if owner_addr != False and owner_addr != addr:
                            self.send_msg('User ' + user_name + ' left your shop.\n', owner_addr)
                        self.send_msg('You have left Shop ' + shop_id + '.\n', addr)

                except:
                    self.send_msg('Invalid input!!', addr)

            if commd[0] == '/goods':
                try:
                    # if this user has shop and is not in other shops, return the info of his own shop
                    if in_Shops[addr] == -1 and has_Shop(userID[userName[addr]]):
                        shop_id = userID[userName[addr]]
                        if Goods.has_key(shop_id):
                            for goods_id in Goods[shop_id]:
                                goods_name = goodsName[goods_id]
                                goods_price = goodsPrice[goods_id]
                                self.send_msg(
                                    'Product ID: ' + goods_id + ', Name: ' + goods_name + ', Price: ' + goods_price + '\n',
                                    addr)
                        else:
                            self.send_msg('No goods in your shop.\n', addr)
                    # return the info of the shop in which user is staying
                    elif in_Shops[addr] in shopID:
                        shop_id = in_Shops[addr]
                        if Goods.has_key(shop_id):
                            for goods_id in Goods[shop_id]:
                                goods_name = goodsName[goods_id]
                                goods_price = goodsPrice[goods_id]
                                self.send_msg(
                                    'Product ID: ' + goods_id + ' Name: ' + goods_name + ' Price: ' + goods_price + '\n',
                                    addr)
                        else:
                            self.send_msg('No goods in shop.\n', addr)
                    else:
                        self.send_msg('This command is unavailable. Try other commands.\n', addr)

                except:
                    self.send_msg('Invalid input!!\n', addr)

            if commd[0] == '/customers':
                try:
                    # if this user has shop and is not in other shops, return the info of his own shop
                    if in_Shops[addr] == -1 and has_Shop(userID[userName[addr]]):
                        shop_id = userID[userName[addr]]
                        if customers.has_key(shop_id):
                            self.send_msg('Current customers: ', addr)
                            for customer in customers[shop_id]:
                                self.send_msg(customer + '\n', addr)
                        else:
                            self.send_msg('No customer in shop.\n', addr)
                    # if the user in any shop..
                    elif in_Shops[addr] in shopID:
                        shop_id = in_Shops[addr]
                        # read the customer info into a list and then send together
                        self.send_msg('Current customers: ', addr)
                        cust = []
                        for customer in customers[shop_id]:
                            cust.append(customer)
                        self.send_msg(cust + '\n', addr)
                    else:
                        self.send_msg('This command is unavailable. Please try other commands.\n', addr)
                except:
                    self.send_msg('Invalid input!!\n', addr)

            if commd[0] == '/buy':
                try:
                    # if the user is not in any shop, tell him/her
                    if in_Shops[addr] == -1:
                        self.send_msg('You are not in any shop.\n', addr)
                    # if the user trying to buy something in his/her own shop, tell him/her
                    elif in_Shops[addr] == userID[userName[addr]]:
                        self.send_msg('It is your own shop.\n', addr)
                    else:
                        if len(commd) == 1 or commd[1] not in goodsID:
                            self.send_msg('Invalid input.\n', addr)
                        elif Goods.has_key(commd[1]) is False:
                            self.send_msg('No good in shop.\n', addr)
                        else:
                            self.send_msg('You bought product ' + commd[1] + ' (Name: ' + goodsName[
                                commd[1]] + ') successfully at the price: ' + goodsPrice[commd[1]] + '.\n', addr)
                            shop_id = in_Shops[addr]
                            # notify the owner
                            owner_name = get_name(shop_id)
                            owner_addr = get_address(owner_name)
                            self.send_msg(
                                userName[addr] + ' has bought product ' + commd[1] + ' (Product Name: ' + goodsName[
                                    commd[1]] + ').\n', owner_addr)

                except:
                    self.send_msg('Invalid input.\n', addr)

            if commd[0] == '/addgoods':
                try:
                    if has_Shop(userID[userName[addr]]) == False:
                        self.send_msg('You do not even own a shop!\n', addr)
                    else:
                        owner_name = userName[addr]
                        shop_id = userID[owner_name]
                        # the value of "Goods" is a list
                        if Goods.has_key(shop_id) is False:
                            Goods[shop_id] = []
                        if commd[1] not in Goods[shop_id]:
                            Goods[shop_id].append(commd[1])
                            if commd[1] not in goodsID:
                                goodsID.append(commd[1])
                                goodsName[commd[1]] = commd[2]
                                goodsPrice[commd[1]] = commd[3]
                                print 'New product added to directory. Product ID: ' + commd[1] + ' Name: ' + commd[
                                    2] + ' Price: ' + commd[3] + '\n'
                                # if new goods added, notify all the other shop owners
                                for ownerid in shopID:
                                    ownername = get_name(ownerid)
                                    owneraddr = get_address(ownername)
                                    if owneraddr != False and owneraddr != addr:
                                        self.send_msg(
                                            'New product added to directory. Product ID: ' + commd[1] + ' Name: ' +
                                            commd[
                                                2] + ' Price: ' + commd[3] + '\n', owneraddr)
                                self.send_msg('New product added to shop. Product ID: ' + commd[1] + ' Name: ' + commd[
                                    2] + ' Price: ' + commd[3] + '\n', addr)
                            else:
                                self.send_msg(
                                    'This product has been registered. The name and price is automatically attached.\n',
                                    addr)
                                self.send_msg(
                                    'New product added to shop. Product ID: ' + commd[1] + ' Name: ' + goodsName[
                                        commd[1]] + ' Price: ' + goodsPrice[commd[1]] + '\n', addr)
                                # notify all the customers in shop
                            if customers.has_key(shop_id):
                                for customer in customers[shop_id]:
                                    customer_addr = get_address(customer)
                                    self.send_msg(
                                        'New product added to shop. Product ID: ' + commd[1] + ', name: ' + goodsName[
                                            commd[1]] + ', price: ' + goodsPrice[commd[1]], customer_addr)
                        else:
                            self.send_msg('You have added this one!\n', addr)

                except:
                    self.send_msg('Invalid input!!\n', addr)

        else:
            self.serv.sendto('Invalid command. Please try again.\n', addr)

    def handle_server_command(self, msg):
        commd = msg.split(' ')
        if commd[0] in ['/msg', '/opennewshop', '/enter', '/leave', '/goods', '/customers', '/shops', '/users', '/closeshop']:
            # e.g. /msg 00001
            if commd[0] == '/msg':
                try:
                    # if only input '/msg', broadcast to all the users
                    if len(commd) == 1:
                        print 'Please input your message: '
                        note = raw_input()
                        self.broadcast(note, userName.keys())
                    else:
                        print 'Please input your message: '
                        note = raw_input()
                        # admin can input more than one ID
                        for user_id in commd[1:]:
                            # leave out invalid IDs
                            if user_id not in userID.values():
                                print user_id + ' is an invalid id.\n'
                                continue
                            user_name = get_name(user_id)
                            user_addr = get_address(user_name)
                            # leave out users who are offline
                            if user_addr not in userName.keys():
                                print user_id + ' has logged out.\n'
                                continue
                            self.send_msg('[Server]: ' + note + '\n', user_addr)

                except:
                    print 'Invalid Input!!\n'

            if commd[0] == '/opennewshop':
                try:
                    if len(commd) == 1:
                        print 'Please input a shop id!\n'
                    else:
                        if commd[1] in shopID:
                            print 'This shop already existed!\n'
                        else:
                            if commd[1] not in userID.values():
                                print 'This user have not registered.\n'
                            else:
                                # admin can input more than one ID
                                for user_id in commd[1:]:
                                    user_name = get_name(user_id)
                                    if user_name not in userName.values():
                                        print user_id + ' has logged out. \n'
                                    else:
                                        shopID.append(user_id)
                                        user_addr = get_address(user_name)
                                        self.send_msg(
                                            ' ' + user_name + ', your shop opens successfully! Add some goods first!\n',
                                            user_addr)
                                        print 'New shop opened. Shop ID: ' + user_id + '\n'
                                        self.broadcast(
                                            'New shop opened!! Shop ID: ' + user_id + '. Go and have a look!\n',
                                            userName.keys())

                except:
                    print 'Invalid input!!\n'

            if commd[0] == '/enter':
                try:
                    if len(commd) == 1:
                        print 'You should input a shop name!\n'
                    else:
                        # if admin is already in a shop
                        if in_Shops['admin'] != -1:
                            print 'You cannot enter another shop.\n'
                        else:
                            if (commd[1] in shopID) is False:
                                print 'Invalid shop name. Please try again.\n'
                            else:
                                print 'You have entered Shop ' + commd[1] + '\n'
                                in_Shops['admin'] = commd[1]

                except:
                    print 'Invalid input!!\n'

            if commd[0] == '/leave':
                try:
                    if in_Shops['admin'] == -1:
                        print 'You are not in any shop!\n'
                    else:
                        shop_id = in_Shops['admin']
                        in_Shops['admin'] = -1
                        print 'You have left Shop ' + shop_id + '\n'

                except:
                    print 'Invalid input!!\n'

            if commd[0] == '/goods':
                try:
                    # if admin not in any shop, show the E-Mall Directory
                    if in_Shops['admin'] == -1:
                        print 'You are not in any shop. Goods in the E-Mall Directory:\n'
                        if len(goodsID) == 0:
                            print 'Nothing.\n'
                        else:
                            for id in goodsID:
                                print 'Goods id: ' + id + ' goods name: ' + goodsName[id] + ' goods price: ' + \
                                      goodsPrice[id] + '\n'
                    # if admin is in a shop, show the goods in shop
                    else:
                        shop_id = in_Shops['admin']
                        if Goods.has_key(shop_id):
                            product_IDs = Goods[shop_id]
                            for product_id in product_IDs:
                                print 'Goods id: ' + product_id + ' goods name: ' + goodsName[
                                    product_id] + ' goods price: ' + goodsPrice[product_id] + '\n'
                        else:
                            print 'No goods in shop.\n'

                except:
                    print 'Invalid input!!\n'

            if commd[0] == '/customers':
                try:
                    if in_Shops['admin'] == -1:
                        print 'You are not in any shop.\n'
                    else:
                        shop_id = in_Shops['admin']
                        if customers.has_key(shop_id):
                            for customer in customers[shop_id]:
                                print 'Name: ' + customer + ' id: ' + userID[customer]
                            print '\n'
                        else:
                            print 'No customer in this shop (except you, of course).\n'
                except:
                    print 'Invalid input!!\n'

            if commd[0] == '/shops':
                try:
                    if len(shopID) > 0:
                        for shop in shopID:
                            print 'Shop id:' + shop + ' Owner:' + get_name(shop)
                    else:
                        print 'There is no shop at all.\n'
                except:
                    print 'Invalid input!!\n'

            if commd[0] == '/users':
                try:
                    if userName:
                        for name in userName.values():
                            user_id = userID[name]
                            if has_Shop(user_id):
                                print 'Name: *' + name + ' ID: ' + user_id
                            else:
                                print 'Name: ' + name + ' ID: ' + user_id
                        print '\n'
                    else:
                        print 'There is no user at all.\n'

                except:
                    print 'Invalid input!!\n'

            if commd[0] == '/closeshop':
                try:
                    if len(commd) == 1:
                        print 'You should specify a shop id.\n'
                    else:
                        if (commd[1] in shopID) is False:
                            print 'No such shop! Try again.\n'
                        else:
                            # notify the owner
                            owner_name = get_name(commd[1])
                            owner_addr = get_address(owner_name)
                            if owner_addr != False:
                                self.send_msg('[Server]: Your shop is being closed\n', owner_addr)
                            # remove all the customers(if any)
                            if customers.has_key(commd[1]):
                                for customer in customers[commd[1]]:
                                    cust_addr = get_address(customer)
                                    self.send_msg(
                                        '[Server]: Sorry, the shop in which you are shopping has been closed\n',
                                        cust_addr)
                                    in_Shops[cust_addr] = -1
                                del customers[commd[1]]
                            # remove all the goods(if any)
                            if Goods.has_key(commd[1]):
                                del Goods[commd[1]]
                            # remove this shop
                            shopID.remove(commd[1])

                except:
                   print 'Invalid input!!\n'

        else:
            print 'Invalid command. Please try again.\n'

server = Server()

def serv_recv():
    while True:
        msg, addr = server.recv_msg()
        server.handle_client_command(msg, addr)

def serv_self():
    while True:
        msg = raw_input()
        server.handle_server_command(msg)

threads = []

if __name__ == '__main__':
    print """Hello, you are the administrator now. You can use the following commands:

/msg [user address](separate with whitespace): If you leave 'user address' empty, you can broadcast to all the users.
/shops: View all the shops in this E-Mall.
/opennewshop userID: Open a shop for a user(one shop for one user only).
/enter ShopID: Enter a shop to view the goods and customers(Shop ID = Owner ID).
/leave: Leave the shop you are in.
/goods: View the goods in the shop.
/customers: View the customers in the shop.
/users: View all the users in this E-Mall.
/closeshop ShopID: Close a shop.

Hope you have a good time!
Copyright: CHEN Xinkai
    """
    send = threading.Thread(target=serv_self)
    threads.append(send)
    read = threading.Thread(target=serv_recv)
    threads.append(read)

    for t in threads:
        t.start()