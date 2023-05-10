import time


#include all necessary packages to get LEDs to work with Raspberry Pi
import board
import neopixel,os
import subprocess
import pickle

NUMBER_OF_LIGHTS = 30

pixels = neopixel.NeoPixel(board.D18, NUMBER_OF_LIGHTS, brightness=1)

# def pi_lights():
#     for i in range(NUMBER_OF_LIGHTS):
#         if(lights_array[i]==1):
#             pixels[i] = [255,255,255]
#         else:
#             pixels[i] = [0,0,0]

def turn_light_on(index):
    pixels[index] = [255,255,255]

def turn_light_off(index):
    pixels[index] = [0,0,0]
