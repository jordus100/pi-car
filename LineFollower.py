import cv2

# open image
img = cv2.imread('cam.png')
# crop to bottom 1/4 of the image
img = img[img.shape[0]//4*3:, :]
# show the image
cv2.imshow('crop', img)
# filter out everything but the black color
mask = cv2.inRange(img, (0, 0, 0), (50, 50, 50))
cv2.imshow('mask', mask)
cv2.waitKey(0)