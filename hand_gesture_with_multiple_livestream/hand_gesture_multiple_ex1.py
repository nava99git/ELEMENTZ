import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model, load_model
from keras.layers import Dense, MaxPool2D, Dropout, Flatten, Conv2D, GlobalAveragePooling2D, Activation
from keras.optimizers import Adam
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from random import choice, shuffle
from scipy import stats as st
from collections import deque
import imutils
import pandas as pd
import csv
from csv import writer
import winsound

#Import necessary libraries
from flask import Flask, render_template, Response
import cv2
#Initialize the Flask app
app = Flask(__name__)



frequency = 2500
duration = 1800
count = 0
count2 = 0

#os.remove("students.csv")
f = open("patient1.csv", "w")
f = open("patient2.csv", "w")
f.truncate()

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


# This list will be used to map probabilities to class names, Label names are in alphabetical order.
model= load_model("rps4.h5")
label_names = ['five', 'four','nothing', 'one','three','two','zero']

cap = cv2.VideoCapture(0)
vid3 = cv2.VideoCapture('http://192.168.1.5:8080/video')
box_size = 234
width = int(cap.get(3))

while True:

    ret, frame = cap.read()  # read the camera frame
    ret2, frame2 = vid3.read()
    if not (ret):
        break

    frame = cv2.flip(frame, 1)
    frame2 = cv2.flip(frame2, 1)

    cv2.rectangle(frame, (width - box_size, 0), (width, box_size), (0, 250, 150), 2)
    cv2.rectangle(frame2, (width - box_size, 0), (width, box_size), (0, 250, 150), 2)

    # cv2.namedWindow("Rock Paper Scissors", cv2.WINDOW_NORMAL)

    roi = frame[5: box_size - 5, width - box_size + 5: width - 5]
    roi_new = roi.copy()

    roi2 = frame2[5: box_size - 5, width - box_size + 5: width - 5]
    roi_new2 = roi2.copy()

    # Normalize the image like we did in the preprocessing step, also convert float64 array.
    roi = np.array([roi]).astype('float64') / 255.
    roi2 = np.array([roi2]).astype('float64') / 255.

    # roi_new = roi.copy()
    gray = cv2.cvtColor(roi_new, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)
    gray = imutils.resize(gray, width=300)

    gray2 = cv2.cvtColor(roi_new2, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.GaussianBlur(gray, (7, 7), 0)
    gray2 = imutils.resize(gray, width=300)

    roi_np = roi_new.copy()
    roi_nd = roi_new.copy()
    # roi_nn = roi_new.copy()

    roi_n2p = roi_new2.copy()
    roi_n2d = roi_new2.copy()
#########################################################################
    hsvim = cv2.cvtColor(roi_np, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 48, 80], dtype="uint8")
    upper = np.array([20, 255, 255], dtype="uint8")

    skinRegionHSV = cv2.inRange(hsvim, lower, upper)
    blurred = cv2.blur(skinRegionHSV, (2, 2))
    ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)
    # cv2.imshow("thresh", thresh)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours = max(contours, key=lambda x: cv2.contourArea(x))
    x = len(contours)
    # print(x)
##############################################################################
    hsvim2 = cv2.cvtColor(roi_n2p, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 48, 80], dtype="uint8")
    upper = np.array([20, 255, 255], dtype="uint8")

    skinRegionHSV = cv2.inRange(hsvim2, lower, upper)
    blurred = cv2.blur(skinRegionHSV, (2, 2))
    ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)
    # cv2.imshow("thresh", thresh)

    contours2, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours = max(contours, key=lambda x: cv2.contourArea(x))
    x2 = len(contours2)
    # print(x)
##############################################################################
    hsvim = cv2.cvtColor(roi_nd, cv2.COLOR_BGR2HSV)
    lower = np.array([101, 50, 38], dtype="uint8")
    upper = np.array([110, 255, 255], dtype="uint8")

    skinRegionHSV = cv2.inRange(hsvim, lower, upper)
    blurred = cv2.blur(skinRegionHSV, (2, 2))
    ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)
    # cv2.imshow("thresh", thresh)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours = max(contours, key=lambda x: cv2.contourArea(x))
    y = len(contours)
    # print(y)
#################################################################################
    hsvim2 = cv2.cvtColor(roi_n2d, cv2.COLOR_BGR2HSV)
    lower = np.array([101, 50, 38], dtype="uint8")
    upper = np.array([110, 255, 255], dtype="uint8")

    skinRegionHSV = cv2.inRange(hsvim2, lower, upper)
    blurred = cv2.blur(skinRegionHSV, (2, 2))
    ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)
    # cv2.imshow("thresh", thresh)

    contours2, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours = max(contours, key=lambda x: cv2.contourArea(x))
    y2 = len(contours)
    # print(y)
#################################################################################
    # Get model's prediction.
    pred = model.predict(roi)
    pred2 = model.predict(roi2)

    # Get the index of the target class.
    target_index = np.argmax(pred[0])
    target_index2 = np.argmax(pred2[0])
    # Get the probability of the target class
    prob = np.max(pred[0])
    prob2 = np.max(pred2[0])
    # Show results

    # cv2.putText(frame, "prediction: {} {:.2f}%".format(label_names[np.argmax(pred[0])], prob * 100),
    #           (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)

    p = label_names[np.argmax(pred[0])]
    p2 = label_names[np.argmax(pred2[0])]
    #print("p : ", p)
    #print("new p : ", p2)


    m = 0
    n = 0


    m2 = 0
    n2 = 0
###################################################################################################################
    if x > 10:
        print("patient-1")

        m = 1
        n = 0
        if p == 'zero':
            p = 'to go to toilet'
            cv2.putText(frame, "to go to toilet",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)

            print("to go to toilet")
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)


        elif p == 'one':
            p = 'patient calling nurse'
            print("patient calling nurse")
            cv2.putText(frame, "patient calling nurse",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        elif p == 'two':
            p = 'no commands'
            print("no commands")
            cv2.putText(frame, "no commands",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        elif p == 'three':
            p = 'to switch on fan'
            print("to switch on fan")
            cv2.putText(frame, "to switch on fan",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        elif p == 'four':
            p = 'to switch off fan'
            print("to switch off fan")
            cv2.putText(frame, "to switch off fan",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        elif p == 'five':
            p = 'for food from nurse'
            print("for food from nurse")
            cv2.putText(frame, "for food from nurse",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        else:
            p = 'nothing'
            # print("nothing")

    elif y > 20:
        print("doctor")
        m = 0
        n = 1
        if p == 'zero':
            p = 'for giving injection or medicines'
            cv2.putText(frame, "for giving injection or medicines",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("for giving injection or medicines")
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        elif p == 'one':
            p = 'doctor calling nurse'
            cv2.putText(frame, "doctor calling nurse",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("doctor calling nurse")
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)


        elif p == 'two':
            p = 'doctor calling nurse in emergency situation'
            cv2.putText(frame, "doctor calling nurse in emergency situation",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("doctor calling nurse in emergency situation")
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)


        elif p == 'three':
            p = 'to switch on fan'
            cv2.putText(frame, "to switch on fan",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("to switch on fan")
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        elif p == 'four':
            p = 'to switch off fan'
            cv2.putText(frame, "to switch off fan",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("to switch off fan")
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        elif p == 'five':
            p = 'to get medical report of the patient'
            cv2.putText(frame, "to get medical report of the patient",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("to get medical report of the patient")
            count = count + 1
            print("count : ", count)
            winsound.Beep(frequency, duration)
            row_contents = [count, m, n, p]
            append_list_as_row('patient1.csv', row_contents)

        else:
            p = 'nothing'
            # print("nothing")
###########################################################################################################################
    if x2 > 10:
        print("patient-2")

        m2 = 1
        n2 = 0
        if p2 == 'zero':
            p2 = 'to go to toilet'
            cv2.putText(frame2, "to go to toilet",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)

            print("to go to toilet")
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)


        elif p2 == 'one':
            p2 = 'patient calling nurse'
            print("patient calling nurse")
            cv2.putText(frame2, "patient calling nurse",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)

        elif p2 == 'two':
            p2 = 'no commands'
            print("no commands")
            cv2.putText(frame2, "no commands",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)

        elif p2 == 'three':
            p2 = 'to switch on fan'
            print("to switch on fan")
            cv2.putText(frame2, "to switch on fan",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)

        elif p2 == 'four':
            p2 = 'to switch off fan'
            print("to switch off fan")
            cv2.putText(frame2, "to switch off fan",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('spatient2.csv', row_contents)

        elif p2 == 'five':
            p2 = 'for food from nurse'
            print("for food from nurse")
            cv2.putText(frame2, "for food from nurse",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            count2 = count2 + 1
            print("count : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)

        else:
            p2 = 'nothing'
            # print("nothing")

    elif y2 > 20:
        print("doctor")
        m2 = 0
        n2 = 1

        if p2 == 'zero':
            p2 = 'for giving injection or medicines'
            cv2.putText(frame2, "for giving injection or medicines",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("for giving injection or medicines")
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)

        elif p2 == 'one':
            p2 = 'doctor calling nurse'
            cv2.putText(frame2, "doctor calling nurse",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("doctor calling nurse")
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)


        elif p2 == 'two':
            p2 = 'doctor calling nurse in emergency situation'
            cv2.putText(frame2, "doctor calling nurse in emergency situation",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("doctor calling nurse in emergency situation")
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)


        elif p2 == 'three':
            p2 = 'to switch on fan'
            cv2.putText(frame2, "to switch on fan",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("to switch on fan")
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)

        elif p2 == 'four':
            p2 = 'to switch off fan'
            cv2.putText(frame2, "to switch off fan",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("to switch off fan")
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)

        elif p2 == 'five':
            p2 = 'to get medical report of the patient'
            cv2.putText(frame2, "to get medical report of the patient",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (0, 0, 255), 2, cv2.LINE_AA)
            time.sleep(1)
            print("to get medical report of the patient")
            count2 = count2 + 1
            print("count2 : ", count2)
            winsound.Beep(frequency, duration)
            row_contents = [count2, m2, n2, p2]
            append_list_as_row('patient2.csv', row_contents)

        else:
            p2 = 'nothing'
            # print("nothing")
##########################################################################################################################
    # else:
    # print("none")

    cv2.imshow("Status From Patient-1 Room ", frame)
    cv2.imshow("Status From Patient-2 Room ", frame2)

    k = cv2.waitKey(1)
    if k == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()




