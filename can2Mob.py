import struct
import random
from flask import Flask, jsonify
import threading
import cantools
import time

db = cantools.database.load_file('demo2.dbc')

def decode_can_data(can_id, raw_data):
    can_id_int = int(can_id, 16)
    message = db.get_message_by_frame_id(can_id_int)

    raw_data_bytes = bytes.fromhex(raw_data.replace(' ', ''))
    print(f"Decoding CAN ID: {can_id} (int: {can_id_int})")
    print(f"Raw data bytes: {raw_data_bytes.hex().upper()}")

    try:
        decoded_data = message.decode(raw_data_bytes)
        print(f"Decoded data: {decoded_data}")
        return decoded_data
    except Exception as e:
        print(f"Decoding error: {e}")
        return None

def generate_raw_can_data():
    # MotorSpeed: 0|16@1+ (0.1,0) [0|10000] "rpm"
    motor_speed = int(random.uniform(0, 10000) / 0.1)
    motor_speed = max(0, min(motor_speed, 65535))
     # MotorTemperature: 16|16@1+ (1,0) [-40|210] "°C"
    motor_temperature = int(random.uniform(-40, 210))
    motor_temperature = max(0, min(motor_temperature, 255))
    motor_data = struct.pack('<HHxxxx', motor_speed, motor_temperature) #'Not working : HxxxxBxx', Partial working :'<3xH3xB'


    # BatteryVoltage: 0|16@1+ (0.1,0) [0|6553.5] "V"
    battery_voltage = int(random.uniform(0, 6553.5) / 0.1)
    battery_voltage = max(0, min(battery_voltage, 65535))

    # BatteryCurrent: 16|16@1+ (0.1,0) [-3276.8|3276.7] "A"
    battery_current = int(random.uniform(-3276.8, 3276.7) / 0.1)
    battery_current = max(-32768, min(battery_current, 32767))

    # StateOfCharge: 32|8@1+ (0.4,0) [0|100] "%"
    state_of_charge = int(random.uniform(0, 100) / 0.4)
    state_of_charge = max(0, min(state_of_charge, 255))
    battery_data = struct.pack('<HhBxxxx', battery_voltage, battery_current, state_of_charge)

    # VehicleSpeed: 0|16@1+ (0.00390625,0) [0|250.996] "km/h"
    vehicle_speed = int(random.uniform(0, 250.996) / 0.00390625)
    vehicle_speed = max(0, min(vehicle_speed, 65535))
    vehicle_data = struct.pack('<Hxxxxxx', vehicle_speed)

    can_data = {
        '0x100': ' '.join(['{:02X}'.format(b) for b in motor_data]),
        '0x200': ' '.join(['{:02X}'.format(b) for b in battery_data]),
        '0x300': ' '.join(['{:02X}'.format(b) for b in vehicle_data]),
    }
     # Print raw CAN data for debugging
    print("Generated CAN data:")
    for can_id, data in can_data.items():
        print(f"{can_id}: {data}")
        
    return can_data

app = Flask(__name__)
can_data = {}

@app.route('/can_data', methods=['GET'])
def get_can_data():
    global can_data
    return jsonify(can_data)

def generate_and_host_can_data():
    global can_data
    while True:
        can_data = generate_raw_can_data()
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=generate_and_host_can_data, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
