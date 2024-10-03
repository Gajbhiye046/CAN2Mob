import cantools
import random
import struct
import matplotlib.pyplot as plt
import seaborn as sns
#from IPython.display import display, clear_output
import time
import binascii
from flask import Flask, jsonify
from flask_socketio import SocketIO
import threading

# Load the DBC file
dbc_file = 'demo3.dbc'
db = cantools.database.load_file(dbc_file)

def decode_can_data(can_id, raw_data, db):
    """
    Decodes the CAN message using the DBC file based on CAN ID and raw hex data.
    
    Args:
        can_id (str): CAN message identifier (CAN ID) in hex format (e.g. '1810A7F3').
        raw_data (str): Raw CAN data in hex string format (e.g. 'B50C6310B8000000').
        db (cantools.database.Database): Loaded DBC database.

    Returns:
        dict: A dictionary with signal names and their decoded values, or an error message if decoding fails.
    """
    try:
        # Convert the CAN ID from hex string to an integer
        can_id_int = int(can_id, 16)
        #print('can id: ',can_id_int)
        # Convert raw hex string data into bytes
        data_bytes = binascii.unhexlify(raw_data)
        
        # Look for the message by CAN ID in the DBC file
        dbc_message = None
        for message in db.messages:
            # Get the 29-bit frame ID
            #print("message_id(32 Bit) :", message)
            message_29bit_id = message.frame_id & 0x1FFFFFFF
            #print('message id(29 bit) : ',message_29bit_id)
            if message_29bit_id == can_id_int:
                dbc_message = message
                break
        
        if dbc_message:
            # Decode the CAN data using the DBC message definition
            decoded_signals = dbc_message.decode(data_bytes)
            
            # Return the decoded signal values as a dictionary
            return decoded_signals
        else:
            print(f"Message for CAN ID {can_id} not found in DBC.")
            return None
    except Exception as e:
        print(f"Error decoding CAN data: {e}")
        return None

def generate_raw_can_data():
    # Generate raw data for MotorController1 (ID: 0x1810A7F3)
    motor_speed = int(random.uniform(0, 10000) / 0.1)  # MotorSpeed: 0|16@1+ (0.1,0)
    motor_speed = max(0, min(motor_speed, 65535))
    
    motor_torque = int(random.uniform(0, 500) / 0.1)  # MotorTorque: 16|16@1+ (0.1,0)
    motor_torque = max(0, min(motor_torque, 65535))
    
    motor_temperature = int(random.uniform(-40, 210))  # MotorTemperature: 32|16@1+ (1,0)
    motor_temperature = max(0, min(motor_temperature, 65535))
    
    motor_controller1_data = struct.pack('<HHHxx', motor_speed, motor_torque, motor_temperature)

    # Generate raw data for MotorController2 (ID: 0x1818A7F3)
    motor_speed2 = int(random.uniform(0, 10000) / 0.1)  # MotorSpeed2: 0|16@1+ (0.1,0)
    motor_speed2 = max(0, min(motor_speed2, 65535))
    
    motor_torque2 = int(random.uniform(0, 500) / 0.1)  # MotorTorque2: 16|16@1+ (0.1,0)
    motor_torque2 = max(0, min(motor_torque2, 65535))
    
    inverter_temperature = int(random.uniform(-40, 210))  # InverterTemperature: 32|16@1+ (1,0)
    inverter_temperature = max(0, min(inverter_temperature, 65535))
    
    motor_controller2_data = struct.pack('<HHHxx', motor_speed2, motor_torque2, inverter_temperature)

    # Generate raw data for BatteryManagement1 (ID: 0x1801F3A7)
    battery_voltage = int(random.uniform(0, 6553.5) / 0.1)  # BatteryVoltage: 0|16@1+ (0.1,0)
    battery_voltage = max(0, min(battery_voltage, 65535))
    
    battery_current = int(random.uniform(-3276.8, 3276.7) / 0.1)  # BatteryCurrent: 16|16@1+ (0.1,0)
    battery_current = max(-32768, min(battery_current, 32767))
    
    state_of_charge = int(random.uniform(0, 100) / 0.4)  # StateOfCharge: 32|8@1+ (0.4,0)
    state_of_charge = max(0, min(state_of_charge, 255))
    
    battery_temperature = int(random.uniform(-40, 100))  # BatteryTemperature: 40|16@1+ (1,0)
    battery_temperature = max(0, min(battery_temperature, 65535))
    
    battery_management1_data = struct.pack('<HhBHxx', battery_voltage, battery_current, state_of_charge, battery_temperature)

    # Generate raw data for VehicleStatus1 (ID: 0x18500627)
    vehicle_speed = int(random.uniform(0, 250.996) / 0.00390625)  # VehicleSpeed: 8|16@1+ (0.00390625,0)
    vehicle_speed = max(0, min(vehicle_speed, 65535))
    
    odometer = int(random.uniform(0, 4294967295))  # Odometer: 24|32@1+ (1,0)
    tire_pressure_fl = int(random.uniform(0, 100) / 0.1)  # TirePressureFL: 0|8@1+ (0.1,0)
    tire_pressure_fl = max(0, min(tire_pressure_fl, 255))  # Ensure the value is between 0 and 255
    
    tire_pressure_fr = int(random.uniform(0, 100) / 0.1)  # TirePressureFR: 8|8@1+ (0.1,0)
    tire_pressure_fr = max(0, min(tire_pressure_fr, 255))  # Ensure the value is between 0 and 255
    
    vehicle_status1_data = struct.pack('<BHHIB', tire_pressure_fl, tire_pressure_fr, vehicle_speed, odometer, 0x00)

    # Generate raw data for BatteryManagement2 (ID: 0x18FF0527)
    battery_voltage2 = int(random.uniform(0, 6553.5) / 0.1)  # BatteryVoltage2: 0|16@1+ (0.1,0)
    battery_voltage2 = max(0, min(battery_voltage2, 65535))
    
    battery_current2 = int(random.uniform(-3276.8, 3276.7) / 0.1)  # BatteryCurrent2: 16|16@1+ (0.1,0)
    battery_current2 = max(-32768, min(battery_current2, 32767))
    
    battery_management2_data = struct.pack('<Hhxxxx', battery_voltage2, battery_current2)

    # Generate raw data for BatteryManagement3 (ID: 0x18FF0927)
    state_of_charge2 = int(random.uniform(0, 100) / 0.4)  # StateOfCharge2: 32|8@1+ (0.4,0)
    state_of_charge2 = max(0, min(state_of_charge2, 255))
    
    battery_temperature2 = int(random.uniform(-40, 100))  # BatteryTemperature2: 40|16@1+ (1,0)
    battery_temperature2 = max(0, min(battery_temperature2, 65535))
    
    battery_management3_data = struct.pack('<BHHxxx', state_of_charge2, battery_temperature2, 0x00)

    # Prepare CAN data dictionary
    can_data = {
        '1810A7F3': motor_controller1_data,
        '1818A7F3': motor_controller2_data,
        '1801F3A7': battery_management1_data,
        '18500627': vehicle_status1_data,
        '18FF0527': battery_management2_data,
        '18FF0927': battery_management3_data,
    }

    # Format the output as messageID#message
    formatted_can_data = {}
    for can_id, data in can_data.items():
        # Convert byte data to hex string and format as 'messageID#message'
        formatted_message = ''.join(['{:02X}'.format(b) for b in data])
        formatted_can_data[can_id] = f'{can_id}#{formatted_message}'
        

    #Print the formatted CAN data
    print("Generated CAN data (messageID#message):")
    for can_id, message in formatted_can_data.items():
       print(message)

    return formatted_can_data
    
    
app = Flask(__name__)
socketio = SocketIO(app)
can_data = {}

@app.route('/can_data', methods=['GET'])
def get_can_data():
    global can_data
    return jsonify(can_data)

def generate_and_host_can_data():
    global can_data
    while True:
        can_data = generate_raw_can_data()
        socketio.emit('can_data_update', can_data)
        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=generate_and_host_can_data, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
