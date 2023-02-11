import time
NUMBER_OF_LIGHTS = 10

lights_array = NUMBER_OF_LIGHTS*[0]

def pi_lights():
    for i in range(NUMBER_OF_LIGHTS):
        if(lights_array[i]==1):
            print(f"Light on at index-{i+1}")
        else:
            print(f"Light off at index-{i+1}")

def turn_light_on(index):
    lights_array[index] = 1

def turn_light_off(index):
    lights_array[index] = 0

# turn_light_on(0)
# pi_lights()
# time.sleep(5)
# turn_light_off(0)
# pi_lights()
        