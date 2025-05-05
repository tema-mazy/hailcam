import os
import logging
import time
import random

from flask import Flask, render_template, Response, send_from_directory
from waitress import serve
from io import BytesIO
from mmap import ACCESS_READ, mmap

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,template_folder="tpl")

# Route for displaying the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for health state
@app.route('/health')
def state():
    return {
        "health": "OK"
    }



# Route for poweroff
@app.route('/poweroff')
def poweroff():
    exit


# Route for manipulating GPIO
@app.route('/output/<string:name>/<int:state>')
def output(name,state):
    if state != 1:
       state = 0
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
    return send_from_directory('mock','img_full.jpg',mimetype='image/jpeg',)


# Route for serving the video stream
@app.route('/video_feed')
def video_feed():
    logger.info("Video feed requested.")
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


#reas distance from sensor
def get_distance():
    return random.randint(10, 2000)/10;

# Generate video frames for streaming
def generate_frames():
    global camera, measure_distance
    try:
        with open("mock/img_crop.jpg", 'rb', 0) as f, mmap(f.fileno(), 0, access=ACCESS_READ) as s:
            while True:
                # Yield the JPEG image as part of the multipart response
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + s + b'\r\n\r\n')

            # Limit frame rate
            time.sleep(0.2)

    except Exception as e:
        logger.error(f"Error during frame generation: {e}")



if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = os.environ.get('PORT', '8082')
    logger.info(f"Starting server at {host}:{port}")
    serve(app, host=host, port=int(port))


