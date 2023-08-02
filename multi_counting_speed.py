import cv2
import pandas as pd
import pafy
from ultralytics import YOLO
from tracker import *
import time
import cvzone

model = YOLO("yolov8m.pt")


def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        point = [x, y]
        print(point)


cv2.namedWindow("RGB")
cv2.setMouseCallback("RGB", RGB)

# Replace the YouTube URL with the one you want to use
# youtube_url = "https://www.youtube.com/watch?v=PNCJQkvALVc&t=1615s"
# video = pafy.new(youtube_url)
# best_stream = video.getbest(preftype="mp4")
# cap = cv2.VideoCapture(best_stream.url)  # type: ignore

# Replace the video file with the one you want to use
# cap = cv2.VideoCapture("multi.mp4")
cap = cv2.VideoCapture("highway_1280.mp4")

# Replace the Webcam with the one you want to use
# cap = cv2.VideoCapture(0)

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")
# print(class_list)

count = 0
# cy1 = 424
cy1 = 280  # HD
cy2 = 388  # HD
centerline = 622


tracker1 = Tracker()
tracker2 = Tracker()
tracker3 = Tracker()


counter1 = []
counter2 = []
counter3 = []

counter1u = []
counter2u = []
counter3u = []

motorcycle_dn = {}
motorcycle_up = {}

car_dn = {}
car_up = {}

truck_dn = {}
truck_up = {}

offset = 6
up_offset = 6
dn_offset = 13

a_speed_kh = 0
a_speed_kh1 = 0
a_speed_kh3 = 0
a_speed_kh4 = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # count += 1
    # if count % 3 != 0:
    #    continue

    # frame = cv2.resize(frame, (1020, 500))
    frame = cv2.resize(frame, (1280, 720))

    results = model.predict(frame)
    #   print(results)
    a = results[0].boxes.data
    # Type error
    if a.device.type == "cuda":
        a = a.cpu().numpy()

    px = pd.DataFrame(a).astype("float")
    #    print(px)
    list1 = []
    motorcycle = []

    list2 = []
    car = []

    list3 = []
    truck = []

    for index, row in px.iterrows():
        #        print(row)

        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])

        c = class_list[d]
        if "motorcycle" in c:
            list1.append([x1, y1, x2, y2])
            motorcycle.append(c)
        elif "car" in c:
            list2.append([x1, y1, x2, y2])
            car.append(c)
        elif "truck" in c:
            list3.append([x1, y1, x2, y2])
            truck.append(c)

    bbox1_idx = tracker1.update(list1)
    bbox2_idx = tracker2.update(list2)
    bbox3_idx = tracker3.update(list3)

    ####### Motorcycle #######
    for bbox1 in bbox1_idx:
        for i in motorcycle:
            x3, y3, x4, y4, id1 = bbox1
            cxm = int(x3 + x4) // 2
            cym = int(y3 + y4) // 2

            if cy2 < (cym + offset) and cy2 > (cym - offset) and cxm > centerline:
                motorcycle_up[id1] = time.time()
            if id1 in motorcycle_up:
                if cy1 < (cym + offset) and cy1 > (cym - offset) and cxm > centerline:
                    cv2.circle(frame, (cxm, cym), 4, (0, 0, 255), -1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 0, 255), 1)
                    cvzone.putTextRect(frame, f"{id1}", (x3, y3), 1, 1)
                    if counter1u.count(id1) == 0:
                        counter1u.append(id1)

            if cy1 < (cym + offset) and cy1 > (cym - offset) and cxm < centerline:
                motorcycle_dn[id1] = time.time()
            if id1 in motorcycle_dn:
                if cy2 < (cym + offset) and cy2 > (cym - offset) and cxm < centerline:
                    cv2.circle(frame, (cxm, cym), 4, (0, 0, 255), -1)
                    cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 0, 255), 1)
                    cvzone.putTextRect(frame, f"{id1}", (x3, y3), 1, 1)
                    if counter1.count(id1) == 0:
                        counter1.append(id1)

    ####### Car #######
    for bbox2 in bbox2_idx:
        for h in car:
            x5, y5, x6, y6, id2 = bbox2
            cxc = int(x5 + x6) // 2  # center point of Car
            cyc = int(y5 + y6) // 2

            if cy2 < (cyc + up_offset) and cy2 > (cyc - up_offset) and cxc > centerline:
                car_up[id2] = time.time()
            if id2 in car_up:
                if (
                    cy1 < (cyc + up_offset)
                    and cy1 > (cyc - up_offset)
                    and cxc > centerline
                ):
                    elapsed_time = time.time() - car_up[id2]
                    cv2.circle(frame, (cxc, cyc), 4, (0, 255, 0), -1)
                    cv2.rectangle(frame, (x5, y5), (x6, y6), (0, 255, 0), 1)
                    cvzone.putTextRect(frame, f"{id2}", (x5, y5), 1, 1)
                    if counter2u.count(id2) == 0:
                        counter2u.append(id2)
                        distance = 20  # meters
                        a_speed_ms = distance / elapsed_time
                        a_speed_kh = a_speed_ms * 3.6

                    cv2.putText(
                        frame,
                        str(int(a_speed_kh)) + "Km/h",
                        (x6, y6),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.8,
                        (0, 255, 255),
                        2,
                    )

            if cy1 < (cyc + dn_offset) and cy1 > (cyc - dn_offset) and cxc < centerline:
                car_dn[id2] = time.time()
            if id2 in car_dn:
                if (
                    cy2 < (cyc + dn_offset)
                    and cy2 > (cyc - dn_offset)
                    and cxc < centerline
                ):
                    elapsed_time1 = time.time() - car_dn[id2]
                    cv2.circle(frame, (cxc, cyc), 4, (0, 255, 0), -1)
                    cv2.rectangle(frame, (x5, y5), (x6, y6), (0, 255, 0), 1)
                    cvzone.putTextRect(frame, f"{id2}", (x5, y5), 1, 1)
                    if counter2.count(id2) == 0:
                        counter2.append(id2)
                        distance1 = 20  # meters
                        a_speed_ms1 = distance1 / elapsed_time1
                        a_speed_kh1 = a_speed_ms1 * 3.6

                    cv2.putText(
                        frame,
                        str(int(a_speed_kh1)) + "Km/h",
                        (x6, y6),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.8,
                        (0, 255, 255),
                        2,
                    )

    ####### Truck #######
    for bbox3 in bbox3_idx:
        for j in truck:
            x7, y7, x8, y8, id3 = bbox3
            cxt = int(x7 + x8) // 2  # center point of Truck
            cyt = int(y7 + y8) // 2

            if cy2 < (cyt + up_offset) and cy2 > (cyt - up_offset) and cxt > centerline:
                truck_up[id3] = time.time()
            if id3 in truck_up:
                if (
                    cy1 < (cyt + up_offset)
                    and cy1 > (cyt - up_offset)
                    and cxt > centerline
                ):
                    elapsed_time3 = time.time() - truck_up[id3]
                    cv2.circle(frame, (cxt, cyt), 4, (0, 255, 255), -1)
                    cv2.rectangle(frame, (x7, y7), (x8, y8), (0, 255, 255), 1)
                    cvzone.putTextRect(frame, f"{id3}", (x7, y7), 1, 1)
                    if counter3u.count(id3) == 0:
                        counter3u.append(id3)
                        distance3 = 20  # meters
                        a_speed_ms3 = distance3 / elapsed_time3
                        a_speed_kh3 = a_speed_ms3 * 3.6

                    cv2.putText(
                        frame,
                        str(int(a_speed_kh3)) + "Km/h",
                        (x8, y8),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.8,
                        (0, 255, 255),
                        2,
                    )

            if (
                cy1 < (cyt + dn_offset - 20)
                and cy1 > (cyt - dn_offset - 20)
                and cxt < centerline
            ):
                truck_dn[id3] = time.time()
            if id3 in truck_dn:
                if (
                    cy2 < (cyt + dn_offset)
                    and cy2 > (cyt - dn_offset)
                    and cxt < centerline
                ):
                    elapsed_time4 = time.time() - truck_dn[id3]
                    cv2.circle(frame, (cxt, cyt), 4, (0, 255, 255), -1)
                    cv2.rectangle(frame, (x7, y7), (x8, y8), (0, 255, 255), 1)
                    cvzone.putTextRect(frame, f"{id3}", (x7, y7), 1, 1)
                    if counter3.count(id3) == 0:
                        counter3.append(id3)
                        distance4 = 20  # meters
                        a_speed_ms4 = distance4 / elapsed_time4
                        a_speed_kh4 = a_speed_ms4 * 3.6

                    cv2.putText(
                        frame,
                        str(int(a_speed_kh4)) + "Km/h",
                        (x8, y8),
                        cv2.FONT_HERSHEY_COMPLEX,
                        0.8,
                        (0, 255, 255),
                        2,
                    )

    cv2.line(frame, (216, cy1), (950, cy1), (0, 0, 255), 1)
    cv2.putText(
        frame, ("L1"), (175, 280), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2
    )
    cv2.line(frame, (0, cy2), (1173, cy2), (0, 0, 255), 1)
    cv2.putText(frame, ("L2"), (0, 380), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)

    # Print counter
    motorcyclec = len(counter1)
    motorcyclecu = len(counter1u)
    cvzone.putTextRect(
        frame, f"motorcycle down:{motorcyclec}  up:{motorcyclecu}", (20, 40), 2, 1
    )

    carc = len(counter2)
    carcu = len(counter2u)
    cvzone.putTextRect(frame, f"car down:{carc}  up:{carcu}", (20, 90), 2, 1)

    truckc = len(counter3)
    truckcu = len(counter3u)
    cvzone.putTextRect(frame, f"truck down:{truckc}  up:{truckcu}", (20, 140), 2, 1)

    cv2.imshow("RGB", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
