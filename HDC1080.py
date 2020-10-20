from typing import Dict, Tuple
import os
import sys
import socket
import time
import pickle
import json

import daemon          
import SDL_Pi_HDC1080


class ConfigFileInvalidError(Exception):
    pass


class SensorInformation:
    """
    Represents a collection of sensor information that can be updated and serialized
    """
    def __init__(self):
        self._sensor_info: Dict[str, str] = {}
        hdc1080 = SDL_Pi_HDC1080.SDL_Pi_HDC1080()
        hdc1080.setTemperatureResolution(SDL_Pi_HDC1080.HDC1080_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
        hdc1080.setHumidityResolution(SDL_Pi_HDC1080.HDC1080_CONFIG_HUMIDITY_RESOLUTION_14BIT)

    def update_and_serialize(self) -> bytes:
        """
        Load updated sensor information and return it in serialized form
        :return:
        """
        self._update()
        return self._serialize()


    def _update(self):
        """
        Loads the dynamic components of sensor info, has to be called before requesting updated information
        """
        self._sensor_info['cur_temp'] = hdc1080.readTemperature()
		self._sensor_info['cur_hum'] = hdc1080.readHumidity()

    def _serialize(self) -> bytes:
        """
        Returns a bytes representation of the sensor information
        :return:
        """
        return pickle.dumps(self._sensor_info)


class Beacon:
    """
    Cyclically sends updated sensor information over the given socket
    """
    def __init__(self, ip_port: Tuple[str, int], interval: float):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip_port = ip_port
        self.interval = interval
        self._sensor_info = SensorInformation()

    def start(self):
        while True:
            payload = self._sensor_info.update_and_serialize()
            self._send_sensor_info(payload)
            time.sleep(self.interval)

    def _send_sensor_info(self, payload: bytes):
        sent_bytes = 0

        # not all bytes might get sent after first call
        while sent_bytes < len(payload):
            sent_bytes += self.sock.sendto(payload, self.ip_port)


class BeaconFactory:
    """
    Creates a beacon object from a config file
    """
    def from_config_file(self, filepath: str) -> Beacon:
        with open(filepath, 'r') as f:
            config = json.load(f)
            self._validate_config_file(config)
            ip = config['server_ip']
            port = config['server_port']
            interval = config['interval']

            return Beacon(ip_port=(ip, port), interval=interval)

    @staticmethod
    def _validate_config_file(config: Dict):
        """
        check that config file contains all mandatory fields and raise a ConfigFileInvalidError if not
        :param config:
        :return:
        """
        if not isinstance(config, dict):
            raise ConfigFileInvalidError("Config file is not a vaild dictionary")
        if "server_ip" not in config.keys():
            raise ConfigFileInvalidError("server_ip missing in config file")
        if "server_port" not in config.keys():
            raise ConfigFileInvalidError("server_port missing in config file")
        if "interval" not in config.keys():
            raise ConfigFileInvalidError("interval missing in config file")


def main():
    factory = BeaconFactory()
    beacon = factory.from_config_file("config.json")
    beacon.start()


if __name__ == '__main__':
    # start beacon as daemon
    # TODO: optionally get config file path from stdin
    config_file = open("config.json", 'r')
    with daemon.DaemonContext(
            files_preserve=[config_file],
            chroot_directory=None,
            stderr=sys.stderr,  # if any, errors shall be printed to stderr
            working_directory=os.getcwd()
    ):
        main()