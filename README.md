# hailcam
Paspberry PI Camera + Adafruit vl53l4cd proximity sensor


## scripts
init.sh - init virtualenv on raspi

init-m.sh - init virtualenv for mock service

run-mock.sh - run mock service

## URLS
**http://127.0.0.1:8082/** - general page with stream and capture button

response - html page

**http://127.0.0.1:8082/get_distance** -  range from proximity sensor ( in cm )

response: JSON '{ "distance_cm": dd.d }'

**http://127.0.0.1:8082/capture.jpg** - capture image in max res (4608 * 2592)

response - jpeg

**http://127.0.0.1:8082/video_feed** - mjpeg video stream low res (1280 * 1024 )

response - mjpeg stream
