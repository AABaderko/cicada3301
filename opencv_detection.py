import cv2
import numpy as np

from place_data import places_data

dot_amount = []

Image1 = cv2.imread("place_photos\domGRES2.jpg")

sift = cv2.SIFT_create()
keypoint1, descriptor1 = sift.detectAndCompute(Image1,None)
for obj in places_data:
    Image2 = cv2.imread(obj.get("img"))
    keypoint2, descriptor2 = sift.detectAndCompute(Image2,None)

    index_parameter = dict(algorithm = 0,trees = 5)
    search_parameter = dict()
    flann = cv2.FlannBasedMatcher(index_parameter,search_parameter)

    matches = flann.knnMatch(descriptor1,descriptor2,k=2)

    good_point_array = []
    for i, j in matches:
        if i.distance < 0.7*j.distance:
            good_point_array.append(i)
    
    dot_amount.append(len(good_point_array))

print(dot_amount)
# resultant_match = cv2.drawMatches(Image1, keypoint1, Image2, keypoint2, good_point_array, None)

# print(len(good_point_array))
# cv2.imshow("resultant_match",resultant_match)
# cv2.waitKey(0)