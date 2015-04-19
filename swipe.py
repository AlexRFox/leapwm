#! /usr/bin/env python

import Leap, sys, thread, time, re
import subprocess as sp
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class swipe_listener (Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"

        self.staged_swipes = {}
        self.last_frame = 0
        self.last_time = 0
        self.last_window_id = -1

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        frame = controller.frame()

        now = time.time () * 1000000
        dt = now - self.last_time

        for hand in frame.hands:
            for finger in hand.fingers:
                if finger.type() == 1:
                    pass
                    #print finger.bone(3).next_joint

        for gesture in frame.gestures ():
            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture (gesture)

                if swipe.position[2] > 100:
                    print "dead zone"
                    continue

                if gesture.id not in self.staged_swipes:
                    if now - self.last_frame < 500000 \
                       and self.last_window_id > 0:
                        window_id = self.last_window_id
                    else:
                        p = sp.Popen (["xdotool", "getwindowfocus"],
                                      stdout=sp.PIPE)
                        out, err = p.communicate ()

                        window_id = out.strip ()
                        self.last_window_id = window_id

                    self.staged_swipes[gesture.id] = [0, [], window_id]

                self.staged_swipes[gesture.id][0] += 1
                self.staged_swipes[gesture.id][1].append (swipe)

                if self.last_time == 0:
                    print "foo"
                    continue

                window_id = self.staged_swipes[gesture.id][2]
                for swipe in self.staged_swipes[gesture.id][1]:
                    if self.last_frame == 0:
                        self.last_frame = frame.timestamp
                        print "bar"
                        continue

                    frame_dt = frame.timestamp - self.last_frame
                    self.last_frame = frame.timestamp

                    if frame_dt > 450000:
                        print "baz"
                        continue

                    uspeed = swipe.speed / 1000000

                    dist = uspeed * frame_dt

                    if swipe.direction[0] < 0:
                        dist *= -1

                    gain = 50

                    p = sp.Popen (["xdotool", "getwindowgeometry", window_id],
                                  stdout=sp.PIPE)
                    out, err = p.communicate ()

                    lines = out.split ("\n")

                    if len (lines) < 3:
                        print "quux"
                        continue

                    m = re.search ("(\d+),(\d+)", lines[1])

                    x = int (m.group (1)) - 1
                    y = int (m.group (2)) - 45

                    newx = max (1, int (int (x) + dist * gain))
                    newx = min (newx, 7400)

                    p = sp.call (["xdotool", "windowmove", window_id,
                                  str (newx), str (y)])

                self.staged_swipes[gesture.id][1] = []

        self.last_time = now

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

listener = swipe_listener ()
controller = Leap.Controller ()

controller.add_listener (listener)

while True:
    pass
