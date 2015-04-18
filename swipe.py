#! /usr/bin/env python

import Leap, sys, thread, time
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

        for gesture in frame.gestures ():
            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture (gesture)

                if gesture.id not in self.staged_swipes:
                    self.staged_swipes[gesture.id] = [0, []]

                self.staged_swipes[gesture.id][0] += 1
                self.staged_swipes[gesture.id][1].append (swipe)

                if self.last_time == 0:
                    continue

                for swipe in self.staged_swipes[gesture.id][1]:
                    if self.last_frame == 0:
                        self.last_frame = frame.timestamp
                        continue

                    frame_dt = frame.timestamp - self.last_frame
                    self.last_frame = frame.timestamp

                    if frame_dt > 10000:
                        continue

                    uspeed = swipe.speed / 1000000

                    dist = uspeed * frame_dt

                    gain = 1

                    print dist * gain

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

print "Press Enter to quit..."
try:
    sys.stdin.readline ()
except KeyboardInterrupt:
    pass
finally:
    controller.remove_listener (listener)
