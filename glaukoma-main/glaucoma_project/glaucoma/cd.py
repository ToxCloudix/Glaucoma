from scipy import signal
import cv2
import numpy as np
from matplotlib import pyplot as plt

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(10,10))

#crop to region of interest
def crop_to_roi(image, crop_radius=350):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(gray, dtype=np.uint8)
    center_x, center_y = gray.shape[1] // 2, gray.shape[0] // 2
    radius = min(center_x, center_y)
    cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(masked_gray)
    x, y = max_loc
    x_start = max(x - crop_radius, 0)
    x_end = min(x + crop_radius, image.shape[1])
    y_start = max(y - crop_radius, 0)
    y_end = min(y + crop_radius, image.shape[0])
    cropped_image = image[y_start:y_end, x_start:x_end]
    return cropped_image

#disc and cup segmantation
def segment(image, plot_hist=False, plot_seg=False):
    # Обрезаем изображение до ROI
    image = crop_to_roi(image)
    # Разбиваем на каналы
    Abo, Ago, Aro = cv2.split(image)
    Aro = clahe.apply(Aro)
    M = 60
    filt = signal.windows.gaussian(M, std=6)
    STDf = filt.std()
    
    Ar = Aro - Aro.mean() - Aro.std()
    Mr = Ar.mean()
    SDr = Ar.std()
    Thr = 0.5*M - STDf - SDr

    M = 20
    filter_cup = signal.windows.gaussian(M, std=6)
    STDf = filter_cup.std()
    
    Ag = Ago - Ago.mean() - Ago.std()
    Mg = Ag.mean()
    SDg = Ag.std()
    Thg = 0.5*M + 2*STDf + 2*SDg + Mg

    # По гистограмме (можно оставить, если нужно для отладки)
    if plot_hist:
        hist, bins = np.histogram(Ag.ravel(), 256, [0,256])
        histr, binsr = np.histogram(Ar.ravel(), 256, [0,256])
        smooth_hist_g = np.convolve(filt, hist)
        smooth_hist_r = np.convolve(filter_cup, histr)
        plt.figure(figsize=(8,8))
        plt.subplot(2,2,1)
        plt.plot(hist)
        plt.title("Preprocessed Green Channel")
        plt.subplot(2,2,2)
        plt.plot(smooth_hist_g)
        plt.title("Smoothed Histogram Green Channel")
        plt.subplot(2,2,3)
        plt.plot(histr)
        plt.title("Preprocessed Red Channel")
        plt.subplot(2,2,4)
        plt.plot(smooth_hist_r)
        plt.title("Smoothed Histogram Red Channel")
        plt.show()

    r, c = Ag.shape
    Dd = np.zeros((r, c), dtype=np.uint8)
    Dc = np.zeros((r, c), dtype=np.uint8)
    
    # Сегментация диска (пороговое значение для красного канала)
    for i in range(1, r):
        for j in range(1, c):
            Dd[i,j] = 255 if Ar[i,j] > Thr else 0

    # Сегментация чаши (пороговое значение для зелёного канала)
    for i in range(1, r):
        for j in range(1, c):
            Dc[i,j] = 255 if Ag[i,j] > Thg else 0

    if plot_seg:
        plt.figure(figsize=(12, 6))
        plt.subplot(1,3,1)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title("Original Image")
        plt.axis("off")
        plt.subplot(1,3,2)
        plt.imshow(Dd, cmap='gray')
        plt.title("Optic Disk")
        plt.axis("off")
        plt.subplot(1,3,3)
        plt.imshow(Dc, cmap='gray')
        plt.title("Optic Cup")
        plt.axis("off")
        plt.show()

    # Возвращаем сегментированные изображения
    return Dd, Dc

def cdr(cup,disc,plot):
    
    #morphological closing and opening operations
    R1 = cv2.morphologyEx(cup, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2)), iterations = 1)
    r1 = cv2.morphologyEx(R1, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)), iterations = 1)
    R2 = cv2.morphologyEx(r1, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(1,21)), iterations = 1)
    r2 = cv2.morphologyEx(R2, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(21,1)), iterations = 1)
    R3 = cv2.morphologyEx(r2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(33,33)), iterations = 2)
    img = R3
    if len(img.shape) == 3:  #  if image has >1 chanels
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img.astype('uint8')
    ret,thresh = cv2.threshold(img,127,255,0)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) #Getting all possible contours in the segmented image
    cup_diameter = 0
    largest_area = 0
    el_cup = contours[0]
    if len(contours) != 0:
        for i in range(len(contours)):
            if len(contours[i]) >= 5:
                area = cv2.contourArea(contours[i]) 
                if (area>largest_area):
                    largest_area=area
                    index = i
                    el_cup = cv2.fitEllipse(contours[i])
                
    cv2.ellipse(img,el_cup,(140,60,150),3)
      
    x,y,w,h = cv2.boundingRect(contours[index]) 
    cup_diameter = max(w,h)


    #morphological closing and opening operations
    R1 = cv2.morphologyEx(disc, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2)), iterations = 1)
    r1 = cv2.morphologyEx(R1, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)), iterations = 1)
    R2 = cv2.morphologyEx(r1, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(1,21)), iterations = 1)
    r2 = cv2.morphologyEx(R2, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(21,1)), iterations = 1)
    R3 = cv2.morphologyEx(r2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(33,33)), iterations = 1)
    r3 = cv2.morphologyEx(R3, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(43,43)), iterations = 1)
    img2 = r3

    if len(img2.shape) == 3:  # if image has >1 chanels
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    img2 = img2.astype('uint8')
    
    ret,thresh = cv2.threshold(img2,127,255,0)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    disk_diameter = 0
    largest_area = 0
    el_disc = el_cup
    if len(contours) != 0:
          for i in range(len(contours)):
            if len(contours[i]) >= 5:
                area = cv2.contourArea(contours[i]) 
                if (area>largest_area):
                    largest_area=area
                    index = i
                    el_disc = cv2.fitEllipse(contours[i])
                    
            cv2.ellipse(img2,el_disc,(140,60,150),10) 
            x,y,w,h = cv2.boundingRect(contours[index]) 
    disk_diameter = max(w,h)
                
    if plot:
        plt.imshow(img2, 'gray',interpolation = 'bicubic')
        plt.axis("off")
        plt.title("Optic Disk")
        plt.show()
        plt.imshow(img, 'gray')
        plt.axis("off")
        plt.title("Optic Cup")
        plt.show()
        
    if(disk_diameter == 0): return 1 
    cdr = cup_diameter/disk_diameter 
    return cdr, img, img2