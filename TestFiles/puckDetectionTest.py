import numpy as np
import cv2
import matplotlib.pyplot as plt
import random

rg = 0
bg = 0

frame = cv2.imread("puckdetection2.png")
frame = cv2.GaussianBlur(frame, (11, 11), 0)

vectorized = frame.reshape((-1,3)).astype("float32")

K = 4
attempts = 10
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
ret,label,center = cv2.kmeans(vectorized,K,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)

labels = label.flatten()
mostFrequentLabel = np.argmax(np.bincount(labels))

detectedColor = cv2.cvtColor(np.uint8([[center[mostFrequentLabel]]]),cv2.COLOR_BGR2HSV)[0,0,:]
hueInterval = 30
othersInterval = 150

Hl = detectedColor[0] - hueInterval/2
if Hl < 0: Hl += 179

Hh = detectedColor[0] + hueInterval/2
if Hh > 179: Hh -= 179

lowerLimit = np.uint8([Hl, max(5, detectedColor[1] - othersInterval/2), max(5, detectedColor[2] - othersInterval/2)])
higherLimit = np.uint8([Hh, min(255, detectedColor[1] + othersInterval/2), min(255, detectedColor[2] + othersInterval/2)])

if lowerLimit[0] > higherLimit[0]:
	lowerLimit1 = np.uint8(lowerLimit)
	higherLimit1 = np.uint8([179, higherLimit[1], higherLimit[2]])
	lowerLimit2 = np.uint8([0, lowerLimit[1], lowerLimit[2]])
	higherLimit2 = np.uint8(higherLimit)

	mask1 = cv2.inRange(frame, lowerLimit1, higherLimit1)
	mask2 = cv2.inRange(frame, lowerLimit2, higherLimit2)


result_mask = (labels == mostFrequentLabel).reshape(frame.shape[0], frame.shape[1]).astype("uint8")
result_image = center[labels].reshape(frame.shape)
result_image = cv2.bitwise_and(result_image, result_image, mask=result_mask)


figure_size = 15
plt.figure(figsize=(figure_size,figure_size))
plt.subplot(1,2,1),plt.imshow(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(1,2,2),plt.imshow(cv2.cvtColor(result_image,cv2.COLOR_BGR2RGB))
plt.title('Segmented Image when K = %i' % K), plt.xticks([]), plt.yticks([])
plt.show()

# print(frame)