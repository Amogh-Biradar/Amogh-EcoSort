from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from prediction import predict
import pandas as pd
import RPi.GPIO as GPIO
import time
import threading
import cv2
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ecosort'


# routes


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["password"]
        r1 = pd.read_excel('user.xlsx')
        for index, row in r1.iterrows():
            if row["email"] == str(email) and row["password"] == str(pwd):
                return redirect(url_for('home'))
        else:
            mesg = 'Invalid Login Try Again'
            return render_template('login.html', msg=mesg)
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['Email']
        password = request.form['Password']
        col_list = ["name", "email", "password"]
        r1 = pd.read_excel('user.xlsx', usecols=col_list)
        new_row = {'name': name, 'email': email, 'password': password}
        r1 = r1.append(new_row, ignore_index=True)
        r1.to_excel('user.xlsx', index=False)
        print("Records created successfully")
        # msg = 'Entered Mail ID Already Existed'
        msg = 'Registration Successful ! U Can login Here !'
        return render_template('login.html', msg=msg)
    return render_template('register.html')


@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template("home.html")


GPIO.setmode(GPIO.BCM)
input_pin = 17  # Replace with your GPIO pin number
GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup LED pins
red_pin = 16
yellow_pin = 18
green_pin = 17
GPIO.setup(red_pin, GPIO.OUT)
GPIO.setup(yellow_pin, GPIO.OUT)
GPIO.setup(green_pin, GPIO.OUT)


def control_leds(input_data):
    with open("static/input/input.txt", "r") as file:
        input_data = file.read().strip()

    if input_data == '1':
        GPIO.output(red_pin, GPIO.HIGH)
        print("Red LED On")
        time.sleep(5)  # Keep LED on for 3 seconds
        GPIO.output(red_pin, GPIO.LOW)
        print("Red LED Off")
    elif input_data == '2':
        GPIO.output(yellow_pin, GPIO.HIGH)
        print("Yellow LED On")
        time.sleep(5)  # Keep LED on for 3 seconds
        GPIO.output(yellow_pin, GPIO.LOW)
        print("Yellow LED Off")
    elif input_data == '3':
        GPIO.output(green_pin, GPIO.HIGH)
        print("Green LED On")
        time.sleep(5)  # Keep LED on for 3 seconds
        GPIO.output(green_pin, GPIO.LOW)
        print("Green LED Off")

    with open("static/input/input.txt", "w") as file:
        file.write("0\n")





@app.route("/submit", methods=['GET', 'POST'])
def get_hours():
    if request.method == 'POST':
        
        external_camera_index = 0

        cap = cv2.VideoCapture(external_camera_index)

        if not cap.isOpened():
            return jsonify({'error': 'Unable to access the external camera'})

        ret, frame = cap.read()

        if not ret:
            return jsonify({'error': 'Unable to capture an image'})

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        img_path = f'static/upload/captured_image_{timestamp}.jpg'

        cv2.imwrite(img_path, frame)

        # img = request.files['my_image']
        # # print('img : ', img)
        # img_path = "static/upload/" + img.filename
        # # print('img_path : ', img_path)
        # img.save(img_path)
        prediction = predict(img_path)

        # led_simulator.simulate_led_control()

        file_path = 'static/input/input.txt'
        if prediction[0] == "E-waste":
            with open(file_path, 'w') as file:
                file.write("1")
        elif prediction[0] == "Recycle":
            with open(file_path, 'w') as file:
                file.write("2")
        else:
            with open(file_path, 'w') as file:
                file.write("3")

        # Control LEDs based on the input (simulated with print)
        # control_leds(file_path)

        led_thread = threading.Thread(target=control_leds, args=(file_path,))
        led_thread.start()

        return render_template("home.html", prediction=prediction[0], acc=prediction[1], img_path=img_path)
    else:
        # Handle GET requests here, if needed
        return render_template("home.html")


@app.route('/password', methods=['POST', 'GET'])
def password():
    if request.method == 'POST':
        current_pass = request.form['current']
        new_pass = request.form['new']
        verify_pass = request.form['verify']
        r1 = pd.read_excel('user.xlsx')
        for index, row in r1.iterrows():
            if row["password"] == str(current_pass):
                if new_pass == verify_pass:
                    r1.replace(to_replace=current_pass,
                               value=verify_pass, inplace=True)
                    r1.to_excel("user.xlsx", index=False)
                    msg1 = 'Password changed successfully'
                    return render_template('password_change.html', msg1=msg1)
                else:
                    msg2 = 'Re-entered password is not matched'
                    return render_template('password_change.html', msg2=msg2)
        else:
            msg3 = 'Incorrect password'
            return render_template('password_change.html', msg3=msg3)
    return render_template('password_change.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    session.clear()
    msg = 'You are now logged out', 'success'
    return redirect(url_for('login', msg=msg))


if __name__ == '__main__':
    app.run(port=5055, debug=True, host='0.0.0.0')
