import subprocess
import psutil


def temperatures():
    sensors = psutil.sensors_temperatures()
    return {key: [temp._asdict() for temp in sensor] for key, sensor in sensors.items()}


def fans():
    sensors = psutil.sensors_fans()
    return {key: [fan._asdict() for fan in sensor] for key, sensor in sensors.items()}


def boot_time():
    boot_time = psutil.boot_time()
    return boot_time


def uptime():
    with open('/proc/uptime', 'r') as f:
        return float(f.read().split(' ')[0])


def mpv_file_pos_sec():
    p = subprocess.run('mpv_control file_pos_sec',
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if p.returncode == 0:
        try:
            return int(p.stdout.strip().decode())
        except:
            return 0


def display():
    p = subprocess.run(
        'xrandr', env={'DISPLAY': ':0'}, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode == 0:
        mode = [line for line in p.stdout.decode().splitlines() if '*' in line]
        if len(mode) > 0:
            mode = mode[0]
            mode = ' '.join(mode.split()).split(' ')
            resolution = mode[0]
            rate = ''.join([c for c in mode[1] if c.isdigit() or c == '.'])
            return f'{resolution}, {rate} Hz'


def easire():
    p = subprocess.run('ps ax | grep -q [e]asire-player',
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if p.returncode == 0:
        return True
