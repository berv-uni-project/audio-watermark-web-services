""" Image Watermarking Proccessor """

import cv2

def arnold(img):
    """Arnold Transform from image matrix, one time"""
    width = img.shape[0]
    height = img.shape[1]
    out = img.copy()
    for i in range(width):
        for j in range(height):
            pixel = img[i][j]
            out[(2 * i + j) % width][(i + j) % height] = pixel
    return out

def anti_arnold(img):
    """Anti Arnold 1 times"""
    width = img.shape[0]
    height = img.shape[1]
    out = img.copy()
    for i in range(width):
        for j in range(height):
            pixel = img[i][j]
            out[(i - j) % width][(-i + 2 * j) % height] = pixel
    return out

def arnold_iteration(data, n_round):
    """ N-time arnold transform """
    out = data
    for i in range(n_round): # pylint: disable=unused-variable
        out = arnold(out)
    return out

def arnold_rgb_iteration(file_name, n_round):
    """ N-time arnold with BGR """
    img = cv2.imread(file_name, 1)
    if img is not None:
        b, g, r = cv2.split(img)
        for i in range(n_round):
            b = arnold(b)
            g = arnold(g)
            r = arnold(r)
        return b,g,r
    else:
        return None, None, None

def anti_arnold_rgb_iteration(b, g, r, n_round):
    r_new = r
    g_new = g
    b_new = b
    if (r is not None) and (g is not None) and (b is not None):
        for i in range(n_round):
            r_new = anti_arnold(r_new)
            g_new = anti_arnold(g_new)
            b_new = anti_arnold(b_new)
    return b_new, g_new, r_new

def anti_arnold_iteration(data, n_round):
    """ N-time anti-arnold transform """
    out = data
    for i in range(n_round): # pylint: disable=unused-variable
        out = anti_arnold(out)
    return out

def arnold_from_file(file, n_times):
    """ Arnold transform from file"""
    img = cv2.imread(file, 0) # pylint: disable=no-member
    out = None
    if img is not None:
        out = arnold_iteration(img, n_times)
    return out

def anti_arnold_from_file(file, n_times):
    """ Anti Arnold from file"""
    img = cv2.imread(file, 0) # pylint: disable=no-member
    out = None
    if img is not None:
        out = anti_arnold_iteration(img, n_times)
    return out


if __name__ == '__main__':
    # arnold
    OUTPUT = arnold_from_file('../sample/final.jpg', 13)
    # anti arnold
    ANTI = anti_arnold_iteration(OUTPUT, 13)
    cv2.imshow('arnold', OUTPUT) # pylint: disable=no-member
    cv2.imshow('anti-arnold', ANTI) # pylint: disable=no-member
    cv2.waitKey(0) # pylint: disable=no-member
    cv2.destroyAllWindows() # pylint: disable=no-member
