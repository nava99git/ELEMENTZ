from flask import Flask, flash, render_template, request, redirect, url_for
import sqlite3
import os
import cv2
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
# import serial

# ser=serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=0.5)

app = Flask(__name__)
app.secret_key = 'thisissecretkey'

types = {'Thermocol' : 'Non-biodegradable', 
		 'Plastic' : 'Non-biodegradable',
		 'Cloth' : 'Biodegradable',
		 'Cardboard' : 'Biodegradable'}

class row(object):
    def __init__(self, Type, Degradability, Count):
        self.Type = Type
        self.Degradability = Degradability
        self.Count = Count

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
	text = request.args.get('jsdata')
	print(text)
	# if cv2.VideoCapture(0).isOpened():
	# cv2.VideoCapture().release()
	

	while 1:
	    # ret,frame=cap.read()

	    # if ret:

	        # data=ser.readline()
	 
	        # data1=data.decode('UTF-8')
	        # print(data1)
		if input('Enter Something!'):
			cap=cv2.VideoCapture(0)
			ret,frame=cap.read()

			if ret:
				cv2.imwrite('test.jpg',frame)
				predictType = predict('test.jpg')
				print(predictType)

				if predictType in types.keys():
					conn = sqlite3.connect('wsDB.db')
					cur = conn.cursor()
					cur.execute("SELECT count(*) FROM DetectedItems")
					itemno = int(cur.fetchone()[0])+1
					message = 'itemno: %d Type : %s Degradability : %s' %(itemno, predictType, types[predictType] )
					cur.execute("INSERT INTO DetectedItems VALUES ('%s', '%s')" %(predictType, types[predictType]))
					conn.commit()
					conn.close()
					cap.release()
					return render_template('run.html')  
				else:
					print("Unable to predict")
					cap.release()
				cv2.waitKey(10)
			else:
				print("Unable to read from camera")
				cap.release()

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
   app.run(host='192.168.43.86', port=8080, debug=True,threaded=True)