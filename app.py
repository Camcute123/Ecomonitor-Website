from flask import Flask, jsonify, render_template, request
import serial
import threading
import time

app = Flask(__name__)

latest_data = {
    "AQI": None,
    "temp": None,
    "RH": None,
    "TVOC": None,
    "CO2": None
}

ser = serial.Serial('/dev/cu.usbmodem1301', 9600, timeout=1)
time.sleep(2)
ser.reset_input_buffer()

serial_lock = threading.Lock()

@app.route("/buzzer", methods=["POST"])
def buzzer():
    command = request.json.get("command")
    print("Buzzer command:", command)

    with serial_lock:
        if command == "on":
            ser.write(b"BUZZER_ON\n")
        elif command == "off":
            ser.write(b"BUZZER_OFF\n")
        elif command == "auto":
            ser.write(b"BUZZER_AUTO\n")

    return jsonify({"status": "ok", "command": command})

def read_from_arduino():
    global latest_data

    while True:
        try:
            with serial_lock:
                line = ser.readline().decode(errors="ignore").strip()

            print("RAW:", repr(line))

            if not line:
                continue

            values = line.split(",")

            if len(values) == 5:
                latest_data["AQI"] = float(values[0])
                latest_data["temp"] = float(values[1])
                latest_data["RH"] = float(values[2])
                latest_data["TVOC"] = float(values[3])
                latest_data["CO2"] = float(values[4])
                print(latest_data)
            else:
                print("Skipped invalid line:", values)

        except Exception as e:
            print("Error:", e)

thread = threading.Thread(target=read_from_arduino)
thread.daemon = True
thread.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(latest_data)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5001)