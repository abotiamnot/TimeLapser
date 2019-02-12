import io
import time
import picamera
from base_camera import BaseCamera


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera(framerate=30) as camera:
            time.sleep(2)
            stream = io.BytesIO()
            camera.resolution = (1280,720)
            # camera.resolution = (640,480)
            for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                stream.seek(0)
                yield stream.read()
                stream.seek(0)
                stream.truncate()
            # while True:
            #     # time.sleep(0.05)
            #     camera.capture(stream, 'jpeg')
            #     stream.seek(0)
            #     yield stream.read()
            #     stream.seek(0)
            #     stream.truncate()

