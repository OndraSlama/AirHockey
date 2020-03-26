import numpy as np
import cv2
import matplotlib.pyplot as plt
import random

rg = 0
bg = 0

frame = cv2.imread("airhockey.png").astype("int16")
frame = cv2.GaussianBlur(frame, (11, 11), 0)
greenPart = np.repeat(frame[:,:,1], 3).reshape(frame.shape)
diffToWhite = (frame - greenPart)

vectorized = diffToWhite.reshape((-1,3)).astype("float32")

K = 8
attempts=10
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
ret,label,center=cv2.kmeans(vectorized,K,None,criteria,attempts,cv2.KMEANS_PP_CENTERS)

labels = label.flatten()
mostFrequentLabel = np.argmax(np.bincount(labels))
referenceIndexes = [random.choice(np.argwhere(labels==mostFrequentLabel))[0] for x in range(10)]

referencePixel = diffToWhite.reshape((-1,3))[random.choice(referenceIndexes)] 

rg += referencePixel[0]/500
bg += referencePixel[1]/500


result_mask = (labels == mostFrequentLabel).reshape(frame.shape[0], frame.shape[1]).astype("uint8")
result_image = cv2.bitwise_and(frame, frame, mask=result_mask)

frame = frame.astype("uint8")
result_image = result_image.astype("uint8")


figure_size = 15
plt.figure(figsize=(figure_size,figure_size))
plt.subplot(1,2,1),plt.imshow(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(1,2,2),plt.imshow(cv2.cvtColor(result_image,cv2.COLOR_BGR2RGB))
plt.title('Segmented Image when K = %i' % K), plt.xticks([]), plt.yticks([])
plt.show()

# print(frame)