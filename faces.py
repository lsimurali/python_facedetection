import numpy as np
import cv2
import pickle
import mysql.connector
import datetime

now = datetime.datetime.now()



mrng_frm=now.strftime("%Y-%m-%d 10:00")
mrng_to=now.strftime("%Y-%m-%d 11:00")


evn_frm=now.strftime("%Y-%m-%d 17:00")
evn_to=now.strftime("%Y-%m-%d 18:00")

if now.hour >11:
	frm=evn_frm
	to =evn_to
else:
	frm = mrng_frm
	to =mrng_to





mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="gatik@123",
  database="mydb"
)

mycursor = mydb.cursor()


def markattendance(username,frm,to):
	# print(now.hour)
	if  now.hour in range(10,11) or now.hour in range(17,18):

		#sql = "SELECT * FROM attendance where  username=%s and date =%s "
		sql = "SELECT * FROM `attendance` WHERE `username`=%s and `date`=%s AND `forenoon_time` BETWEEN '10:00' AND '11:00' "
		date = now.strftime("%Y-%m-%d")
		values = (username,date,)

		mycursor.execute(sql, values)

		myresult = mycursor.fetchall()

		if len(myresult) == 0:

			if now.hour in range(10,11):

				#print("it's working ")
				sql = "INSERT INTO `attendance`(`username`, `forenoon`,`forenoon_time`,`date`) VALUES (%s, %s,%s,%s)"
				val = (username,"P",now.strftime("%H:%M"),now.strftime("%Y-%m-%d"))
				mycursor.execute(sql, val)
				mydb.commit()

		if now.hour in range(17, 18):
			sql = "SELECT * FROM attendance where  username=%s and `date`=%s AND `forenoon_time` BETWEEN '10:00' AND '11:00'"
			date = now.strftime("%Y-%m-%d")
			values = (username, date)
			mycursor.execute(sql, values)
			myresult = mycursor.fetchall()

			if (len(myresult) == 0):
				# print("it's working ")

				sql = "SELECT * FROM attendance where  username=%s and `date`=%s AND `afternoon_time` BETWEEN '17:00' AND '18:00'"
				date = now.strftime("%Y-%m-%d")
				values = (username, date)
				mycursor.execute(sql, values)
				myresult = mycursor.fetchall()

				if (len(myresult) == 0):
					sql = "INSERT INTO `attendance`(`username`, `forenoon`,`afternoon`,`afternoon_time`,`date`) VALUES (%s, %s,%s,%s,%s)"
					date = now.strftime("%Y-%m-%d")
					val = (username, "A", "P", now.strftime("%H:%M"),date)
					mycursor.execute(sql, val)
					mydb.commit()

			else:
				sql = "UPDATE `attendance` SET `afternoon`=%s ,`afternoon_time`=%s  WHERE `username`=%s"
				val = ("P", now.strftime("%H:%M"),username)
				mycursor.execute(sql, val)
				mydb.commit()


face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
eye_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_smile.xml')

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("./recognizers/face-trainner.yml")
labels = {"person_name": 1}

with open("pickles/face-labels.pickle", 'rb') as f:
	og_labels = pickle.load(f)
	labels = {v:k for k,v in og_labels.items()}

cap = cv2.VideoCapture(0)
while(True):
	# Capture frame-by-frame
    ret, frame = cap.read()
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
    for (x, y, w, h) in faces:
    	# print(x,y,w,h)
    	roi_gray = gray[y:y+h, x:x+w] #(ycord_start, ycord_end)
    	roi_color = frame[y:y+h, x:x+w]

    	# recognize? deep learned model predict keras tensorflow pytorch scikit learn
    	id_, conf = recognizer.predict(roi_gray)
    	if conf>=45 and conf <= 85:
    		print(id_)
    		print(labels[id_])
    		markattendance(labels[id_],frm,to)
    		font = cv2.FONT_HERSHEY_SIMPLEX
    		name = labels[id_]

    		color = (255, 255, 255)
    		stroke = 2
    		cv2.putText(frame, name, (x,y), font, 1, color, stroke, cv2.LINE_AA)

    	img_item = "7.png"
    	cv2.imwrite(img_item, roi_color)

    	color = (255, 0, 0) #BGR 0-255
    	stroke = 2
    	end_cord_x = x + w
    	end_cord_y = y + h
    	cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color, stroke)

    	#subitems = smile_cascade.detectMultiScale(roi_gray)
    	#for (ex,ey,ew,eh) in subitems:
    	#	cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
