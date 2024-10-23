# Công cụ OCR
Dự án này được phát triển dựa trên [PP-OCR](https://github.com/PaddlePaddle/PaddleOCR) của PaddlePaddle. Và sử dụng model Vgg Seq2seq của [VietOCR](https://github.com/pbcquoc/vietocr) của pbcquoc.

Dự án có chỉnh sửa source code của PP-OCR để có thể kết hợp thêm mô hình VietOCR vào trong Pipeline của PP-OCR. Bên cạnh đó kết hợp thêm OpenCV để có thể xoay ảnh được về đúng vị trí văn bản trong trường hợp ảnh bị xoay. 
File code sử dụng OpenCV để xoay ảnh trong project là file [rotate_image.py](https://github.com/PhanHung7/OCR-Tool/blob/main/rotate_image.py) mặc dù độ chính xác chưa được 100% nhưng cũng lớn hơn 90% khi xoay ảnh. 
Vì còn đang nghiên cứu nên vẫn sẽ bị lỗi xảy ra khi xoay ảnh nhưng đã được tạm thời bỏ qua khi chạy code trong dự án.

# Cài đặt
Vì trong dự án này mình sử dụng bản cũ của PP-OCR và có sự can thiệp vào soucre code của PP-OCR nên phải clone git về mới có thể chạy local. Để có thể cài đặt dự án và chạy local thì hãy chạy lệnh. 

```python
!git clone https://github.com/PhanHung7/OCR-Tool
```

Dưới đây là một số thư viện cần thiết để chạy chương trình kèm theo cách cài đặt.

```python
!pip install spire.doc
!pip install fastapi
!pip install uvicorn
!pip install os
!pip install pandas
!pip install zipfile
!pip install vietocr
!pip install numpy
!pip install pytorch
!pip install tqdm
!pip install imutils
!pip install cv2
!pip install pytesseract
!pip install pdf2image
```

Để chạy công cụ OCR hãy vào file main.py để có thể chạy vì project này sử dụng FastAPI để có thể deploy công cụ OCR.
# Kết quả
Mình đã chạy thử với một vài file trong dự án và kết quả được lưu lại ở trong các folder output_file_(số) các bạn có thể tham khảo.

# Giấy Phép
Dự án này sử dụng giấy phép Apache License 2.0. Xem chi tiết trong file [LICENSE](./LICENSE).