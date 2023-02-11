
import subprocess
from LightControl import control
pyscript = f'from LightControl import control; control.turn_light_off({4});control.pi_lights()'
proc = subprocess.Popen(['sudo','python','-c', pyscript], stdin=subprocess.PIPE)
proc.communicate(input=b'server123\n')



