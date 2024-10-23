import cv2
import numpy as np
import imutils
from pytesseract import Output
from PIL import Image
import pytesseract

#Document image orientation correction
#This approach is based on text orientation

#Assumption: Document image contains all text in same orientation

# debug = True

#Display image
# def display(img, frameName="OpenCV Image"):
#     h, w = img.shape[0:2]
#     neww = 800
#     newh = int(neww*(h/w))
#     img = cv2.resize(img, (neww, newh))
#     cv2.imshow(frameName, img)
#     cv2.waitKey(0)

def order_corners(corners):
    # Sắp xếp lại các góc (trái trên, phải trên, phải dưới, trái dưới)
    rect = np.zeros((4, 2), dtype="float32")

    s = corners.sum(axis=1)
    rect[0] = corners[np.argmin(s)]  # Trái trên (x + y nhỏ nhất)
    rect[2] = corners[np.argmax(s)]  # Phải dưới (x + y lớn nhất)

    diff = np.diff(corners, axis=1)
    rect[1] = corners[np.argmin(diff)]  # Phải trên (x - y nhỏ nhất)
    rect[3] = corners[np.argmax(diff)]  # Trái dưới (x - y lớn nhất)

    return rect

def crop_paper_from_image(img, corners):
    # Sắp xếp lại các đỉnh theo đúng thứ tự
    rect = order_corners(corners.reshape(4, 2))
    
    # Tính chiều rộng và chiều cao của tờ giấy sau khi cắt
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    # Xác định điểm đích cho hình chữ nhật chuẩn
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # Phép biến đổi phối cảnh (perspective transform)
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    return warped

#rotate the image with given theta value
def rotate(img, theta):
    if np.abs(theta) <= 7:
        return img
    else:
        rotated = imutils.rotate_bound(img, -theta)
        
        # Chuyển ảnh sang grayscale
        gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Dùng Canny edge detection để tìm các cạnh của tờ giấy
        edges = cv2.Canny(blurred, 50, 150)
        
        # Áp dụng phép co dãn (dilate) và xói mòn (erode) để làm rõ các cạnh
        edges = cv2.dilate(edges, None, iterations=2)
        edges = cv2.erode(edges, None, iterations=1)

        # Tìm tất cả các contour
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            print("Không tìm thấy contour nào.")
            return None

        # Tạo danh sách để lưu các góc
        corners = []

        for contour in contours:
            # Dùng hàm approxPolyDP để tìm hình đa giác gần đúng
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) == 4:  # Nếu contour có 4 góc
                corners.append(approx)

        if len(corners) == 0:
            # print("Không tìm thấy contour có 4 góc.")
            return img

        # Lấy các điểm từ góc
        selected_corners = corners[0].reshape(4, 2)

        # Sắp xếp các góc theo vị trí
        top_left = selected_corners[np.argmin(selected_corners[:, 0] + selected_corners[:, 1])]  # Góc trái trên
        top_right = selected_corners[np.argmin(-selected_corners[:, 0] + selected_corners[:, 1])]  # Góc phải trên
        bottom_left = selected_corners[np.argmax(selected_corners[:, 0] + selected_corners[:, 1])]  # Góc trái dưới
        bottom_right = selected_corners[np.argmax(-selected_corners[:, 0] + selected_corners[:, 1])]  # Góc phải dưới

        # Tạo danh sách chứa 4 góc đã chọn
        final_corners = np.array([top_left, top_right, bottom_left, bottom_right])

        return crop_paper_from_image(rotated, final_corners)



def slope(x1, y1, x2, y2):
    if x1 == x2:
        return 0
    slope = (y2-y1)/(x2-x1)
    theta = np.rad2deg(np.arctan(slope))
    return theta


def Cv2_rotate(image_path):
    img = cv2.imread(image_path)
    textImg = img.copy()

    small = cv2.cvtColor(textImg, cv2.COLOR_BGR2GRAY)

    #find the gradient map
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)

    #Binarize the gradient image
    _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # display(bw)

    #connect horizontally oriented regions
    #kernal value (9,1) can be changed to improved the text detection
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    # display(connected)

    # using RETR_EXTERNAL instead of RETR_CCOMP
    # _ , contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) #opencv >= 4.0



    mask = np.zeros(bw.shape, dtype=np.uint8)
    # display(mask)
    #cumulative theta value
    cummTheta = []
    #number of detected text regions
    ct = 0
    for idx in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[idx])
        mask[y:y+h, x:x+w] = 0
        #fill the contour
        cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
        # display(mask)
        #ratio of non-zero pixels in the filled region
        r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)

        #assume at least 45% of the area is filled if it contains text
        if r > 0.45 and w > 8 and h > 8:
            #cv2.rectangle(textImg, (x1, y), (x+w-1, y+h-1), (0, 255, 0), 2)

            rect = cv2.minAreaRect(contours[idx])
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(textImg,[box],0,(0,0,255),2)

            #we can filter theta as outlier based on other theta values
            #this will help in excluding the rare text region with different orientation from ususla value 
            theta = slope(box[0][0], box[0][1], box[1][0], box[1][1])
            cummTheta.append(theta) 

    for i in cummTheta:
        i = int(i)
    
    unique, counts = np.unique(cummTheta, return_counts=True)
    most_frequent = unique[np.argmax(counts)]
    
    orientation = most_frequent
    img_cv2 = rotate(img, orientation)
    
    
    try:
        rbg = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        results = pytesseract.image_to_osd(rbg, output_type= Output.DICT)
        rotated = imutils.rotate_bound(img_cv2, results['rotate'])
        Image.fromarray(rotated).save(image_path)
    except:
        #Nguyên nhân đây là bức ảnh có ít chữ nên ko quan trọng
        Image.fromarray(img_cv2).save(image_path)

    # display(textImg, "Detectd Text minimum bounding box")
    # display(finalImage, "Deskewed Image")