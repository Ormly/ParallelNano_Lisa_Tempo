# Temperature and humidity monitoring

Monitors the temperature and humidity data using HDC1080 sensor connected to the RPi.

## Used library

For the I2C interface the library `SDL_Pi_HDC1080.py` by SwitchDoc Labs is used.
[https://github.com/switchdoclabs/SDL_Pi_HDC1080_Python3]

The file `testHDC1080.py` provides a test for all the functionalities of the library.

## Usage

The file `HDC1080.py` configures the sensor and measures both the temperature and the humidity every 5 seconds.
