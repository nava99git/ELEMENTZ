import cv2
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

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
i = 0
while(True):
    for j in range(3):
        _, frame = cap.read()
    frame = cv2.putText(frame, str(i), org, font, fontScale, color, thickness, cv2.LINE_AA)
    cv2.imshow('frame', frame)
    input('Enter Something')
    i = i+1
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
