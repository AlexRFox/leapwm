#! /usr/bin/env python

import re, time, sys
import subprocess as sp

def move_window (wid, x, y):
    sp.call (["xdotool", "windowmove", wid, str (x), str (y)])

window_id = "71303183"

mass = 5
v = 0
f = 200

forces = [[0, 150], [.25, 160], [.73, 200], [1.2, 220], [1.7, 0]]

friction = 100

now = time.time ()
last_time = now
start = now
force_idx = 0
while True:
    now = time.time ()
    dt = now - last_time
    since_start = now - start

    cur_force = forces[force_idx]
    if force_idx < len (forces) - 1:
        next_force = forces[force_idx+1]

        if since_start > next_force[0]:
            force_idx += 1
            cur_force = next_force

    f = cur_force[1]

    p = sp.Popen (["xdotool", "getwindowgeometry", window_id],
                  stdout=sp.PIPE)
    out, err = p.communicate ()

    lines = out.split ("\n")

    m = re.search ("(\d+),(\d+)", lines[1])

    x = int (m.group (1)) - 1
    y = int (m.group (2)) - 45

    a = f / mass

    if v > 0:
        frict_a = friction / mass
    else:
        frict_a = 0

    if a < 0:
        frict_a *= -1

    v += a * dt
    v -= frict_a * dt

    if v < 0:
        v = 0

    newx = x + v

    move_window (window_id, newx, y)

    last_time = now
    time.sleep (.01)
