from flask import Flask, render_template, Response
import cv2
import hand_gesture_recognition as hgr
#Initialize the Flask app
app = Flask(__name__)


#capture the webcam
vid1 = cv2.VideoCapture(0)
#vid2 = cv2.VideoCapture(1)
vid3 = cv2.VideoCapture('http://192.168.1.6:8080/video')
                                          #ipwebcam address

def getcam(id):
    while True:
        if id == 1:
            ret,frame = vid1.read()
            # cv2.imshow('cam', frame1)
        elif id == 2:
            ret,frame = vid3.read()
            # cv2.imshow('cam', frame3)


        if ret:
            getGesture(frame)
            ret, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            break

@app.route("/")
def index():
   return render_template('cam.html')

@app.route('/cam/<int:id>', methods=['POST', 'GET'])
def cam(id):
	print('Running...')

	return Response(getcam(id), mimetype = 'multipart/x-mixed-replace; boundary=frame')

app.run('0.0.0.0', port = 8000)

vid1.release()
#vid2.release()
vid3.release()
