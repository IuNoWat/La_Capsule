import time

# This library is an example on how to use picod. It allow to read the first analog input (A0) of a slave raspberry pico

import picod

pico=picod.pico()

while True :
    print(pico.adc_read(0))

#for i in range(0,10) :
#    pico.gpio_write(25,1)
#    time.sleep(1)
#    pico.gpio_write(25,0)
#    time.sleep(1)
