import sys
import cv2 
import imutils
from JetsonYoloV7TensorRT.yoloDet import YoloTRT
import track
import send_data

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


# use path for library and engine file
model = YoloTRT(library="JetsonYoloV7TensorRT/yolov7/build/libmyplugins.so", engine="JetsonYoloV7TensorRT/yolov7/build/yolov7-tiny.engine", conf=0.5, yolo_ver="v7")

cap = cv2.VideoCapture("/home/jetson/Downloads/mapy.mp4")
# cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)

font = cv2.FONT_HERSHEY_SIMPLEX

# display = False
display = True

track.display(display)

send_data.start(min=1)

while True:
    ret, frame = cap.read()

    # for video loop
    if not ret:
       cap.set(cv2.CAP_PROP_POS_FRAMES, 10)
       continue

    frame = imutils.resize(frame, width=600)
    detections, t = model.Inference(frame)
    track.update(detections,model.categories,frame)


    fps = "FPS: {} | COUNT: {},{}".format(int(1/t),track.counter[0],track.counter[1])
    
    if display:
        cv2.putText(frame, fps, (3, 20), font, 0.5, (100, 255, 0), 1, cv2.LINE_AA) 
        cv2.imshow("Output", imutils.resize(frame, width=1080))
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    else:
        print(fps)
cap.release()
cv2.destroyAllWindows()
