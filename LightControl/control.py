import time
NUMBER_OF_LIGHTS = 30

#include all necessary packages to get LEDs to work with Raspberry Pi
import board
import neopixel,os
import subprocess

lights_array = NUMBER_OF_LIGHTS*[0]
pixels = neopixel.NeoPixel(board.D18, NUMBER_OF_LIGHTS, brightness=1)
def pi_lights():
    for i in range(NUMBER_OF_LIGHTS):
        if(lights_array[i]==1):
            pixels[i] = [255,255,255]
        else:
            pixels[i] = [0,0,0]

def turn_light_on(index):
    lights_array[index] = 1

def turn_light_off(index):
    lights_array[index] = 0
