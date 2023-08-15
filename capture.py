import torch
import numpy as np
import cv2
import time
import uuid
import os
import easyocr
import datetime
import threading
import pyaudio
import wave
from db import check_whitelist
import tkinter as tk
from gui import MainGui

os.chdir(os.path.dirname(os.path.abspath(__file__)))

reader = easyocr.Reader(['en'], gpu=True)

class PlateDetection:
    def __init__(self, capture_index):
        self.capture_index = capture_index
        self.model = self.load_model()
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.duration = 4
        self.time_to_capture = 0
        self.start_timer_detect = 0
        print("Using Device: ", self.device)

    def get_video_capture(self):
        return cv2.VideoCapture(self.capture_index)

    def load_model(self):
        model = torch.hub.load("yolov5", 'custom', path="best.pt", source='local')
        return model

    def score_frame(self, frame):
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        return self.classes[int(x)]

    def filter_text(self, region, ocr_result):
        region_threshold = 0.040
        rectangle_size = region.shape[0]*region.shape[1]
        plate = [] 
        for result in ocr_result:
            length = np.sum(np.subtract(result[0][1], result[0][0]))
            height = np.sum(np.subtract(result[0][2], result[0][1]))
            if (length*height) / rectangle_size > region_threshold:
                plate.append(result[1])
        return plate

    def play_wav(self, file_path):
        CHUNK = 1024
        wf = wave.open(file_path, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def plot_boxes(self, results, frame):
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        

        for i in range(n):
            row = cord[i]
            if row[4] >= 0.8:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                green_color = (0, 255, 0)
                red_color = (0, 0, 255)
                time_remaining = int(self.duration-(time.time() - self.start_timer_detect))
                cv2.putText(frame, f'capturing in {time_remaining}', (x1, y1-30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, green_color, 2)
                if time.time() - self.start_timer_detect >= self.duration:
                    self.start_timer_detect = time.time()
                    margin = 3  # Increase the ROI size by 3 pixels
                    x1 -= margin
                    y1 -= margin
                    x2 += margin
                    y2 += margin

                    roi = frame[max(0, y1):y2, max(0, x1):x2]
                    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    ocr_result = reader.readtext(gray)
                    plate = self.filter_text(gray, ocr_result)
                    # save as image
                    img_name = '{}.jpg'.format(uuid.uuid1())
                    # plate only
                    image_pos = frame[y1:y2, x1:x2]
                    # image_pos = frame
                    cv2.imwrite(os.path.join('./detected_images', img_name), image_pos)
                    time_stamp = datetime.datetime.now().strftime("%B, %d, %Y, %I:%M %p")
                    captured_image_directory = os.path.join('./detected_images', img_name)
                    formatted_plate = ' '.join(plate)
                    # print(formatted_plate, f'percentage: {round(row[4].item()*100)}%')
                    
                    if check_whitelist(formatted_plate):
                        cv2.rectangle(frame, (x1, y1), (x2, y2), green_color, 2)
                        print("its in the whitelist")
                        gui.open_popup(formatted_plate, time_stamp, captured_image_directory, "True")
                    else:
                        self.play_wav('beep.wav')
                        gui.open_popup(formatted_plate, time_stamp, captured_image_directory, "False")
                    self.start_timer_detect = time.time() 
                # print(os.path.join('D:\\Codes\python_\\thesis\\detected', img_name))
                else:
                    # draw rectangle together with the accuracy percentage
                    cv2.rectangle(frame, (x1, y1), (x2, y2), red_color, 2)
                    cv2.putText(frame, self.class_to_label(labels[i]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, green_color, 2)
            else:     
                self.start_timer_detect = time.time()
        
        return frame    
    

    def __call__(self):
        cap = self.get_video_capture()
        if not cap.isOpened():
            cap.open()
            assert cap.isOpened()
        start_time = time.time()
        self.start_timer_detect = time.time()
        while True:
            ret, frame = cap.read()
            # check if ret returns something
            assert ret
            results = self.score_frame(frame)
            frame = cv2.resize(frame, (600, 400))
            frame = self.plot_boxes(results, frame)

            end_time = time.time()
            fps = 1/np.round(end_time - start_time, 2)

            cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.imshow('Plate Number Detection', frame)
           
                
            if cv2.waitKey(5) & 0xFF == ord('q'):
                cap.release()
                break
        cv2.destroyAllWindows()

detector = PlateDetection(capture_index=0)

def start_anpr():
  global t
  t = threading.Thread(target=detector)
  t.start()

gui = MainGui(start_anpr)
gui.mainloop()

