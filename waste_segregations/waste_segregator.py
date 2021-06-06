from flask import Flask, flash, render_template, request, redirect, url_for, Response
import sqlite3
import os
import cv2, queue, threading
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import time

# import serial
# ser=serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=0.5)

app = Flask(__name__)
app.secret_key = 'thisissecretkey'

types = {'Thermocol': 'Non-biodegradable',
		 'Plastic': 'Non-biodegradable',
		 'Cloth': 'Biodegradable',
		 'Cardboard': 'Biodegradable'}

# font
font = cv2.FONT_HERSHEY_SIMPLEX
# org
org = (50, 50)
# fontScale
fontScale = 0.8
# Blue color in BGR
color = (255, 0, 0)
# Line thickness of 2 px
thickness = 2


class VideoCapture:

  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    return self.q.get()

class row(object):
    def __init__(self, Type, Degradability, Count):
        self.Type = Type
        self.Degradability = Degradability
        self.Count = Count

cap = VideoCapture(0)

def predict(img_path):
#     labels = {0: 'card_board', 1: 'cloth', 2: 'paper', 3: 'pen',4:'plastics'}
    target_names = ['Cardboard','Cloth','paper','pen','Plastic']
    # img_path = 'C:\\Users\\--\\Downloads\\dataset-original\\dataset-original\\metal\\'

    img = image.load_img(img_path, target_size=(150, 150))
    img = image.img_to_array(img, dtype=np.uint8)
    img = np.array(img) / 255.0


    model = tf.keras.models.load_model("train_modelnew.h5")
    p = model.predict(img[np.newaxis, ...])
    pro = np.max(p[0], axis=-1)
    print("p.shape:", p.shape)
    print("prob", pro)
    predicted_class = target_names [np.argmax(p[0], axis=-1)]
    os.remove(img_path)
    print("classified label:", predicted_class)

    # if (predicted_class=="Thermocol"):
        # ser.write("l\r\n".encode('ascii'))

    # if (predicted_class=="Plastic"):
        # ser.write("l\r\n".encode('ascii'))

    # if (predicted_class=="Cloth"):
        # ser.write("r\r\n".encode('ascii'))

    # if (predicted_class=="Cardboard"):
        # ser.write("r\r\n".encode('ascii'))

    return predicted_class

def getprediction(start):
	print('getprediction called')
	i = 0
	# detect = False

	while True:
		print('reading new frame')
		frame=cap.read()
		# if ret:
		# data=ser.readline()

	        # data1=data.decode('UTF-8')
	        # print(data1)
		i = i+1
		if i == 30:
		# if input('Enter Something') == 'a':
			print('trigger')
			i = 0
			cv2.imwrite('test.jpg',frame)
			predictType = predict('test.jpg')
			print(predictType)

			if predictType in types.keys():
				conn = sqlite3.connect('wsDB.db')
				cur = conn.cursor()
				cur.execute("SELECT count(*) FROM DetectedItems")
				itemno = int(cur.fetchone()[0])+1
				# message = 'itemno: %d Type : %s Degradability : %s' %(itemno, predictType, types[predictType] )
				cur.execute("INSERT INTO DetectedItems VALUES ('%s', '%s')" %(predictType, types[predictType]))
				conn.commit()
				conn.close()
				text = "Type : '%s' Degradability : %s'" % (predictType, types[predictType])
				frame = cv2.putText(frame, text, org, font, fontScale, color, thickness, cv2.LINE_AA)
				# detect = True
			else:
				print("Unable to predict")

		# if detect:
		# 	print('sleeping')
		# 	time.sleep(5)
		# 	detect = False
		print('showing new frame')
		ret, jpeg = cv2.imencode('.jpg', frame)
		frame = jpeg.tobytes()

		yield (b'--frame\r\n'
			b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route("/")
def index():
   return render_template('start.html')

@app.route('/start', methods=['POST'])
def start():
	conn = sqlite3.connect('wsDB.db')
	cur = conn.cursor()
	cur.execute("DELETE FROM DetectedItems")
	conn.commit()
	conn.close()

	return render_template('run.html')

@app.route('/run', methods=['POST', 'GET'])
def run():
	print('Running...')

	return Response(getprediction(True), mimetype = 'multipart/x-mixed-replace; boundary=frame')

@app.route('/result', methods=['POST'])
def result():
	conn = sqlite3.connect('wsDB.db')
	cur = conn.cursor()
	rows = []

	for Type in types.keys():
		cur.execute("SELECT count(*) FROM DetectedItems WHERE Type = '%s'" % (Type))
		rows.append(row('%s' %(Type), '%s' %(types[Type]), cur.fetchone()[0]))

	conn.close()
	return render_template('result.html', rows = rows)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080, debug=False)
