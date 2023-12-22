import time
from threading import Thread
from typing import Union, Callable
import logging
from inspect import getmembers, isfunction

from paho.mqtt.client import Client, SubscribeOptions, MQTTMessage


from misc import error_response, logger, parse_payload, make_response
import methods
from methods import call_method


class Probe(Thread):
    def __init__(self,
                 fqdn: str,
                 client: Client,
                 config: dict,
                 logger: logging.Logger):
        super().__init__(target=self.run, daemon=True)
        self.fqdn = fqdn
        self.client = client
        self.config = config

        self._running = False

        self.is_connected = False
        self.playback_pos = None
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        try:
            periodic_methods = self.config['PROBE_METHODS'].split(',')
        except:
            logger.critical('No PROBE_METHODS in userconfig.txt')
            periodic_methods = []

        try:
            self.capabilities = self.config['PROBE_CAPABILITIES']
        except:
            logger.critical('No PROBE_CAPABILITIES in userconfig.txt')
            self.capabilities = 'wake,shutdown,reboot'

        self.methods = {name: function for name, function in getmembers(
            methods, isfunction) if name in periodic_methods}
        self.errors = {}

    def check_playback_pos(self):
        new_playback_pos = methods.mpv_file_pos_sec()
        if new_playback_pos == self.playback_pos:
            self.errors['playback'] = 'error'
        else:
            self.errors['playback'] = 'ok'
        self.playback_pos = new_playback_pos

    def check_display(self):
        display = methods.display()
        if display != None:
            self.errors['display'] = 'ok'
        else:
            self.errors['display'] = 'error'

    def check_easire(self):
        display = methods.easire()
        if display != None:
            self.errors['easire'] = 'ok'
        else:
            self.errors['easire'] = 'error'

    def call_methods(self):
        self.client.publish(
            f'probe/{self.fqdn}/capabilities', self.capabilities)
        for name, method in self.methods.items():
            try:
                if name == 'mpv_file_pos_sec':
                    self.check_playback_pos()
                elif name == 'display':
                    self.check_display()
                elif name == 'easire':
                    self.check_easire()
                else:
                    self.client.publish(
                        f'probe/{self.fqdn}/{name}', call_method(method))
                self.client.publish(
                    f'probe/{self.fqdn}/errors', error_response(self.errors))
            except:
                logger.exception(name)

    def run(self):
        self._running = True
        while self._running:
            if self.is_connected:
                self.call_methods()
            time.sleep(5)

    def stop(self):
        self._running = False

    def on_connect(self, client: Client, *args):
        logger.info('Connected %s', args)
        self.is_connected = True
        client.publish(f'probe/{self.fqdn}/connected')
        self.client.publish(
            f'probe/{self.fqdn}/capabilities', self.capabilities)
        self.client.publish(
            f'probe/{self.fqdn}/boot_time', call_method(methods.boot_time))
        client.subscribe(
            f'manager/{self.fqdn}/#',
            options=SubscribeOptions(noLocal=True)
        )

    def on_disconnect(self, _, *args):
        logger.info('Disconnected %s', args)
        self.is_connected = False

    def on_message(self, client: Client, userdata, msg: MQTTMessage):
        method_name = msg.topic.split('/')[2]
        logger.info('Received method %s', method_name)
        method: Union[Callable, None] = getattr(methods, method_name, None)
        response = make_response(data=dict(status='received'))
        client.publish(f'probe/{self.fqdn}/{method_name}', response)
        if method is None:
            response = make_response(
                error=dict(message='Unknown method')
            )
        else:
            args, kwargs = parse_payload(msg.payload)
            response = methods.call_method(method, *args, **kwargs)
        logger.debug(response)
        client.publish(f'probe/{self.fqdn}/{method_name}', response)
