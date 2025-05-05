import os
import logging
import cv2
import time
import board
import adafruit_vl53l4cd
import RPi.GPIO as GPIO

from flask import Flask, render_template, Response
from picamera2 import Picamera2
from libcamera import controls
from waitress import serve

led_b = 11
led_g = 9
led_r = 10
out1 = 14
out2 = 15
power = 17
# dtoverlay=gpio-shutdown,gpio_pin=17,active_low=1,gpio_pull=up,debounce=1000


i2c = board.I2C()  # uses board.SCL and board.SDA
vl53 = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,template_folder="tpl")

# Initialize Picamera2 instance
camera = None
camera_initialized = False
# Still snapshot profile
c_still = None
c_still_size = (4608, 2592)
# Preview stream
c_preview = None
c_preview_size = (1536, 864)

# read proximity sensor
measure_distance = True

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_color = (128,128, 255)  # White color
thickness = 2

ERRORS = None
ERRORC = None

# Route for displaying the main page
@app.route('/')
def index():
    return render_template('index.html',errors=ERRORS,errorc=ERRORC)

# Route for health state
@app.route('/health')
def state():
    if ERRORC or ERRORS:
        return {
            "health": "ERROR", "error_cam": ERRORC, "error_range": ERRORS
        }

    else:
        return {
            "health": "OK"
        }

# Route for poweroff
@app.route('/poweroff')
def poweroff():
    GPIO.output(power, GPIO.LOW)
    return {
        "DONE": "OK"
    }


# Route for manipulating GPIO
@app.route('/output/<string:name>/<int:state>')
def output(name,state):
    if state != 1:
       state = 0
    match name:
        case 'out1':
            GPIO.output(out1, GPIO.HIGH if state ==1 else GPIO.LOW )
        case 'out2':
            GPIO.output(out2, GPIO.HIGH if state ==1 else GPIO.LOW )
        case _:
            return { "error": "invalid IO"}
    
    logger.info("OUTPUT {}:{}".format(name,state))
    return { "pin": name, "state": state }

# Route for serving still image
@app.route('/distance')
def distance():
    d = get_distance()
    logger.info("Distance {} cm".format(d))
    return {
        "distance_cm": d,
    }

# Route for serving still image
@app.route('/capture.jpg')
def still():
    logger.info("Snapshot requested.")
    return Response(make_snapshot(),mimetype='image/jpeg')


# Route for serving the video stream
@app.route('/video_feed')
def video_feed():
    logger.info("Video feed requested.")
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


#reas distance from sensor
def get_distance():
    if vl53:
        vl53.clear_interrupt()
        return vl53.distance
    else:
        return -1

# Generate video frames for streaming
def generate_frames():
    global camera, measure_distance
    try:
        camera.start()
        while True:
            # Capture a frame
            frame = camera.capture_array()
            position = (frame.shape[1] - 300, frame.shape[0] - 20)  # Bottom-right corner
            if measure_distance:
                distance = "Distance: {} cm".format(get_distance())
                cv2.putText(frame, distance, position, font, font_scale, font_color, thickness)

            # Convert the frame to JPEG
            success, jpeg = cv2.imencode('.jpg', frame)
            if not success:
                logger.error("Failed to encode frame.")
                continue

            # Yield the JPEG image as part of the multipart response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

            # Limit frame rate
            time.sleep(0.2)

    except Exception as e:
        logger.error(f"Error during frame generation: {e}")

# Generate video frames for streaming
def make_snapshot():
    global camera,c_still
    try:
        camera.start()
        # Capture a frame
        frame = camera.switch_mode_and_capture_array(c_still,"main")
        camera.stop_recording()
        # Convert the frame to JPEG
        success, jpeg = cv2.imencode('.jpg', frame)
        if not success:
            logger.error("Failed to encode frame.")
        else:    
            return (jpeg.tobytes() + b'\r\n\r\n')

    except Exception as e:
        logger.error(f"Error during snaphot: {e}")

# Initialize camera
def initialize_camera():
    global camera, camera_initialized, c_still, c_preview
    if not camera_initialized:
        try:
            camera = Picamera2()
            sensor_modes = camera.sensor_modes
            logger.info(f"Sensor modes {sensor_modes}")

            c_still = camera.create_still_configuration(
                main={"size": c_still_size , "format": "RGB888" }  # Set desired resolution 
            )

            c_preview = camera.create_preview_configuration(
                main={"size": c_preview_size, "format": "RGB888" }  
            )
            # Set manual exposure time and disable auto exposure
            camera.set_controls({
                "ExposureTime": 10000,  #  exposure
#                "AeEnable": True,      # Disable auto exposure
#                "AfMode": controls.AfModeEnum.Continuous
            })
            camera.configure("preview")
            camera.configure(c_preview)
            camera_initialized = True
            logger.info("Camera initialized successfully with custom settings.")
            camera.start()

        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            camera_initialized = False


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(power, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(out1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(out2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(led_r, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(led_g, GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(led_g, GPIO.LOW)
    GPIO.output(led_r, GPIO.HIGH)
    host = os.environ.get('HOST', '0.0.0.0')
    port = os.environ.get('PORT', '8082')

    GPIO.output(led_r, GPIO.LOW)

    try:
        logger.info("Initializing Distance sensor.")
        vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)

        # OPTIONAL: can set non-default values
        vl53.inter_measurement = 0
        vl53.timing_budget = 200
    
        model_id, module_type = vl53.model_info
        logger.info("Sensor model ID: 0x{:0X}".format(model_id))
        logger.info("Sensor moudle Type: 0x{:0X}".format(module_type))
        vl53.start_ranging()
        
    except:
        ERRORS = "Range Sensor not found"
        logger.error("Range sensor not found")
        

    logger.info("Initializing Camera.")
    initialize_camera()  # Ensure camera is initialized

    if not camera_initialized:
        ERRORC = "Camera not initialized properly."
        logger.error("Camera not initialized properly")

    logger.info(f"Starting server at {host}:{port}")

    if ERRORS or ERRORC:
        GPIO.output(led_r, GPIO.HIGH)
    else:
        GPIO.output(led_g, GPIO.HIGH)

    serve(app, host=host, port=int(port))
    GPIO.output(led_r, GPIO.LOW)
    GPIO.output(led_g, GPIO.LOW)

