from tkinter import *
from tkinter.filedialog import asksaveasfile
import cv2
root = Tk()


cap=cv2.VideoCapture(0)






while True:
    ret,frame=cap.read()
    cv2.imshow("frame",frame)
    k=cv2.waitKey(10)
    if k & 0xff == ord('c'):





            name = asksaveasfile(initialdir="/mnt/C000FEAA00FEA696/ELEMENTZ/GUI Tkinter", title="Select file", filetypes=(
                ('JPEG', ('*.jpg', '*.jpeg', '*.jpe')), ('PNG', '*.png'), ('BMP', ('*.bmp', '*.jdib')),
                ('GIF', '*.gif')))

            print (name.name)
            cv2.imwrite(name.name,frame)


