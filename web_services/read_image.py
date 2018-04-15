import cv2
import numpy as np

def arnold(img):
    width = img.shape[0]
    height = img.shape[1]
    output = img.copy()
    for i in range(width):
        for j in range(height):
            pixel = img[i][j]
            output[(2*i+j) % width][(i+j) % height] = pixel
    return output
    
def anti_arnold(img):
    width = img.shape[0]
    height = img.shape[1]
    anti = img.copy()
    for i in range(width):
        for j in range(height):
            pixel = img[i][j]
            anti[(i-j) % width][(-i+2*j) % height] = pixel
    return anti

def arnold_iteration(data,N):
    output = data
    for i in range(N):
        output = arnold(output)
    return output

def anti_arnold_iteration(data, N):
    output = data
    for i in range(N):
        output = anti_arnold(output)
    return output

def arnold_from_file(file,N):
    img = cv2.imread(file,0)
    if img is not None:
        (thresh, im_bw) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        # cv2.imwrite('../sample/blackwhite.jpg', im_bw)
        output = arnold_iteration(im_bw, N)
        return output
    else:
        None

def anti_arnold_from_file(file,N):
    img = cv2.imread(file,0)
    if img is not None:
        (thresh, im_bw) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        output = anti_arnold_iteration(im_bw, N)
        return output
    else:
        return None

    
if __name__ == '__main__':
    ##arnold
    output = arnold_from_file('../sample/final.jpg',13)
    ## anti arnold
    anti = anti_arnold_iteration(output, 13)
    cv2.imshow('arnold',output)
    cv2.imshow('anti-arnold',anti)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
