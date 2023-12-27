# Avorus-Probe

Avorus-probe is a critical software component of the Avorus suite designed to be installed on computers within AV/Digital Media installations. It enables these computers to communicate with the manager service of an Avorus deployment, providing real-time control, reporting as health and status metrics back to the system.

## Features

- **MQTT Integration:** Establishes a secure client connection to an MQTT broker for telemetry and command message exchange.
- **Service Watchdog:** Utilizes `sd_notify` for systemd service notification support, keeping the system manager informed about the service's state.
- **Dynamic Configuration:** Supports loading configurations from a file for tailored operations on different systems.
- **Resilience:** Built-in retry mechanism that ensures steady operation despite intermittent network issues or exceptions.
- **Secure Communication:** Leverages TLS for secure MQTT communication, ensuring confidentiality and integrity of messages.
- **Runtime Status:** Regular log output for monitoring the fully qualified domain name (FQDN) of the host and connection status to the MQTT broker.

## System Requirements

- A machine running within an AV/Digital Media installation with network access to the MQTT broker set up for Avorus.
- Python 3.x environment with required packages installed.

## Installation

1. Ensure Python 3.x is installed on the target machine.
2. Install required Python packages using `pip install -r requirements.txt`.
3. Place `src` in the desired directory.
4. Place certificates and private key in the desired directory.
5. Configure system service (if needed) to manage the avorus-probe lifecycle.

## Usage

Run `app.py` via the command line or set it as a service with the following mandatory options:

- `--config_file`: Path to the configuration file.
- `--mqtt_hostname`: Hostname of the MQTT Broker.
- `--mqtt_port`: Port number of the MQTT Broker (default: 8883).
- `--ca_certificate`: Path to the CA certificate for TLS.
- `--certfile`: Path to the client's certificate file for TLS.
- `--keyfile`: Path to the client's key file for TLS.
- `--loglevel`: Logging level (CRITICAL, ERROR, WARNING, INFO, DEBUG).

## Configuration

`--config_file` is expected to contain two variables with comma seperated values.

`PROBE_METHODS` are the methods that are being run periodically, their result being sent via MQTT to the manager.

`PROBE_CAPABILITIES` are reported to the manager and define which methods can be run on this instance of the probe.

### Available `PROBE_METHODS`

| Method name      | Description                                  | Linux | Windows |
| ---------------- | -------------------------------------------- | ----- | ------- |
| ping             | Signal that the device is alive              | ✅    | ✅      |
| uptime           | Time since boot                              | ✅    | ❌      |
| fans             | Fan speeds (lm_sensors)                      | ✅    | ❌      |
| temperatures     | CPU temps (lm_sensors)                       | ✅    | ❌      |
| display          | Display resolution and refresh rate (xrandr) | ✅    | ❌      |
| is_muted         | Audio mute                                   | ✅    | ✅      |
| easire           | Health state of the easire client            | ✅    | ❌      |
| mpv_file_pos_sec | Playback position of the mpv player          | ✅    | ❌      |

### Available `PROBE_CAPABILITIES`

| Method name | Description          | Linux | Windows |
| ----------- | -------------------- | ----- | ------- |
| wake        | Wake the device      | ✅    | ✅      |
| shutdown    | Shut down the device | ✅    | ✅      |
| reboot      | Reboot the device    | ✅    | ✅      |
| mute        | Mute the audio       | ✅    | ✅      |
| unumute     | Unmute the audio     | ✅    | ✅      |

Example userconfig.txt:

```bash
PROBE_METHODS="ping,fans,temperatures,uptime,display,is_muted"
PROBE_CAPABILITIES="wake,shutdown,reboot,mute,unmute"
```

Example command:

```bash
python app.py \
    --config_file "/path/to/userconfig.txt" \
    --mqtt_hostname "mqtt.example.com" \
    --mqtt_port 8883 \
    --ca_certificate "/path/to/ca.pem" \
    --certfile "/path/to/client_key.pem" \
    --keyfile "/path/to/client_key.pem" \
    --loglevel INFO
```

## Contact and Support

For any issues or support related to Avorus-probe, refer to the main Avorus repository issues section or the support forums.

## Contributions

Contributions to Avorus-probe are welcome. Please follow the contribution guidelines outlined in the main Avorus repository.
