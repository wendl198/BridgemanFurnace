import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
from datetime import datetime

segment_to_number = {
    (0, 0, 0, 0, 0, 0, 0): '',
    (1, 1, 1, 0, 1, 1, 1): '0',
    (0, 0, 1, 0, 0, 1, 0): '1',
    (1, 0, 1, 1, 1, 0, 1): '2',
    (1, 0, 1, 1, 0, 1, 1): '3',
    (0, 1, 1, 1, 0, 1, 0): '4',
    (1, 1, 0, 1, 0, 1, 1): '5',
    (1, 1, 0, 1, 1, 1, 1): '6',
    (1, 0, 1, 0, 0, 1, 0): '7',
    (1, 1, 1, 1, 1, 1, 1): '8',
    (1, 1, 1, 1, 0, 1, 1): '9'
}#[Top,Upper left,Upperright,middle,lower left,lower right, bottom]

thres = 150

def extract_text_from_frame(frame,thres):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, gray_frame = cv2.threshold(gray_frame, thres, 1, cv2.THRESH_BINARY)

    num1,num2,num3,num4,dec = get_pixels(gray_frame)
    if dec:
        try:
            return float(segment_to_number[num1] + segment_to_number[num2] + segment_to_number[num3] + '.' + segment_to_number[num4])
        except (KeyError, ValueError):
            # print(num1,num2,num3,num4,dec)
            # plt.imshow(frame)
            # plt.show()
            return 0
    else:
        try:
            return float(segment_to_number[num1] + segment_to_number[num2] + segment_to_number[num3] + segment_to_number[num4])
        except (KeyError, ValueError):
            return 0

def main(video_path):
    cap = cv2.VideoCapture(video_path)
    data = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        text = extract_text_from_frame(frame,thres) #returned as a float
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        # print(text,timestamp)
        if len(data) == 0:
            data.append([timestamp, text])
        elif text != data[-1][1]:#filters out repeated points
            if text == 0 and len(data)>1:
                data.append([timestamp, data[-1][1]])
            else:
                data.append([timestamp, text])
    
    cap.release()
    
    return data

def onclick(event):
    global pixel_coordinates, counter
    
    if event.button == 1:  # Left mouse button click
        x, y = int(event.xdata), int(event.ydata)
        pixel_coordinate = (x, y)
        # print(f"Clicked pixel coordinates: {pixel_coordinate}")
        
        pixel_coordinates.append(pixel_coordinate)
        counter += 1
        
        if counter >= 29:
            plt.disconnect(cid)  # Disconnect the click event listener when done
            plt.close()
            # print("Pixel coordinates:", pixel_coordinates)

def get_pixels(img):
    output = [[],[],[],[],0]
    for i,pixel in enumerate(pixel_coordinates):
        if i <28:
            output[i//7].append(img[pixel[1]][pixel[0]])
        else:
            output[4] = img[pixel[1]][pixel[0]]
    return tuple(output[0]),tuple(output[1]),tuple(output[2]),tuple(output[3]),output[4]

folderpath = "C:/Users/Contactless/Desktop/TempVideos/GrowthTemp"
video_paths = os.listdir(folderpath)

#check for success
#print(folderpath+'/'+video_paths[0])
cap = cv2.VideoCapture(folderpath+'/'+video_paths[0])
ret, frame = cap.read()  # Read the first frame

if not ret:
    if cap.isOpened():  # Check if the video file is still open
        print("End of video.")
    else:
        print("Error reading the next frame. Check the video file and format.")
        exit()

#get pixel coords
pixel_coordinates = []
counter = 0
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
plt.imshow(frame)
plt.axis('off')  # Turn off axis labels and ticks
cid = plt.connect('button_press_event', onclick)
plt.show()
cap.release()  # Release the video capture



times = [] #relative time
temps = []
start_times = []


#time to collect the data from each video (this may take a while)
for i, video_path in enumerate(video_paths):
    times.append([])
    temps.append([])
    extracted_data = main(folderpath+'/'+video_path)
    for data in extracted_data:
        times[i].append(data[0]/60)
        temps[i].append(data[1])    
    date_time_str = video_path.split('.')[0]
    date_time_format = "%Y-%m-%d %H-%M-%S"# Define the format of the input string
    date_time_obj = datetime.strptime(date_time_str, date_time_format)# Parse the input string into a datetime object
    start_times.append(date_time_obj.timestamp())# Convert the datetime object to a Unix timestamp
    print(date_time_str)
    #t_data = video_path[-16:-8].split('_')
    #t_start = int(t_data[0])*60+int(t_data[1])+int(t_data[2])/60 #time in min

    times[i] = np.array(times[i])

    #remove outliers
    for j in range(len(temps)-5):
        avg1 = np.average([temps[i][j],temps[i][j+1]])
        avg2 = np.average([temps[i][j+3],temps[i][j+4]])
        if temps[i][j+2]<min(avg1,avg2)*.975 or temps[i][j+2]>max(avg1,avg2)*1.025:
            temps[i][j+2] = np.average([avg1,avg2])


#save file stuff
save_path = "C:/Users/Contactless/Desktop/TempVideos/GrowthTempData"
save_file = open(save_path +'/'+ video_paths[0].split('.')[0] + ".dat", "w")
save_file.write("Time (min)" + "\t" 'Temp (C)'+'\t'+"\n")
for i in range(len(times)):
    for j in range(len(times[i])):
        save_file.write(str(times[i][j]+(start_times[i]-start_times[0])/60)+ "\t"+str(temps[i][j])+'\n')
save_file.close()

#plot temp v time
fig1 = plt.figure(constrained_layout = True)
ax = fig1.add_subplot(1, 1, 1)
for i in range(len(times)):
    ax.scatter(times[i]+(start_times[i]-start_times[0])/60,temps[i])
# ax.scatter(handtime,handtemp)
for i,path in enumerate(video_paths):
    video_paths[i] = path[len('C:/Users/blake/Downloads/WIN_20230816_'):]
ax.legend(video_paths)
ax.set_xlabel('Time (min)')
ax.set_ylabel('Temp (C)')
plt.show()
