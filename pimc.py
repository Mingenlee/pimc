#!/usr/bin/env python
#
#
# to do:
#       support no doors and no lights
#
# disable push notice, shutdown process flag
# use python to access instapush
# use python to access InitialState

import RPi.GPIO as GPIO
import time
import picamera
import datetime
import os
import threading
import sys
sys.path.append('../pyconfig')
from pimcconfig import *
#from ISStreamer.Streamer import Streamer

GPIO.setmode(GPIO.BCM)

door_status_open = 0
door_status_close = 1
#
# P2 GPIO information
# GPIO 18, 27, 23, 24, 17, 22, 25, 12, 5, 6, 13, 26 ]
# GPIO GND 6, 9, 14, 20, 25, 30, 34, 39
# GPIO 5V: 2, 4; 3.3V: 1, 17
#
#door_pins = [ 18, 27, 23 ]
door_pins = [ ]
motion1_pin = 18
#light_pins = [ 17, 24 ]
light_pins = [ ]
#run_pin = 25
run_pin = 0

door_names = [ "door1", "door2", "door3", "door4" ]
light_names = [ "door_on", "motion_on" ]
max_delay=40
scp_cmd="scp -p "
bucket_name_value="Door Sendor"
bucket_key_value="door_status"

door_status = [ door_status_open, door_status_open, door_status_open, door_status_open ]
motion_status_on = 1
motion_status_off = 0
motion1_status = motion_status_off

light_status_off = 0
light_status_on = 1
light_status = [ light_status_off, light_status_off ]
light_for_door = 0
light_for_motion = 1

#cam = picamera.PiCamera()
#logger=Streamer(bucket_name=bucket_name_value, bucket_key=bucket_key_value, access_key=access_key_value

delay = 0
vdatetime = ""
vfile = ""
vfilename = ""

def get_hostname():
    return os.uname()[1]

def get_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d__%H.%M.%S")

def getvideopath():
    return os.getcwd() + "/Videos/"

def get_file_name():
    global vdatetime
    vdatetime = get_datetime()
    return getvideopath() + vdatetime + "." + get_hostname() + "."

def getmotionshutdown():
    return os.getcwd() + "/MOTIONSHUTDOWN"
def getmotionpushnotice():
    return os.getcwd() + "/MOTIONPUSHNOTICE"

def get_camera():
    cam = picamera.PiCamera()
#    cam.hflip = True
#    cam.vflip = True
    cam.sharpness = 0
    cam.contrast = 0
    cam.brightness = 50
    cam.saturation = 0
    cam.ISO = 0
    cam.video_stabilization = False
    cam.exposure_compensation = 0
    cam.exposure_mode = 'auto'
    cam.meter_mode = 'average'
    cam.awb_mode = 'auto'
    cam.image_effect = 'none'
    cam.color_effects = None
    cam.rotation = 0
    cam.resolution = (640, 480)
#    cam.resolution = (320, 240)
    cam.framerate = 24
    cam.led = False
    return cam

def transferFile(f, fname):
    global scp_name
    cmd = scp_cmd + fname + scp_name
    cmd_ready = scp_cmd + f + "ready" + scp_name
    cmd1 = "touch " + f + "ready"
    cmd2 = "rm -f " + f + "ready"
    print("%s" % (cmd1))
    os.system(cmd1)
    print("%s" % (cmd));
    os.system(cmd)
    print("%s" % (cmd_ready));
    os.system(cmd_ready)
    os.system(cmd2)

def SendNotice(id, action, ft):
        t2 = threading.Thread(target=pushNotice, args=(id, action, ft))
        t2.start()

def pushNotice(id, action, ft):
    print("id: " + id + ", action: " + action + ", ft: " + ft)
#    logger.log(id, ft)
#    logger.flush()
#    instapush = Instapush(user_token="'" + user_token_value + "'")
#    if (os.path.isfile(getmotionpushnotice()) == True):
#        msg = "'" + id + " " + action + " " + ft + "'"
#        pushRing(msg)
#    else:
#        print("no file: " + getmotionpushnotice() + ", disable push notice")

def init():
    print("Entering Init State...")
    for doorpin in door_pins:
        GPIO.setup(doorpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for lightpin in light_pins:
        GPIO.setup(lightpin, GPIO.OUT)
    if (run_pin != 0):
        GPIO.setup(run_pin, GPIO.OUT)
    GPIO.setup(motion1_pin, GPIO.IN)

#    cam.hflip = True
#    cam.vflip = True
#    cam.sharpness = 0
#    cam.contrast = 0
#    cam.brightness = 50
#    cam.saturation = 0
#    cam.ISO = 0
#    cam.video_stabilization = False
#    cam.exposure_compensation = 0
#    cam.exposure_mode = 'auto'
#    cam.meter_mode = 'average'
#    cam.awb_mode = 'auto'
#    cam.image_effect = 'none'
#    cam.color_effects = None
#    cam.rotation = 0
#    cam.resolution = (640, 480)
#    cam.resolution = (320, 240)
#    cam.framerate = 24
#    cam.led = False
    cam = get_camera()
    cam.close()
    return initStatus()

def initStatus():
    global door_status, door_names, door_pins, light_pins

    for index in range(len(door_pins)):
        if (GPIO.input(door_pins[index]) == True):
            door_status[index] = door_status_open
        else:
            door_status[index] = door_status_close;
    for index in range(len(light_pins)):
        light_off(light_pins[index], " ")
    if (run_pin != 0):
        light_on(run_pin, " ")
#    camera_off(cam)
    if (os.path.isfile(getmotionshutdown()) == True):
        print("Motion Shutdown file exists, please delete it before starting")
        return False
    else:
        print ('Press Ctrl-C to quit.')
        return True

def light_on_off_door(light_pins, light_status, all_door_pins):
    global door_status_open, light_status_on, light_status_off
    temp_light = light_status_off
    if (len(light_pins) <= light_for_door):
        return
    for index in range(len(all_door_pins)):
        if (door_status[index] == door_status_open):
            temp_light = light_status_on
            break;
    if (temp_light == light_status_on and light_status[light_for_door] != light_status_on):
        light_status[light_for_door] = light_status_on
        light_on_door(light_pins[light_for_door])
    if (temp_light == light_status_off and light_status[light_for_door] != light_status_off):
        light_status[light_for_door] = light_status_off
        light_off_door(light_pins[light_for_door])

def light_on_off_motion(light_pins, light_status, motion1_status):
    global light_status_on, light_status_off
    if (len(light_pins) <= light_for_motion):
        return
    if (motion1_status == motion_status_on and light_status[light_for_motion] != light_status_on):
        light_status[light_for_motion] = light_status_on
        light_on_motion(light_pins[light_for_motion])
    if (motion1_status == light_status_off and light_status[light_for_motion] != light_status_off):
        light_status[light_for_motion] = light_status_off
        light_off_motion(light_pins[light_for_motion])

def camera_on():
    global vfile, vfilename, vdatetime
    vfile = get_file_name()
    vfilename = vfile + "h264"
    pushNotice("video", "recording", vdatetime)
    print ("before opening camera ... for file " + vfilename)
#    cam = picamera.PiCamera()
    cam = get_camera()
    print ("... after opening camera")
    cam.start_recording(vfilename)
    print ("camera on, file name: " + vfilename)
    return cam

def camera_off(cam):
    global vfile, vfilename, vdatetime
    if (vfile != ""):
        cam.stop_recording()
        print ("before closing camera ...")
        cam.close()
        print ("... after closing camera")
        t1 = threading.Thread(target=transferFile, args=(vfile, vfilename))
        t1.start()
#        pushNotice("video", "stop", vdatetime)
    print ("camera off")

def light_on_door(lit):
    light_on(lit, " for door")

def light_off_door(lit):
    light_off(lit, " for door")

def light_on_motion(lit):
    light_on(lit, " for motion")

def light_off_motion(lit):
    light_off(lit, " for motion")

def light_on(lit, msg):
    GPIO.output(lit, GPIO.HIGH)
    if (msg != " "):
        print("turn on light" + msg)

def light_off(lit, msg):
    GPIO.output(lit, GPIO.LOW)
    if (msg != " "):
        print("turn off light" + msg)

def loop():
    global mmtion1_pin, motion1_status, light_pins, delay, max_delay
    global cam
    if (os.path.isfile(getmotionshutdown()) == True):
        return False
    for index in range(len(door_pins)):
        if (GPIO.input(door_pins[index]) == True and door_status[index] == door_status_close):
            pushNotice(door_names[index], "open", get_datetime())
            door_status[index] = door_status_open
        if (GPIO.input(door_pins[index]) == False and door_status[index] != door_status_close):
            pushNotice(door_names[index], "close", get_datetime())
            door_status[index] = door_status_close
    light_on_off_door(light_pins, light_status, door_pins)
    if (GPIO.input(motion1_pin) == True):
        if (motion1_status == motion_status_off):
            print("ON camera ........")
            motion1_status = motion_status_on
            delay = 0
            cam = camera_on()
    else:
        delay = delay + 1
        if (delay > max_delay):
            if (motion1_status == motion_status_on):
                print ("motion pin is off ..")
                camera_off(cam)
                motion1_status = motion_status_off
                delay = 0
    light_on_off_motion(light_pins, light_status, motion1_status)
    time.sleep(0.1)
    return True

if __name__ == '__main__':
    try:
        if (init() == True):
            loop_again = True
            while loop_again:
                loop_again = loop()
    finally:
        for index in range(len(light_pins)):
            light_off(light_pins[index], " ")
        if (run_pin != 0):
            light_off(run_pin, " ")
        GPIO.cleanup()
#	cam.close()

