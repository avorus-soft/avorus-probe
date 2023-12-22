import os
import platform
import subprocess
from .sensors import temperatures, fans, boot_time, uptime, mpv_file_pos_sec, display, easire
from misc import logger, parse_payload, make_response


def call_method(method, *args, **kwargs):
    try:
        result = method(*args, **kwargs)
        response = make_response(
            data=dict(status='complete', result=result)
        )
    except Exception as e:
        response = make_response(
            error=dict(
                message=type(e).__name__,
                errors=e.args
            )
        )
    return response


def shutdown():
    result = os.system('shutdown now')
    if result != 0:
        raise Exception(result)


def reboot():
    result = os.system('reboot now')
    if result != 0:
        raise Exception(result)


def ping():
    return


def get_audio_device():
    try:
        from alsaaudio import pcms
        pcms = pcms()
        if 'pipewire' in pcms or 'pulseaudio' in pcms:
            return 'pipewire' if 'pipewire' in pcms else 'pulseaudio'
        else:
            return False
    except:
        False


def is_muted():
    if platform.system() == 'Linux':
        device = get_audio_device()
        if device:
            from alsaaudio import Mixer
            mixer = Mixer(device=device)
            return mixer.getmute()[0]
        else:
            p = subprocess.run(
                'mpv_control get_mute', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            if p.returncode == 0:
                return int(p.stdout.strip().decode())
    else:
        result = subprocess.run(
            ['sc', 'query', 'audiosrv'], capture_output=True, text=True)
        return 'RUNNING' not in result.stdout


def mute():
    if platform.system() == 'Linux':
        device = get_audio_device()
        if device:
            from alsaaudio import Mixer
            mixer = Mixer(device=device)
            mixer.setmute(True, 0)
        else:
            subprocess.run('mpv_control set_mute 1',
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    else:
        subprocess.run('net stop audiosrv')


def unmute():
    if platform.system() == 'Linux':
        device = get_audio_device()
        if device:
            from alsaaudio import Mixer
            mixer = Mixer(device=device)
            mixer.setmute(False, 0)
        else:
            subprocess.run('mpv_control set_mute 0',
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    else:
        subprocess.run('net start audiosrv')
