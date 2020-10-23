# Temperature and humidity monitoring

Monitors the temperature and humidity data of the compute nodes using HDC1080 sensor connected to the RPi. It publishes the data onto the POSIX queue which can be read then by any interested party running on the RPi.

## Installation 
```shell script
sudo apt install python3-pip
sudo apt install libffi-dev
git clone https://github.com/Ormly/ParallelNano_Lisa_Tempo.git
cd ParallelNano_Lisa_Tempo
python3 setup.py install --user
``` 

## Usage
```shell script
cd ParallelNano_Lisa_Tempo/tempo
python3 tempo.py
```

To kill daemon:

```shell script
$ ps -ef | grep tempo
mario       4481    1720  3 10:38 ?        00:00:00 python tempo.py
$ kill 4481
```

## Configuration
Script is configured using the ```config.json``` file residing in the same library.

```json
{
  "queue_id": "/sensor_status",
  "queue_size": 20,
  "interval": 5.0
}
```

* ```queue_id``` - id of the POSIX queue to publish messages on 
* ```queue_size``` - size of the POSIX queue
* ```interval``` - how often the sensor data is measured and published to the POSIX queue in seconds

**Daemon should be restarted to apply changes to config file**

## Message format on POSIX queue
The messages posted onto the POSIX queue are pickled dictionary containing the sensor data.
Sensor data sent is a [pickled](https://docs.python.org/3.6/library/pickle.html) dictionary with the following structure
```json
{
  "current_humidity":"50.0",
  "current_temperature":"25.0",
} 
```

## Used library

For the I2C interface the library `sdl_pi_hdc1080.py` by SwitchDoc Labs is used.
[https://github.com/switchdoclabs/SDL_Pi_HDC1080_Python3]

The file `test_hdc080.py` provides a test for all the functionalities of the library.
