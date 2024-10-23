def create():

    table_rec_model_dic = {
        'english': 'Model\Table_recognition\en_ppstructure_mobile_v2.0_SLANet_infer\en_ppstructure_mobile_v2.0_SLANet_infer',
        'chinese': "Model\Table_recognition\ch_ppstructure_mobile_v2.0_SLANet_infer\ch_ppstructure_mobile_v2.0_SLANet_infer",
        'japanese': "Model\Table_recognition\ch_ppstructure_mobile_v2.0_SLANet_infer\ch_ppstructure_mobile_v2.0_SLANet_infer",
        'korean': "Model\Table_recognition\ch_ppstructure_mobile_v2.0_SLANet_infer\ch_ppstructure_mobile_v2.0_SLANet_infer",
        'arabic': "Model\Table_recognition\ch_ppstructure_mobile_v2.0_SLANet_infer\ch_ppstructure_mobile_v2.0_SLANet_infer",
        'vietnamese': 'Model\Table_recognition\en_ppstructure_mobile_v2.0_SLANet_infer\en_ppstructure_mobile_v2.0_SLANet_infer',
    }
        
    table_char_dict = {
        'english': r'ppocr\utils\dict\table_structure_dict.txt',
        'vietnamese': r'ppocr\utils\dict\table_structure_dict.txt',
        'chinese': r"ppocr/utils/dict/table_structure_dict_ch.txt",
        'japanese': r"ppocr/utils/dict/table_structure_dict_ch.txt",
        'korean': r"ppocr/utils/dict/table_structure_dict_ch.txt",
        'arabic': r"ppocr/utils/dict/table_structure_dict_ch.txt",
    }

    text_det_model = {
        'english': 'Model\Text_detection\en_PP-OCRv3_det_infer\en_PP-OCRv3_det_infer',
        'chinese': "Model\Text_detection\ch_PP-OCRv3_det_infer\ch_PP-OCRv3_det_infer",
        'japanese': "Model\Text_detection\Multilingual_PP-OCRv3_det_infer\Multilingual_PP-OCRv3_det_infer",
        'korean': "Model\Text_detection\Multilingual_PP-OCRv3_det_infer\Multilingual_PP-OCRv3_det_infer",
        'arabic': "Model\Text_detection\Multilingual_PP-OCRv3_det_infer\Multilingual_PP-OCRv3_det_infer",
    }

    text_rec_model = {
        'english': 'Model\Text_recognition\en_PP-OCRv3_rec_infer\en_PP-OCRv3_rec_infer',
        'chinese': "Model\Text_recognition\ch_PP-OCRv3_rec_infer\ch_PP-OCRv3_rec_infer",
        'japanese': "Model\Text_recognition\japan_PP-OCRv3_rec_infer\japan_PP-OCRv3_rec_infer",
        'korean': "Model\Text_recognition\korean_PP-OCRv3_rec_infer\korean_PP-OCRv3_rec_infer",
        'arabic': "Model\Text_recognition\\arabic_PP-OCRv3_rec_infer\\arabic_PP-OCRv3_rec_infer",
    }

    rec_char_dict = {
        'english': 'ppocr/utils/en_dict.txt',
        'chinese': "ppocr/utils/ppocr_keys_v1.txt",
        'japanese': "ppocr/utils/dict/japan_dict.txt",
        'korean': "ppocr/utils/dict/korean_dict.txt",
        'arabic': "ppocr/utils/dict/arabic_dict.txt",
    }
    return table_rec_model_dic,table_char_dict,text_det_model,text_rec_model,rec_char_dict