from paddleocr import PaddleOCR, PPStructure, draw_ocr, draw_structure_result, save_structure_res
from ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx
from imutils.object_detection import non_max_suppression
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from PIL import Image
import imutils
import pytesseract
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import rotate_image, Path_model
from tqdm import tqdm
# Dòng dưới tránh bị xảy ra lỗi : Initializing libiomp5md.dll, but found libiomp5md.dll already initialized. \
# Gây ra chết kernel
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

#Hàm đọc file pdf và lưu lại ảnh đã xoay
def Save_Image(path, count):
    list_images = convert_from_path(path)
    output_dir = f'image_folder_{count}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Lưu các hình ảnh từ list_image vào thư mục đã tạo
    for i, img in enumerate(list_images):
        image_path = os.path.join(output_dir, f'image_{i}.jpg')
        img.save(image_path)
    return output_dir

def take_text(boxes,img):
    """Hàm lấy từng bbox trong text để tiến hành recognition lại"""
    box_images = []
    for text in boxes:
        bboxes = text['text_region']
        a,b,c,d = bboxes
        #Nguyên nhân cần phải cộng thêm 1 ít vì cách bbox có thể thiếu 1 ít,
        #để dẫn tới kết quả đúng nên cộng thêm 1 ít sẽ dẫn tới độ chính xác cao hơn
        y_start = int(a[1])
        y_end=int(c[1])
        x_start=int(a[0])
        x_end =int(c[0])
        roi = img[y_start:y_end, x_start:x_end]
        box_images.append(roi)
    return box_images

def sort_file_img(lis):
    """
    Hàm dùng để sắp xếp lại tên của các file ảnh
    phục vụ mục đích tìm bảng chính trong báo cáo tài chính
    """
    tmp  = []
    for i in range(len(lis)):
        tmp.append((int(lis[i].split('_')[1].split('.')[0]), lis[i]))
    tmp.sort(key = lambda x: x[0])
    sorted_lis = []
    for i in tmp:
        sorted_lis.append(i[1])
    return sorted_lis

def run_model_and_recovery(folder_path, lang:str, model, count):
    lis_img_error = []
    
    table_rec_model_dic,table_char_dict,text_det_model,text_rec_model,rec_char_dict = Path_model.create()

    if lang == 'vietnamese':
        config = Cfg.load_config_from_file(r"D:\\OCR\\OCR\\vietocr\\base.yml")
        config['cnn']['pretrained']=False
        config['device'] = 'cpu'
        detector = Predictor(config)
    
        table_engine = PPStructure(show_log = False, table_model_dir =table_rec_model_dic[lang], \
                                    table_char_dict_path = table_char_dict[lang], \
                                    vietocr = True)
    else:
        table_engine = PPStructure(show_log = False, table_model_dir =table_rec_model_dic[lang],\
                                    rec_char_dict_path = rec_char_dict[lang],\
                                    rec_model_dir= text_rec_model[lang],\
                                    det_model_dir= text_det_model[lang],\
                                    table_char_dict_path = table_char_dict[lang])
    sorted_file_name = sort_file_img(os.listdir(folder_path))
    
    for i in tqdm(range(0,len(sorted_file_name))):
        try:
            img_path = os.path.join(folder_path, sorted_file_name[i])
            img = cv2.imread(img_path)
            result = table_engine(img, return_ocr_result_in_table= True)
                
            save_folder = f'image_structure_save_{count}'
            if lang == 'vietnamese':
                for j in result:
                    text = []
                    if j['type'] == 'table':
                        """Continue vi đoạn code này đã được trực tiếp sửa trong thư viện paddleocr file predict_system.py"""
                        continue
                    else:
                            box = take_text(j['res'], cv2.imread(img_path))
                            for img in box:
                                try:
                                    text.append(detector.predict(Image.fromarray(img)))
                                except ZeroDivisionError:
                                    text.append('')
                            for k in range(len(j['res'])):
                                j['res'][k]['text'] = text[k]
                    
            save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])

            
            h, w, _ = img.shape
            res = sorted_layout_boxes(result, w)
            convert_info_docx(img, res, save_folder, os.path.basename(img_path).split('.')[0])
        except:
            lis_img_error.append(i+1)
            print("Bị lỗi ko thể xuất file thành excel, word ra word được")
    count+=1
    print(f"Đã OCR và xuất ra file excel, docx thành công và có {len(lis_img_error)} trang bị lỗi")
    return lis_img_error, save_folder

def OCR(file_path, model, lang:str , pdf: bool, count: int):
    if pdf:
        file_path = Save_Image(file_path,count)
    for img_path in os.listdir(file_path):
        try:
            rotate_image.Cv2_rotate(os.path.join(file_path, img_path))
        except:
            #Có thể một số ảnh trống và ko có gì nên sẽ skip
            continue
    return run_model_and_recovery(file_path, lang, model, count)