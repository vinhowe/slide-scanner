from pyimagesearch.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils
from google.cloud import vision
from google.cloud.vision import types
import io
from matplotlib import pyplot as plt
from enum import Enum
import requests
from PIL import Image, ImageEnhance, ImageDraw
from io import BytesIO
from time import sleep

# To allow me time to grab my phone and aim it at something
sleep(3)

r = requests.get('http://192.168.1.105:8080/photo.jpg')
i = Image.open(BytesIO(r.content))

enhancer = ImageEnhance.Sharpness(i)
enhanced_im = enhancer.enhance(2)

image = cv2.cvtColor(np.array(enhanced_im), cv2.COLOR_RGB2BGR)

# ratio = image.shape[0] / 500.0
orig = image.copy()
# image = imutils.resize(image, height = 500)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)

cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

for c in cnts:
	peri = cv2.arcLength(c, True)
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)

	if len(approx) == 4:
		screenCnt = approx
		break

warped = four_point_transform(orig, screenCnt.reshape(4, 2))

# warped = cv2.resize(warped, (1920, 1080))

im_pil = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
post_enhancer = ImageEnhance.Sharpness(im_pil)

post_im = post_enhancer.enhance(10)

post_enhancer = ImageEnhance.Contrast(post_im)

post_im = post_enhancer.enhance(2)

post_im.save('temp.jpg')

# Instantiates a client
client = vision.ImageAnnotatorClient.from_service_account_json(
        'client_account_conf.json')

# # The name of the image file to annotate
# file_name = os.path.abspath('resources/wakeupcat.jpg')

# # Loads the image into memory
# with io.open(file_name, 'rb') as image_file:
#     content = image_file.read()

buffer = io.BytesIO()
post_im.save(buffer, "JPEG")
content = buffer.getvalue()

vision_image = types.Image(content=content)

# Performs label detection on the image file
response = client.document_text_detection(image=vision_image)
text = response.text_annotations[0].description
print(text)
