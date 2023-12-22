from typing import Union, Any, Tuple
import shlex
import json
import logging

logger = logging.getLogger()


def get_config(config_file):
    config = {}
    try:
        with open(config_file) as f:
            for line in shlex.split(f.read()):
                var, _, value = line.partition('=')
                config[var] = value
    except Exception as e:
        logger.error('Loading config %s', e)
    return config


def parse_payload(payload: bytes) -> Tuple[list, dict]:
    args = []
    kwargs = {}
    try:
        arguments = json.loads(payload)
        if 'args' in arguments:
            args = arguments.args
        if 'kwargs' in arguments:
            kwargs = arguments.kwargs
    except json.JSONDecodeError:
        pass
    return args, kwargs


def make_response(
    data: Union[None,dict]=None,
    error: Union[None,dict]=None) -> str:
    response: dict[str, Any] = {}
    if data is not None:
        response['data'] = data
    if error is not None:
        response['error'] = error
    return json.dumps(response)


def error_response(status):
    return make_response(data={'status': 'complete', 'result': status})
