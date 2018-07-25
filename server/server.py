import os
import sys
import time
import socket
import random
import threading

if not os.path.exists('accounts'):
    os.system('mkdir accounts')
if not os.path.exists('rooms'):
    os.system('mkdir rooms')
open('online_users', 'w')

HOST = ''
PORT = 8888
 
os.system('fuser -k ' + str(PORT) + '/tcp')
print

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

s.listen(10)

def login(log, pas):
    if log in logins and logins[log] == pas:
        return True
    return False

def logins_info():
    global logins
    logins = {}
    for i in os.listdir('accounts'):
        current_user = open('accounts/' + i).read().splitlines()
        logins[current_user[0]] = current_user[1]

def rm_if_afk(x):
    ret = []
    now = open('online_users').read().splitlines()
    ret.append(x + ',' + str(time.time()))
    for i in now:
        if time.time() - float(i.split(',')[1]) < 3:
            if not i.startswith(x):
                ret.append(i)
        else:
            remove_from_rooms(i.split(',')[0])
    file = open('online_users', 'w')
    file.write('\n'.join(ret))

def online_users(x):
    rm_if_afk(x)
    return [i.split(',')[0] for i in open('online_users').read().splitlines()]

def add_online_user(name, action):
    currently_online = open('online_users').read().splitlines()

    if action == 'put':
        if not name in currently_online:
            currently_online.append(name + ',' + str(time.time()))

    elif action == 'rm':
        currently_online = [i for i in currently_online if not i.startswith(name)]

    file = open('online_users', 'w')
    file.write('\n'.join(currently_online))
    file.close()

def nick_of_login(x):
    for i in os.listdir('accounts'):
        if open('accounts/' + i).read().splitlines()[0] == x:
            return i

def random_bombs(info):
    y, x, b = info[0], info[1], info[2]
    grid = [
        [0 for j in range(x)]
        for i in range(y)
        ]
    bombs_locations = random.sample(xrange(y*x), b)
    for i in bombs_locations:
        grid[i/(x)][i%(x)] = 1
    return grid

logins = {}

def bombs_around(bombs, h, w):
    to_check = [
        [i, j]
        for i in range(h-1, h+2) 
        for j in range(w-1, w+2) 
        if 
        0 <= i < len(bombs) and 
        0 <= j < len(bombs[0]) and
        not (i == h and j == w) and
        (bombs[i][j] == 0 or
        bombs[i][j] == 1)
    ]
    amount_of_bombs = 0
    for i in to_check:
        if bombs[i[0]][i[1]] == 1:
            amount_of_bombs += 1
    return [amount_of_bombs, to_check]

def starting_point(bombs):
    for y_idx, y in enumerate(bombs):
        for x_idx, x in enumerate(y):
            if bombs[y_idx][x_idx] == 0:
                checked = bombs_around(bombs, y_idx, x_idx)
                if len(checked[1]) == 8 and checked[0] == 0:
                    return [y_idx, x_idx, 1]

def remove_from_rooms(x):
    for i in os.listdir('rooms'):
        info = eval(open('rooms/' + i).read())
        if i == x:
            os.system('rm rooms/' + i)
        else:
            if x in info['users']:
                info['users'].remove(x)
                file = open('rooms/' + i, 'w')
                file.write(str(info))
                file.close()

def room_info(x):
    info = eval(open('rooms/' + x).read())
    return {'host': info['host'],
            'size': info['size'],
            'users': info['users'],
            'game_status': True}

def rooms():
    ret = []
    for j in [eval(open('rooms/' + i).read()) for i in os.listdir('rooms')]:
        if not j['status']:
            ret.append({'host': j['host'],
                        'size': j['size'],
                        'users': len(j['users'])})
    return ret

def clientthread(conn, ip):
    logins_info()
    this_user = ''
    while True:
        data = conn.recv(1024)
        logins_info()
        fine = False

        try:
            data = eval(data)
            fine = True
        except:
            reply = {'validate': False, 'status': False}

        if fine:
            print data['action']
            if data['action'] == 'sign_up':
                if not data['nick'] in os.listdir('accounts') and not data['username'] in logins:
                    file = open('accounts/' + data['nick'], 'w')
                    file.write(data['username'] + '\n' + data['password'] + '\n')
                    file.close()
                    this_user = data['nick']
                    add_online_user(this_user, 'put')
                    reply = {'validate': True, 'status': True, 'nick': nick_of_login(data['username'])}
                else:
                    reply = {'validate': True, 'status': False}

            elif data['action'] == 'sign_in':
                if login(data['username'], data['password']):
                    this_user = nick_of_login(data['username'])
                    remove_from_rooms(this_user)
                    add_online_user(this_user, 'put')
                    reply = {'validate': True, 'status': True, 'nick': nick_of_login(data['username'])}
                else:
                    reply = {'validate': True, 'status': False}

            elif data['action'] == 'online_users':
                reply = {'online_users': online_users(data['nick'])}

            elif data['action'] == 'create_room':
                this_user = data['nick']
                file = open('rooms/' + this_user, 'w')
                file.write(str({'host': this_user,
                            'size': data['size'],
                            'users': [this_user],
                            'status': False,
                            'bombs_map': [],
                            'moves': {},
                            'ended': []}))
                file.close()
  
            elif data['action'] == 'join_room':
                this_user = data['login']
                game_host = data['host']

                if os.path.isfile('rooms/' + game_host):
                    r = eval(open('rooms/' + game_host).read())
                    if r['status'] == False and len(r['users']) < 4 and not this_user in r['users']:
                        r['users'].append(this_user)
                        file = open('rooms/' + game_host, 'w')
                        file.write(str(r))
                        file.close()
                        reply = {'status': True}
                    else:
                        reply = {'status': False}
                else:
                    reply = {'status': False}

            elif data['action'] == 'show_room':
                rm_if_afk(data['me'])
                host = data['host']
                if host in os.listdir('rooms'):
                    reply = room_info(host)
                else:
                    reply = {'game_status': False}

            elif data['action'] == 'start_game':
                sizes = [[10, 10, 10], [16, 16, 40], [16, 30, 99]]
                info = eval(open('rooms/' + data['host']).read())
                info['bombs_map'] = random_bombs(sizes[int(info['size'])])
                start = starting_point(info['bombs_map'])
                info['status'] = True
                for i in info['users']:
                    info['moves'][i] = [start]
                file = open('rooms/' + data['host'], 'w')
                file.write(str(info))
                file.close()
                
            elif data['action'] == 'show_game':
                rm_if_afk(data['me'])
                reply = {}
                if os.path.isfile('rooms/' + data['host']):
                    reply = eval(open('rooms/' + data['host']).read())

            elif data['action'] == 'game_move':
                s = 'rooms/' + data['host']
                if os.path.isfile(s) and eval(open(s).read())['status']:
                    info = eval(open(s).read())
                    if 'action2' in data:
                        info['ended'].append(data['me'])
                    info['moves'][data['me']].append(data['move'])
                    if all(i in info['ended'] for i in info['users']):
                        info['status'] = False
                    file = open(s, 'w')
                    file.write(str(info))
                    file.close()

            elif data['action'] == 'game_status':
                reply = {'game_status': False}
                if data['host'] in os.listdir('rooms') and eval(open('rooms/' + data['host']).read())['status']:
                    reply = {'game_status': True}

            elif data['action'] == 'exit_room':
                remove_from_rooms(data['nick'])

            elif data['action'] == 'show_rooms':
                reply = rooms()

        if not data:
            if this_user != '':
                add_online_user(this_user, 'rm')
                remove_from_rooms(this_user)
            break
        else:
        	conn.sendall(str(reply))
    conn.close()

while True:
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    my_thread = threading.Thread(target=clientthread, args=(conn,addr))
    my_thread.setDaemon(True)
    my_thread.start()
 
s.close()
