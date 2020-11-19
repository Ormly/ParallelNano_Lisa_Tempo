#imports

import sdl_pi_hdc1080

# Main Program

hdc1080 = sdl_pi_hdc1080.SDL_Pi_HDC1080()

# read temperature
print ("Temperature = %3.1f C" % hdc1080.readTemperature())
# read humdity
print ("Humidity = %3.1f %%" % hdc1080.readHumidity())
