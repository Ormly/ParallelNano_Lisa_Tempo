"""
The sensor component of the monitoring system
"""
from typing import Dict
import json
import sys
import os
import signal
import time

from ipcqueue import posixmq
import daemon
import sdl_pi_hdc1080


class ConfigFileInvalidError(Exception):
    """
    Should be raised to indicate an invalid config file structure
    """
    pass


class SensorData:
    """
    puts the sensor info onto the IPC queue
    """
    def __init__(self, queue_id: str, queue_size: int, interval: float):
        self.queue_id = queue_id
        self.queue_size = queue_size
        self.interval = interval

        self.ipc_queue: posixmq.Queue

        self._init_queue()
        self._sensor_info: Dict[str, str] = {}
        self._hdc1080 = sdl_pi_hdc1080.SDL_Pi_HDC1080()
        self._hdc1080.setTemperatureResolution(sdl_pi_hdc1080.HDC1080_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
        self._hdc1080.setHumidityResolution(sdl_pi_hdc1080.HDC1080_CONFIG_HUMIDITY_RESOLUTION_14BIT)

    def _init_queue(self):
        if not (isinstance(self.queue_id, str) and self.queue_id.startswith("/") and len(self.queue_id) < 255):
            raise ValueError("Invalid queue id")
        self.ipc_queue = posixmq.Queue(name=self.queue_id)

    def start(self):
        """
        post sensor data on the IPC queue
        If full, do nothing else
        :return:
        """
        while True:
            self._sensor_info['current_humidity'] = self._hdc1080.readHumidity()
            self._sensor_info['current_temperature'] = self._hdc1080.readTemperature()
            try:
                self.ipc_queue.put_nowait(self._sensor_info)
            except posixmq.queue.Full:
                # queue is full -> nobody's listening on the other side. nothing to do.
                pass
            time.sleep(self.interval)

    def cleanup(self):
        """
        clean up the queue
        :return:
        """
        if self.ipc_queue:
            self.ipc_queue.close()

class ConfigFactory:
    """
    Reads the config from a validated config file
    """
    def from_config_file(self, filepath: str) -> SensorData:
        with open(filepath, 'r') as f:
            config = json.load(f)
            self._validate_config_file(config)
            queue_id = config['queue_id']
            queue_size = config['queue_size']
            interval = config['interval']

            return SensorData(queue_id=queue_id, queue_size=queue_size, interval=interval)

    @staticmethod
    def _validate_config_file(config: Dict):
        """
        check that config file contains all mandatory fields and raise a ConfigFileInvalidError if not
        :param config:
        :return:
        """
        if not isinstance(config, dict):
            raise ConfigFileInvalidError("Config file is not a valid dictionary")
        if "queue_id" not in config.keys():
            raise ConfigFileInvalidError("queue_id missing in config file")
        if "queue_size" not in config.keys():
            raise ConfigFileInvalidError("queue_size missing in config file")
        if "interval" not in config.keys():
            raise ConfigFileInvalidError("interval missing in config file")


def main(daemon_context: daemon.DaemonContext):
    factory = ConfigFactory()
    sensor_data = factory.from_config_file("config.json")

    # set termination callback
    daemon_context.signal_map[signal.SIGTERM] = sensor_data.cleanup
    sensor_data.start()


if __name__ == '__main__':
    # TODO: optionally get config file path from stdin
    config_file = open("config.json", 'r')

    with daemon.DaemonContext(
        files_preserve=[config_file],
        chroot_directory=None,
        stderr=sys.stderr,  # if any, errors shall be printed to stderr
        working_directory=os.getcwd()
    ) as context:
        # start beacon_server as daemon
        main(context)