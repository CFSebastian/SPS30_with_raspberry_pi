
import logging.handlers
import time
import json
import os
import subprocess
import signal
import sys
from tb_gateway_mqtt import TBDeviceMqttClient

ACCESS_TOKEN = "7tUZaVu6iZFxLUcYRc53"
THINGSBOARD_SERVER = 'demo.thingsboard.io'

logging.basicConfig(level=logging.DEBUG)

client = None
sensor_proc = None

global is_power_on
is_power_on = True

sps_attributes = {}

# callback pentru a schimba perioada de interogare
period = 1.0

def parse_sensor_data(lines):
    try:
        attributes = {}
        for line in lines:
            data = json.loads(line)
            attributes.update(data)
        return attributes
    except Exception as e:
        print("Parse error (attributes):", e)
        return {}

def parse_sensor_reading(lines):
    try:
        telemetry = {}
        for line in lines:
            data = json.loads(line)
            telemetry.update(data)
        return telemetry
    except Exception as e:
        print("Parse error (telemetry):", e)
        return {}

def attribute_callback(result, _):
    global period
    period = result.get('blinkingPeriod', 1.0)

def rpc_callback(id, request_body):
    global is_power_on
    global sps_attributes
    method = request_body.get('method')
    if method == 'getState':
        client.send_rpc_reply(id,{"result":is_power_on})
    elif method == 'setState':
        params = request_body.get("params",False)
        if(params):  
            sps_attributes.update(start_sensor_process())
            is_power_on = True
        else:
            stop_sensor_process()
            is_power_on = False
        
    else:
        print('Unknown method:', method)

def start_sensor_process():
    global sensor_proc
    sensor_proc = subprocess.Popen("./sps30-uart-3.1.0/connect_python_sps",
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   bufsize=1
                                   )
    try:
        # Trimite o comandă de inițializare ca să primești date utile
        sensor_proc.stdin.write("read\n")
        sensor_proc.stdin.flush()
        
        output = []
        while True:
            line = sensor_proc.stdout.readline()
            if not line:
                break
            output.append(line.strip())
            if "typical" in line:
                break

        print("Sensor Output:", output)
        attributes = parse_sensor_data(output)
        return attributes
    except Exception as e:
        print("Error reading sensor:", e)
        return None


# Stop 
def stop_sensor_process():
    global sensor_proc
    if sensor_proc:
        try:
            sensor_proc.stdin.write("exit\n")
            sensor_proc.stdin.flush()
            sensor_proc.wait(timeout=5)
        except Exception as e:
            print("Forțez închiderea procesului C:", e)
            sensor_proc.kill()
        sensor_proc = None


# handler pentru Ctrl+C
def handle_exit(signum, frame):
    print("\nÎnchidere cerută de utilizator (Ctrl+C)...")
    stop_sensor_process()
    if client:
        client.disconnect()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)

import select

def read_sensor(timeout=5):
    if sensor_proc is None:
        print("Sensor process not started")
        return None

    try:
        sensor_proc.stdin.write("read\n")
        sensor_proc.stdin.flush()

        output = []
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                print("Timeout waiting for sensor data")
                break
            rlist, _, _ = select.select([sensor_proc.stdout], [], [], 0.5)
            if rlist:
                line = sensor_proc.stdout.readline()
                if "typical" in line:
                    output.append(line.strip())
                    break
                output.append(line.strip())

        print("Sensor Output:", output)
        telemetry = parse_sensor_reading(output)
        return telemetry
    except Exception as e:
        print("Error reading sensor:", e)
        return None


def get_data():
    global sps_attributes
    
    cpu_usage = round(float(os.popen("grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }'").readline().replace('\n', '').replace(',', '.')), 2)
    ip_address = os.popen("hostname -I").readline().strip()
    ram_usage = float(os.popen("free -m | grep Mem | awk '{print ($3/$2) * 100}'").readline().strip())
    boot_time = os.popen('uptime -p').read().strip()
    avg_load = (cpu_usage + ram_usage) / 2

    attributes = {
        'ip_address': ip_address
    }
    
    if bool(sps_attributes):
        attributes.update(sps_attributes)
    
    telemetry = {
        'boot_time': boot_time,
        'avg_load': avg_load
    }
    
    sps_telemtry = {}
    if bool(sps_attributes):
        sps_telemtry = read_sensor() or {}
    
    telemetry.update(sps_telemtry)
    
    return attributes, telemetry

def sync_state(result, exception=None):
    global period
    if exception is not None:
        print("Exception:", exception)
    else:
        period = result.get('shared', {'blinkingPeriod': 1.0})['blinkingPeriod']

def main():
    global client
    client = TBDeviceMqttClient(THINGSBOARD_SERVER, username=ACCESS_TOKEN)
    client.connect()
    client.set_server_side_rpc_request_handler(rpc_callback)

    while not client.stopped:
        attributes, telemetry = get_data()
        client.send_attributes(attributes)
        client.send_telemetry(telemetry)
        time.sleep(15)

if __name__ == '__main__':
    if ACCESS_TOKEN != "TEST_TOKEN":
        main()
    else:
        print("Please change the ACCESS_TOKEN variable to match your device access token and run script again.")
