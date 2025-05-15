import os
import uuid
import requests
from io import BytesIO
from PIL import Image, ExifTags
import cv2
import numpy as np
from config import UPLOAD_FOLDER

def download_image(url):
    """Download image from URL"""
    response = requests.get(url)
    return BytesIO(response.content)

def remove_metadata(image):
    """Remove EXIF metadata from image"""
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    return image_without_exif

def blur_faces(image_path):
    """Detect and blur faces in an image"""
    # Load pre-trained face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Read the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    # Blur each face
    for (x, y, w, h) in faces:
        # Apply stronger Gaussian blur to face region
        face_roi = image[y:y+h, x:x+w]
        blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 30)
        image[y:y+h, x:x+w] = blurred_face
    
    # Save the image with blurred faces
    cv2.imwrite(image_path, image)
    
    return image_path

def process_image(image_url):
    """Process image: download, remove metadata, blur faces, and save"""
    # Download image
    image_data = download_image(image_url)
    image = Image.open(image_data)
    
    # Remove EXIF metadata
    clean_image = remove_metadata(image)
    
    # Generate unique filename
    filename = str(uuid.uuid4()) + '.jpg'
    output_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save cleaned image
    clean_image.save(output_path)
    
    # Blur faces
    blur_faces(output_path)
    
    return output_path