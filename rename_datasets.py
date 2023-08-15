import os, re

IMAGE_PATH = 'D:\\Codes\\python_\\thesis\\plate_numbers_dataset\\images'
files = os.listdir(IMAGE_PATH)


for x in range(len(files)):
  if f'{IMAGE_PATH}\\{x}.jpg' != f'{IMAGE_PATH}\\{files[x]}':
    os.rename(f'{IMAGE_PATH}\\{files[x]}', f'{IMAGE_PATH}\\{x}.jpg')

    
  