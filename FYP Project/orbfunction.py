import cv2
import numpy as np
import os
import winsound
consecutive_threshold = 8


def import_images(path):
    images = []
    classNames = []

    mylist = os.listdir(path)

    for cl in mylist:
        imageCur = cv2.imread(f'{path}/{cl}', 0)
        images.append(imageCur)
        classNames.append(os.path.splitext(cl)[0])

    return images, classNames


def findDes(images):
    orb = cv2.ORB_create(nfeatures=1500)
    desList = []
    for img in images:
        kp, des = orb.detectAndCompute(img, None)
        desList.append(des)
    return desList


def findID(img, desList, thres =15):
    orb = cv2.ORB_create(nfeatures=1500)
    kp2, des2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matchList = []
    finalVal = -1
    try:
        for des in desList:
            matches = bf.knnMatch(des, des2, k=2)
            good = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good.append([m])
            matchList.append(len(good))
        # print(matchList)
    except:
        pass

    if len(matchList) != 0:
        if max(matchList) > thres:
            finalVal = matchList.index(max(matchList))
    return finalVal


def record_consecutive_appearances(class_name, counter):
    if "previous_class_name" not in counter:
        counter["previous_class_name"] = None

    if class_name == counter["previous_class_name"]:

        if class_name in counter:
            counter[class_name] += 1
            print(f"Counter now for {class_name}: {counter[class_name]}")
            if counter[class_name] == consecutive_threshold:
                print(f"Consecutive appearances reached {consecutive_threshold} for {class_name}!")
                # 在达到阈值后，你可以在这里执行特定的操作
                result = f"Result for {class_name}"
                # 重置计数
                counter[class_name] = 0
                return True
        else:
            counter[class_name] = 1

    else:
        counter[class_name] = 1
    counter["previous_class_name"] = class_name

    return False


def make_noise():
  duration = 1200  # milliseconds
  freq = 440  # Hz
  winsound.Beep(freq, duration)