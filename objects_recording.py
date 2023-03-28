from tkinter.font import families
import cv2
import time
from datetime import date, datetime
import pandas


#Declaring variable without value to use it later on
first_frame = None 

#Declaring variable used to start / stop recording
record_status = None
videono = 0
recording = False

#creating video writer object to record and save a video
fcc = cv2.VideoWriter_fourcc(*'XVID')

#Trigger the PC camera; 0 because we've got only one camera
video = cv2.VideoCapture(0) 

#declaring list for detecting history graph
status_list = [0,0]
times = []

#declaring pandas dataframe to track frames changes
df = pandas.DataFrame(columns=["Start", "End"])

#Loop which captures the video
while True:
    check, frame = video.read()  #check when the video is visible, reading the frame
    original_frame = frame.copy() #copying frame to have original video
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #convert frame to gray scale
    gray = cv2.GaussianBlur(gray,(21,21),0) #blurry the image to mitigate noise, commonly used parameters

    #showing current time in the video frame
    hms = time.strftime('%H:%M:%S', time.localtime())
    cv2.putText(frame, str(hms), (0, 15), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255))

    status = 0 #status of the frame changes is 0 because we only capture the first frame for the moment

    #conditional which executes only in the first iteration to catch the very first frame
    if first_frame is None:
        first_frame = gray
        continue #comes directly to the beginning of the while loop after first iteration

    delta_frame = cv2.absdiff(first_frame,gray) #difference between first frame and subsequent ones, difference is shown in white pixels
    # print(delta_frame) #numpy array with the pixels difference between two frames

    thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1] #threshold to make the difference black and white, difference between pixels is more than 30 to consider it as a change, 255 is the color of the difference, threshold method is in general changing pixels after some value to different colors

    (cnts,_) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #function to find contours

    for contour in cnts:
        if cv2.contourArea(contour) < 1000:  #consider only contours which has got area > 1000 pixels
            continue
        status = 1  # value of 1 when we detect changes
        (x,y,w,h) = cv2.boundingRect(contour)  #saving contours parameters
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 3) #writing rectangle based on the parameters

    status_list.append(status) #we add status to the list for tracking purpose

    status_list = status_list[-2:] #we only keep last 2 values to save the memory

    if status_list[-1] == 1 and status_list[-2] == 0:   #moment when there was a change in the list -> ...,0,1,...
        times.append(datetime.now())
        record_status = 'start'
    if status_list[-1] == 0 and status_list[-2] == 1:   # change back to 0
        times.append(datetime.now())
        record_status = 'stop'

    cv2.imshow("Gray Frame", gray) #showing the gray frame
    cv2.imshow("Delta Frame", delta_frame) #showing delta frame
    cv2.imshow("Threshold Delta Frame", thresh_frame) #showing trashold difference
    cv2.imshow("Color Frame", frame) #showing original video with contours
    cv2.imshow("Original Frame", original_frame) #showing original video

    key = cv2.waitKey(1) #closing the frame after 1 milisec

    if key == ord('q'): #breaking the loop - closing the video after pressing 'q'
        if status == 1:
            times.append(datetime.now()) #saving switch off time when object is being detected
        break 

    #print(status) #printing status of changes for visibility
    #print(record_status)

    #conditions to save the video while detecting an object
    if(record_status == 'start' and recording == False):
        path = 'c:/Users/kamx9/OneDrive/Pulpit/PC Programming-20220117T222949Z-001/PC Programming/Python/MyApps/Security_Camera/record' + str(videono) + '.avi'
        videono += 1
        print(path+' recording')
        writer = cv2.VideoWriter(path, fcc, 30.0, (int(video.get(3)), int(video.get(4))))
        recording = True
    if(recording):
        writer.write(frame)
    if(record_status == 'stop' and recording):
        print("recording finished")
        recording = False
        writer.release()


print(status_list)
print(times)

for i in range(0,len(times),2):   #iterating through times and saving values to dataframe
    df = df.append({"Start":times[i], "End":times[i+1]}, ignore_index = True)

print(df)
df.to_csv("Times.csv")  #saving data tracking to csv file

video.release() #closing the camera
cv2.destroyAllWindows #closing all windows





