#! /usr/bin/env python

import re, time, sys, socket, select
import subprocess as sp

def move_window (wid, x, y):
    newx = max (0, x)
    newx = min (newx, 7425)

    newy = max (0, y)
    newy = min (newy, 1450)

    #print " ".join (["xdotool", "windowmove", wid, str (newx), str (newy)])
    sp.call (["xdotool", "windowmove", wid, str (newx), str (newy)])

    if newx != x or newy != y:
        return False
    else:
        return True

sock = socket.socket ()

host = socket.gethostname ()
port = 64659

try:
    sock.bind ((host, port))
except:
    sock.bind ((host, 0))

print "bound to ", sock.getsockname()[1]

f = open ("PORT", "w")
f.write (str (sock.getsockname()[1]))
f.close ()

sock.setblocking (0)
sock.listen (5)
read_list = [sock]

window_id = "90177551"

mass = 5
v = 0
f = 0

#forces = [[0, 150], [.25, 160], [.73, 200], [1.2, 220], [1.7, 0]]
forces = [[0, 0]]

friction = 150

now = time.time ()
last_time = now
start = now
force_idx = 0
while True:
    now = time.time ()
    dt = now - last_time
    since_start = now - start

    try:
        inp, out, err = select.select (read_list, [], [], 0)
    except Exception as e:
        read_list = [sock]
        continue

    for source in inp:
        if source is sock:
            c, addr = sock.accept ()
            read_list.append (c)
        else:
            data = source.recv (1024)
            if data:
                #print data
                tokens = data.split (",")
                if len (tokens) == 2:
                    start_time = float (tokens[0].strip ())
                    if start_time < 0:
                        start_time = since_start
                elif len (tokens) == 3:
                    start_time = since_start + float (tokens[2])

                forces.append ([start_time, float (tokens[1].strip ())])
                #print "new force: ", forces[-1]
            else:
                source.close ()
                read_list.remove (sock)

    cur_force = forces[force_idx]
    while force_idx < len (forces) - 1 and since_start > forces[force_idx+1][0]:
        force_idx += 1
        cur_force = forces[force_idx]
        #print since_start
        print cur_force

    f = cur_force[1]

    p = sp.Popen (["xdotool", "getwindowgeometry", window_id],
                  stdout=sp.PIPE)
    out, err = p.communicate ()

    lines = out.split ("\n")

    m = re.search ("(\d+),(\d+)", lines[1])

    x = int (m.group (1)) - 1
    y = int (m.group (2)) - 45

    a = f / mass

    v += a * dt

    frict_a = friction / mass
    frict_v = frict_a * dt

    if abs (frict_v) > abs (v):
        v = 0
    else:
        if v > 0:
            v -= frict_v
        else:
            v += frict_v

    #print frict_v

    newx = x + v

    if v != 0:
        if not move_window (window_id, newx, y):
            forces.append ([since_start, 0])
            v = 0

    last_time = now
    time.sleep (.01)
