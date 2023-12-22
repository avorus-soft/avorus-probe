import time
import socket
import logging

import click
import paho.mqtt.client as mqtt
import sd_notify


from probe import Probe
from misc import get_config, logger


class App:
    def __init__(self,
                 config,
                 mqtt_hostname,
                 mqtt_port,
                 ca_certificate,
                 certfile,
                 keyfile,
                 notify):
        self.mqtt_hostname = mqtt_hostname
        self.mqtt_port = mqtt_port
        self.config = config
        self.ca_certificate = ca_certificate
        self.certfile = certfile
        self.keyfile = keyfile
        self.notify = notify
        self.notify_enabled = notify.enabled()
        self._fqdn = socket.getfqdn()

    @property
    def fqdn(self):
        fqdn = socket.getfqdn()
        if fqdn != self._fqdn:
            self.stop()
            self._fqdn = fqdn
            raise Exception('FQDN change detected. Retrying.')
        return fqdn

    def run(self):
        _setting_up = True
        while _setting_up:
            try:
                logger.info('FQDN: %s', self.fqdn)
                self.mqtt_client = mqtt.Client(client_id=self.fqdn)
                self.mqtt_client.enable_logger(logger)

                logger.info('MQTT TLS: %s %s %s', self.ca_certificate, self.certfile, self.keyfile)
                self.mqtt_client.tls_set(
                    self.ca_certificate,
                    self.certfile,
                    self.keyfile
                )

                self.probe = Probe(self.fqdn,
                                   client=self.mqtt_client,
                                   config=self.config,
                                   logger=logger)
                _setting_up = False
            except Exception as e:
                logger.exception(e)
                time.sleep(5)

        while True:
            try:
                self.probe.start()

                if self.notify_enabled:
                    self.notify.status('Connecting...')

                logger.info('Connecting MQTT Host: %s:%s', self.mqtt_hostname, self.mqtt_port)
                self.mqtt_client.connect(self.mqtt_hostname, self.mqtt_port, 60)
                self.mqtt_client.loop_start()
                
                if self.notify_enabled:
                    self.notify.ready()
                    self.notify.status('Connected.')
                
                if self.notify_enabled:
                    self.notify.notify()
                time.sleep(3)
                
                while self.probe.is_connected:
                    logger.info('FQDN: %s', self.fqdn)
                    time.sleep(5)
                    if self.notify_enabled:
                        self.notify.notify()

                logger.debug('Probe is not connected')
                self.stop()
            except Exception as e:
                logger.exception(e)
                if self.notify_enabled:
                    self.notify.status('Failed.')
                    self.notify.notify()
                self.stop()
                self.run()
            time.sleep(5)


    def stop(self):
        if self.mqtt_client.is_connected():
            self.mqtt_client.disconnect()
        if self.probe._running:
            self.probe.stop()
            self.probe.join()


@click.command()
@click.option('--config_file', type=str, required=True)
@click.option('--mqtt_hostname', type=str, required=True)
@click.option('--mqtt_port', type=int, default=8883)
@click.option('--ca_certificate', type=str, required=True)
@click.option('--certfile', type=str, required=True)
@click.option('--keyfile', type=str, required=True)
@click.option('--loglevel', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], case_sensitive=False), default='CRITICAL')
def main(
        config_file,
        mqtt_hostname,
        mqtt_port,
        ca_certificate,
        certfile,
        keyfile,
        loglevel):

    logging.basicConfig(level=getattr(logging, loglevel, 'WARNING'),
                        format='%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

    notify = sd_notify.Notifier()
    notify_enabled = notify.enabled()

    if notify_enabled:
        notify.status('Startup...')

    config = get_config(config_file)
    logger.info('Config: %s', config)

    app = App(config,
              mqtt_hostname,
              mqtt_port,
              ca_certificate,
              certfile,
              keyfile,
              notify)
    app.run()


if __name__ == '__main__':
    main()
