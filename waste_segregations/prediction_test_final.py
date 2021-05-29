import os
import cv2
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image


def predict(img_path):
#     labels = {0: 'card_board', 1: 'cloth', 2: 'paper', 3: 'pen',4:'plastics'}
    target_names = ['card_board','cloth','paper','pen','plastics']
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
    
    if (predicted_class=="thermocol"):
        ser.write("l\r\n".encode('ascii'))
        
    if (predicted_class=="plastics"):
        ser.write("l\r\n".encode('ascii'))
        
    if (predicted_class=="cloth"):
        ser.write("r\r\n".encode('ascii'))
        
    if (predicted_class=="card_board"):
        ser.write("r\r\n".encode('ascii'))
#     return (str(predicted_class) + " \n Probability:" + str(pro))
# 
# 
import cv2

import serial

cap=cv2.VideoCapture(0)
# cap=cv2.VideoCapture('http://192.168.1.8:8080/video')

ser=serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=0.5)
while 1:
    ret,frame=cap.read()

    if ret:
        cv2.imshow("frame",frame)

        data=ser.readline()
 
        data1=data.decode('UTF-8')
        print(data1)

        if data1=='a':
            cv2.imwrite('test.jpg',frame)
            print(predict('test.jpg'))
            
        cv2.waitKey(10)

