import os
import json
import numpy as np
import copy
import cv2
import random
import pandas as pd
import re

from PIL import Image, ImageDraw,ImageFont
# pdir = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
# os.chdir(pdir)
import common_utils



def get_overlap_y(x1,y1,w1,h1,x2,y2,w2,h2):
    '''
    y轴方向重叠
    :param x1:
    :param y1:
    :param w1:
    :param h1:
    :param x2:
    :param y2:
    :param w2:
    :param h2:
    :return:
    '''
    y_min = max(y1, y2)
    y_max = min(y1 + h1, y2 + h2)
    y_dis = y_max - y_min
    flag = False
    if 2 * y_dis > h1 or 2 * y_dis > h2:
        flag = True
    return flag

def get_overlap_x(x1,y1,w1,h1,x2,y2,w2,h2):
    '''
     x轴方向重叠
    :param x1:
    :param y1:
    :param w1:
    :param h1:
    :param x2:
    :param y2:
    :param w2:
    :param h2:
    :return:
    '''
    x_min = max(x1, x2)
    x_max = min(x1 + w1, x2 + w2)
    x_dis = x_max - x_min
    flag = False
    if 2 * x_dis > w1 or 2 * x_dis > w2:
        flag = True
    return flag


def get_overlap_area(x1, y1, w1, h1, x2, y2, w2, h2):
    '''
    面积重叠
    :param x1:
    :param y1:
    :param w1:
    :param h1:
    :param x2:
    :param y2:
    :param w2:
    :param h2:
    :return:
    '''
    intersect_flag = True
    x1_1 = x1 + w1
    y1_1 = y1 + h1
    x2_2 = x2 + w2
    y2_2 = y2 + h2
    minx = max(x1, x2)
    miny = max(y1, y2)

    maxx = min(x1_1, x2_2)
    maxy = min(y1_1, y2_2)
    if minx > maxx or miny > maxy:
        intersect_flag = False

    intersect_area = 0
    if intersect_flag == True:
        intersect_area = (maxx - minx) * (maxy - miny)
    return intersect_area

def make_parse_filedir(save_path,one_levels,file1,file2,file3,pic_levels = None):
    '''
    解析文件夹
    :param save_path:
    :param one_levels:
    :param file1:
    :param file2:
    :param file3:
    :param pic_levels:
    :return:
    '''
    for one_level in one_levels:
        os.makedirs(os.path.join(save_path, one_level), exist_ok=True)
        os.makedirs(os.path.join(save_path, one_level,file1), exist_ok=True)
        os.makedirs(os.path.join(save_path, one_level, file1), exist_ok=True)
        os.makedirs(os.path.join(save_path, one_level, file1, file2), exist_ok=True)
        os.makedirs(os.path.join(save_path, one_level, file1, file2, file3), exist_ok=True)
    if pic_levels != None:
        for pic_level in pic_levels:
            os.makedirs(os.path.join(save_path, 'pic', pic_level), exist_ok=True)
            os.makedirs(os.path.join(save_path, 'pic', pic_level, file1), exist_ok=True)
            os.makedirs(os.path.join(save_path, 'pic', pic_level, file1, file2), exist_ok=True)
            os.makedirs(os.path.join(save_path, 'pic', pic_level, file1, file2, file3), exist_ok=True)

def make_parse_filedir_server(save_path,one_levels,pic_levels = None):
    '''
    解析文件夹
    :param save_path:
    :param one_levels:
    :param file1:
    :param file2:
    :param file3:
    :param pic_levels:
    :return:
    '''
    for one_level in one_levels:
        os.makedirs(os.path.join(save_path, one_level), exist_ok=True)

    if pic_levels != None:
        for pic_level in pic_levels:
            os.makedirs(os.path.join(save_path, 'pic', pic_level), exist_ok=True)

def draw_pic(pic_fill,pic_hollow,pic_text,pic_index,shape,name,cur_index,color_box):
    '''
    绘图
    :param pic_fill:
    :param pic_hollow:
    :param pic_text:
    :param pic_index:
    :param shape:
    :param name:
    :param cur_index:
    :param color_box:
    :return:
    '''
    x = int(float(shape['x'].replace('cm', '')) * 100) + 50
    y = int(float(shape['y'].replace('cm', '')) * 100) + 50
    w = int(float(shape['width'].replace('cm', '')) * 100)
    h = int(float(shape['height'].replace('cm', '')) * 100)
    pic_hollow = cv2.rectangle(pic_hollow, (x, y), (x + w, y + h), color_box, 10)
    pic_fill = cv2.fillConvexPoly(pic_fill, np.array([[(x, y), (x + w, y), (x + w, y + h), (x, y + h)]]),
                                  color_box)
    pic_text = cv2.rectangle(pic_text, (x, y), (x + w, y + h), color_box, 10)
    pic_index = cv2.rectangle(pic_index, (x, y), (x + w, y + h), color_box, 10)
    color = (0, 0, 0)
    pic_text = common_utils.paint_chinese_opencv(pic_text, name, (x, y), color)
    # color = (0, 255, 0)
    pic_index = common_utils.paint_chinese_opencv(pic_index, str(cur_index), (x, y), color_box)
    return pic_fill,pic_hollow,pic_text,pic_index

def deal_specail_name(name,one_all_names):
    '''
    处理特殊name
    :param name:
    :param one_all_names:
    :return:
    '''
    if name not in one_all_names:
        one_all_names.append(name)
    else:
        rand_num = random.randint(1, 10000)
        new_name = name + '_' + str(rand_num)
        name = new_name
    return name,one_all_names

def get_text_info_df(text_info_columns,info,info_key,cur_info_index,file_name,name):
    '''
    获取文本中每一条信息
    :param text_info_columns:
    :param info:
    :param info_key:
    :param cur_info_index:
    :param file_name:
    :param name:
    :return:
    '''
    one_text_info_dict = {}
    text_info_columns1 = [one for one in text_info_columns if one not in ['file_name','name','info_key']]
    for one_column in text_info_columns1:
        if one_column.replace('_','-') in info.keys():
            one_text_info_dict[one_column] = info[one_column.replace('_','-')]
        else:
            one_text_info_dict[one_column] = 'none'
    one_text_info_dict['file_name'] = file_name
    one_text_info_dict['name'] = name
    one_text_info_dict['info_key'] = info_key
    return pd.DataFrame(one_text_info_dict,index=[cur_info_index])

def get_overlap_features(texts,shapes):
    '''
     # 判断是否叠加的问题
    :param texts:
    :param shapes:
    :return:
    '''
    all_shapes_bak = []
    all_shapes = texts + shapes
    for one_index, one in enumerate(all_shapes):
        one_x = common_utils.deal_no_word(one['x'].replace('cm', ''))
        one_y = common_utils.deal_no_word(one['y'].replace('cm', ''))
        one_w = common_utils.deal_no_word(one['width'].replace('cm', ''))
        one_h = common_utils.deal_no_word(one['height'].replace('cm', ''))
        over_shape_flag = 0
        over_shape_num = 0
        over_shape_area = 0
        over_text_flag = 0
        over_text_num = 0
        over_text_area = 0
        for other_index, other in enumerate(all_shapes):
            other_x = common_utils.deal_no_word(other['x'].replace('cm', ''))
            other_y = common_utils.deal_no_word(other['y'].replace('cm', ''))
            other_w = common_utils.deal_no_word(other['width'].replace('cm', ''))
            other_h = common_utils.deal_no_word(other['height'].replace('cm', ''))
            other_subject = other['subject']
            if one_index == other_index:
                continue
            intersect_area = get_overlap_area(one_x, one_y, one_w, one_h, other_x, other_y, other_w, other_h)
            if intersect_area > 0:
                if other_subject == 'shape':
                    over_shape_num = over_shape_num + 1
                    over_shape_area = over_shape_area + intersect_area
                    over_shape_flag = 1
                elif other_subject == 'texts':
                    over_text_num = over_text_num + 1
                    over_text_area = over_text_area + intersect_area
                    over_text_flag = 1
        one_copy = copy.copy(one)
        one_copy['over_shape_num'] = over_shape_num
        one_copy['over_shape_area'] = over_shape_area
        one_copy['over_shape_flag'] = over_shape_flag
        one_copy['over_text_num'] = over_text_num
        one_copy['over_text_area'] = over_text_area
        one_copy['over_text_flag'] = over_text_flag
        all_shapes_bak.append(one_copy)
    return all_shapes_bak

def estimate_title(one_shape,ppt_width,ppt_height):
   '''
   判断是文本框位置是否符合title
   :param one_shape:
   :param ppt_width:
   :param ppt_height:
   :return:
   '''
   shape_y = common_utils.deal_no_word(one_shape['y'].replace('cm',''))
   shape_height = common_utils.deal_no_word(one_shape['height'].replace('cm',''))
   ppt_height = common_utils.deal_no_word(ppt_height.replace('cm',''))
   shape_subject = one_shape['subject']
   if shape_subject == 'texts' and shape_y + shape_height < ppt_height/5:
       return 1
   else:
       return 0

def get_type(x,type_unique):
    if x in type_unique:
        return x
    else:
        x = 'unknown'
    return x

def get_all_info_df(file_name,cur_index,one_shape,ppt_width,ppt_height,shape_num,text_num,type_unique):
    '''
    获取单个shape的所有原始及预处理信息
    :param cur_index:
    :param one_shape:
    :param ppt_width:
    :param ppt_height:
    :param shape_num:
    :param text_num:
    :param type_unique:
    :return:
    '''
    one_info = {}
    name = one_shape['name']
    one_info['name'] = name
    one_info['file_name'] = file_name
    one_info['key'] = one_shape['key']
    one_info['shape_num'] = shape_num
    one_info['text_num'] = text_num
    one_info['line'] = one_shape['line']
    one_info['over_shape_flag'] = one_shape['over_shape_flag']
    one_info['over_shape_num'] = one_shape['over_shape_num']
    one_info['over_shape_area'] = one_shape['over_shape_area']
    one_info['over_text_flag'] = one_shape['over_text_flag']
    one_info['over_text_num'] = one_shape['over_text_num']
    one_info['over_text_area'] = one_shape['over_text_area']

    one_info['class'] = one_shape['class'] if one_shape['class'] != '' else 'other'
    one_info['type'] = name.split(' ')[0] #这里的type是name去掉了后面的标注，比如 图片 16 -> 图片
    one_info['width'] = common_utils.deal_no_word(ppt_width.replace('cm', ''))
    one_info['height'] = common_utils.deal_no_word(ppt_height.replace('cm', ''))

    one_info['shape_height'] = common_utils.deal_no_word(one_shape['height'].replace('cm', ''))
    one_info['shape_width'] = common_utils.deal_no_word(one_shape['width'].replace('cm', ''))
    one_info['shape_x'] = common_utils.deal_no_word(one_shape['x'].replace('cm', ''))
    one_info['shape_y'] = common_utils.deal_no_word(one_shape['y'].replace('cm', ''))

    one_info['shape_area'] = one_info['shape_height'] * one_info['shape_width']

    one_info['estimate_title'] = estimate_title(one_shape,ppt_width,ppt_height)

    if one_info['shape_area'] == 0:
        one_info['over_shape_area_rate'] = 0.0
        one_info['over_text_area_rate'] = 0.0
    else:
        one_info['over_shape_area_rate'] = one_shape['over_shape_area'] * 1.0 /  one_info['shape_area']
        one_info['over_text_area_rate'] = one_shape['over_text_area'] * 1.0 /  one_info['shape_area']

    if one_info['shape_height'] == 0:
        one_info['slope'] = 0.0
    else:
        one_info['slope'] = one_info['shape_width'] / one_info['shape_height']

    # 暂时采用内容的第一行的属性作为该text的属性，具体每一行的属性见info表
    if 'Infos' in one_shape.keys():
        infos = one_shape['Infos']
        all_content = ''
        len_all_content = 0
        for info in infos:
            if 'content' in info.keys():
                content = info['content']
                if content != None and content != '':
                    all_content = all_content + content
                    len_content = get_content_len(info)
                    len_all_content = len_all_content + len_content

        if len(infos) > 0:
            one_info['language'] = infos[0]['language']
            one_info['font-size-asian'] = infos[0]['font-size-asian']
            one_info['font-name-asian'] = infos[0]['font-name-asian']
            one_info['font-weight'] = infos[0]['font-weight']
            one_info['font-name'] = infos[0]['font-name']
            one_info['font-style'] = infos[0]['font-style']
            one_info['font-size'] = infos[0]['font-size']
        else:
            one_info['language'] = 'none'
            one_info['font-size-asian'] = 'none'
            one_info['font-name-asian'] = 'none'
            one_info['font-weight'] = 'none'
            one_info['font-name'] = 'none'
            one_info['font-style'] = 'none'
            one_info['font-size'] = 'none'

    else:
        one_info['language'] = 'none'
        one_info['font-size-asian'] = 'none'
        one_info['font-name-asian'] = 'none'
        one_info['font-weight'] = 'none'
        one_info['font-name'] = 'none'
        one_info['font-style'] = 'none'
        one_info['font-size'] = 'none'
        all_content = ''
        len_all_content = 0

    one_info['content'] = all_content
    one_info['content_size'] = len_all_content
    one_info['subject'] = one_shape['subject']

    one_info['type_unique'] = get_type(one_info['type'],type_unique)



    return pd.DataFrame(one_info, index=[cur_index])



def get_content_len(info):
    if 'language' in info.keys():
        if info['language'] == 'en':
            zhmodel = re.compile(u'[\u4e00-\u9fa5]')
            res = zhmodel.search(info['content'])
            if res:
                return len(info['content'])
            else:
                return int(0.5*len(info['content']))
        else:
            return len(info['content'])
    else:
        return len(info['content'])

def parse_json_2_csv(raw_path,save_path,file1,file2,file3,file4,one_levels,text_info_columns,all_columns,pic_levels = None):
    '''
    解析json 到 csv，获取单页ppt的所有shape信息
    :param raw_path:
    :param save_path:
    :param file1:
    :param file2:
    :param file3:
    :param file4:
    :param one_levels:
    :param text_info_columns:
    :param all_columns:
    :param pic_levels:
    :return:
    '''
    text_info_df = pd.DataFrame(columns=text_info_columns)
    all_info_df = pd.DataFrame(columns=all_columns)

    file_name = os.path.join(file1,file2,file3,file4)
    file_name_2 = os.path.join(file2,file3,file4)
    json_path = os.path.join(raw_path, file_name)
    with open(json_path) as file:
        file_json = json.load(file)

    with open(os.path.join(save_path,'json',file1,file2,file3,file4),'w') as file11:
        file_json1 = json.dumps(file_json,ensure_ascii=False,indent=4)
        file11.write(file_json1)
    file11.close()
    # pic_flag为True，表示要存储图片
    pic_flag = False
    if 'pic' in one_levels:
        pic_flag = True

    pic_fill = None
    pic_hollow = None
    pic_text = None
    pic_index = None
    if pic_flag:
        pic_ppt_width = int(float(file_json['width'].replace('cm', '')) * 100) + 100
        pic_ppt_height = int(float(file_json['height'].replace('cm', '')) * 100) + 100
        white = np.ones((pic_ppt_height, pic_ppt_width, 3), np.uint8) * 255
        pic_fill = copy.copy(white)
        pic_hollow = copy.copy(white)
        pic_text = copy.copy(white)
        pic_index = copy.copy(white)


    #==================================================
    # shape 信息预处理 报告graphic,chart,普通的shape
    #==================================================
    shapes_1 = file_json['Shapes']
    shapes_2 = []
    one_all_shape_names = []
    shape_cur_index = 0
    if len(shapes_1) > 0:
        for shape in shapes_1:
            try:
                name = shape['name']
                shape['subject'] = 'shape'
                if name == '备注占位符 2':
                    continue
                if name == '':
                    name = '无'
                    continue
                name,one_all_shape_names = deal_specail_name(name,one_all_shape_names)
                shape['name'] = name
                shape['key'] = shape_cur_index
                shape['line'] = 0
                if pic_flag:
                    shape_color_box = (0, 255, 0)
                    pic_fill,pic_hollow,pic_text,pic_index = \
                        draw_pic(pic_fill, pic_hollow, pic_text, pic_index,
                                 shape, name, shape_cur_index, shape_color_box)
                shapes_2.append(shape)
                shape_cur_index = shape_cur_index + 1
            except:
                print('remove one shape')
                continue

    # ==================================================
    # text 信息预处理 包括table,text,等
    # ==================================================
    texts_1 = file_json['Texts']
    texts_2 = []
    one_all_text_names = []
    text_cur_index = 0
    if len(texts_1) > 0:
        for text in texts_1:
            try:
                name = text['name']
                if name == '':
                    name = '无'
                    continue
                name,one_all_shape_names = deal_specail_name(name,one_all_text_names)
                text['name'] = name
                cur_info_index = 0
                if 'Infos' in text.keys():
                    infos = text['Infos']
                    info_key = 0
                    all_content = ''
                    len_all_content = 0
                    line = len(infos)
                    for info in infos:
                        if 'content' in info.keys():
                            # 添加文本框的细节信息
                            text_info_df = text_info_df.append(get_text_info_df(text_info_columns, info, info_key, cur_info_index, file_name, name))
                            content = info['content']
                            if content != None and content != '' and content != 'e7d195523061f1c01d60fa9f1cfcbfb3d7dea265119d71e15FBB43640B43E9A75E03FE54C774D5D4779ED45933E78901D3CB0E69E39D04A9E1E9B25CF060C4BCA4D072860494D0D8E683C2FE58414E159AE804DD9B70DB041DC1ACA0EBCE4199549284F3A2910107F3F389C484B57BF3EDAE091BE0601339FCCAEACBADEB54867414D56E926B05F0':
                                all_content = all_content + content
                                len_content = get_content_len(info)
                                len_all_content = len_all_content + len_content
                    if all_content == '':
                        text['key'] = shape_cur_index
                        text['line'] = 0
                        text['subject'] = 'shape'
                        shapes_2.append(text)

                        if pic_flag:
                            shape_color_box = (0, 255, 0)
                            pic_fill, pic_hollow, pic_text, pic_index = \
                                draw_pic(pic_fill, pic_hollow, pic_text, pic_index,
                                         text, name, shape_cur_index, shape_color_box)
                        shape_cur_index = shape_cur_index + 1
                    else:
                        text['key'] = text_cur_index
                        text['line'] = line
                        text['subject'] = 'texts'
                        texts_2.append(text)

                        if pic_flag:
                            text_color_box = (0, 0, 255)
                            pic_fill, pic_hollow, pic_text, pic_index = \
                                draw_pic(pic_fill, pic_hollow, pic_text, pic_index,
                                         text, name, text_cur_index, text_color_box)
                        text_cur_index = text_cur_index + 1
                else:
                    text['key'] = shape_cur_index
                    text['line'] = 0
                    text['subject'] = 'shape'
                    shapes_2.append(text)

                    if pic_flag:
                        shape_color_box = (0, 255, 0)
                        pic_fill, pic_hollow, pic_text, pic_index = \
                            draw_pic(pic_fill, pic_hollow, pic_text, pic_index,
                                     text, name, shape_cur_index, shape_color_box)
                    shape_cur_index = shape_cur_index + 1
            except:
                print('remove one text')
                continue

    pic_dict = {}
    pic_dict['fill'] = pic_fill
    pic_dict['hollow'] = pic_hollow
    pic_dict['text'] = pic_text
    pic_dict['index'] = pic_index

    # ==================================================
    # 图片如果存储，那么直接存储
    # ==================================================
    if pic_flag:
        for pic_level in pic_levels:
            cv2.imwrite(os.path.join(save_path,'pic',pic_level, file1, file2, file3, file4 + '.png'), pic_dict[pic_level])

    # ==================================================
    # 判断框与框之间是否叠加
    # ==================================================

    all_shapes = get_overlap_features(texts_2,shapes_2)

    # ==================================================
    # 信息整理
    # ==================================================
    ppt_width = file_json['width']
    ppt_height = file_json['height']
    # type_unique为统计后的量
    type_unique = ['文本占位符', '内容占位符', '矩形', '文本框', '椭圆', 'TextBox', '燕尾形', '表格', 'Rectangle',
                   'Text', '任意多边形', 'nd_null_2783', 'nd_null_9337', 'nd_null_7143',
                   'nd_null_189', 'nd_null_4593', 'nd_null_9149', '五边形', '矩形标注', 'CustomText1',
                   'CustomText2',
                   'ValueText1', '备注占位符', '标题', '页脚占位符',
                   'nd_null_8998', 'nd_null_418', 'nd_null_826', 'nd_null_8755',
                   '副标题', 'nd_null_9543', 'nd_null_6418', '手动输入', 'AutoShape', '圆角矩形', '平行四边形',
                   '圆角矩形标注', 'Freeform', 'nd_null_9269', 'nd_null_378',
                   'nd_null_1754', 'nd_null_9246', 'nd_null_7016', 'nd_null_5693',
                   '椭圆形标注', '竖排文本占位符', '图片']



    for cur_index,one_shape in enumerate(all_shapes):

        all_info_df = \
            all_info_df.append(get_all_info_df(file_name_2,
                                               cur_index,
                                               one_shape,
                                               ppt_width,
                                               ppt_height,
                                               shape_cur_index,
                                               text_cur_index,
                                               type_unique))

    all_info_df['font_size_estimate_title'] = 0
    all_info_text_df = all_info_df[all_info_df['subject'] == 'texts']
    if len(all_info_text_df) >= 2:
        text_one_font_df = all_info_text_df.copy()
        text_one_font_df = text_one_font_df.sort_values(['font-size'], ascending=[False])
        text_one_font_df = text_one_font_df[~text_one_font_df.content.str.match('\d+')]
        if len(text_one_font_df) >= 2:
            first_text_one_font_size = float(text_one_font_df.iloc[0]['font-size'].replace('pt', ''))
            first_text_one_content_size = int(text_one_font_df.iloc[0]['content_size'])
            first_text_one_key = text_one_font_df.iloc[0]['key']
            second_text_one_font_size = float(text_one_font_df.iloc[1]['font-size'].replace('pt', ''))
            if first_text_one_font_size >= (3 / 2) * second_text_one_font_size and first_text_one_content_size <= 15:
                all_info_df.loc[(all_info_df['key'] == first_text_one_key) & (
                            all_info_df['subject'] == 'texts'), 'font_size_estimate_title'] = 1


    return all_info_df,text_info_df

def parse_json_2_csv_server(save_path,file4,file_json,one_levels,text_info_columns,all_columns,pic_levels = None):
    '''
    解析json 到 csv，获取单页ppt的所有shape信息
    :param raw_path:
    :param save_path:
    :param file1:
    :param file2:
    :param file3:
    :param file4:
    :param one_levels:
    :param text_info_columns:
    :param all_columns:
    :param pic_levels:
    :return:
    '''
    text_info_df = pd.DataFrame(columns=text_info_columns)
    all_info_df = pd.DataFrame(columns=all_columns)
    # 暂时统一叫这个名字
    file_name = os.path.join(save_path,file4)
    file_name_2 = os.path.join(save_path,file4)


    with open(os.path.join(save_path,'json',file4),'w') as file11:
        file_json1 = json.dumps(file_json,ensure_ascii=False,indent=4)
        file11.write(file_json1)
    file11.close()
    # pic_flag为True，表示要存储图片
    pic_flag = False
    if 'pic' in one_levels:
        pic_flag = True

    pic_fill = None
    pic_hollow = None
    pic_text = None
    pic_index = None
    if pic_flag:
        # print('==========\n',file_json)
        # print('==========\n',file_json['width'])
        # 
        # print('==========',np.round(float(file_json['width'].replace('cm', '')) * 100))
        pic_ppt_width = int(np.round(float(file_json['width'].replace('cm', '')) * 100)) + 100
        pic_ppt_height = int(np.round(float(file_json['height'].replace('cm', '')) * 100)) + 100
        white = np.ones((pic_ppt_height, pic_ppt_width, 3), np.uint8) * 255
        pic_fill = copy.copy(white)
        pic_hollow = copy.copy(white)
        pic_text = copy.copy(white)
        pic_index = copy.copy(white)


    #==================================================
    # shape 信息预处理 报告graphic,chart,普通的shape
    #==================================================
    shapes_1 = file_json['Shapes']
    shapes_2 = []
    one_all_shape_names = []
    shape_cur_index = 0
    if len(shapes_1) > 0:
        for shape in shapes_1:
            try:
                name = shape['name']
                shape['subject'] = 'shape'
                if name == '备注占位符 2':
                    continue
                if name == '':
                    name = '无'
                    continue
                name,one_all_shape_names = deal_specail_name(name,one_all_shape_names)
                shape['name'] = name
                shape['key'] = shape_cur_index
                shape['line'] = 0
                if pic_flag:
                    shape_color_box = (0, 255, 0)
                    pic_fill,pic_hollow,pic_text,pic_index = \
                        draw_pic(pic_fill, pic_hollow, pic_text, pic_index,
                                 shape, name, shape_cur_index, shape_color_box)
                shapes_2.append(shape)
                shape_cur_index = shape_cur_index + 1
            except:
                print('remove one shape')
                continue

    # ==================================================
    # text 信息预处理 包括table,text,等
    # ==================================================
    texts_1 = file_json['Texts']
    texts_2 = []
    one_all_text_names = []
    text_cur_index = 0
    if len(texts_1) > 0:
        for text in texts_1:
            try:
                name = text['name']
                if name == '':
                    name = '无'
                    continue
                name,one_all_shape_names = deal_specail_name(name,one_all_text_names)
                text['name'] = name
                cur_info_index = 0
                if 'Infos' in text.keys():
                    infos = text['Infos']
                    info_key = 0
                    all_content = ''
                    len_all_content = 0
                    line = len(infos)
                    for info in infos:
                        if 'content' in info.keys():
                            # 添加文本框的细节信息
                            text_info_df = text_info_df.append(get_text_info_df(text_info_columns, info, info_key, cur_info_index, file_name, name))
                            content = info['content']
                            if content != None and content != '' and content != 'e7d195523061f1c01d60fa9f1cfcbfb3d7dea265119d71e15FBB43640B43E9A75E03FE54C774D5D4779ED45933E78901D3CB0E69E39D04A9E1E9B25CF060C4BCA4D072860494D0D8E683C2FE58414E159AE804DD9B70DB041DC1ACA0EBCE4199549284F3A2910107F3F389C484B57BF3EDAE091BE0601339FCCAEACBADEB54867414D56E926B05F0':
                                all_content = all_content + content
                                len_content = get_content_len(info)
                                len_all_content = len_all_content + len_content
                    if all_content == '':
                        text['key'] = shape_cur_index
                        text['line'] = 0
                        text['subject'] = 'shape'
                        shapes_2.append(text)

                        if pic_flag:
                            shape_color_box = (0, 255, 0)
                            pic_fill, pic_hollow, pic_text, pic_index = \
                                draw_pic(pic_fill, pic_hollow, pic_text, pic_index,
                                         text, name, shape_cur_index, shape_color_box)
                        shape_cur_index = shape_cur_index + 1
                    else:
                        text['key'] = text_cur_index
                        text['line'] = line
                        text['subject'] = 'texts'
                        texts_2.append(text)

                        if pic_flag:
                            text_color_box = (0, 0, 255)
                            pic_fill, pic_hollow, pic_text, pic_index = \
                                draw_pic(pic_fill, pic_hollow, pic_text, pic_index,
                                         text, name, text_cur_index, text_color_box)
                        text_cur_index = text_cur_index + 1
                else:
                    text['key'] = shape_cur_index
                    text['line'] = 0
                    text['subject'] = 'shape'
                    shapes_2.append(text)

                    if pic_flag:
                        shape_color_box = (0, 255, 0)
                        pic_fill, pic_hollow, pic_text, pic_index = \
                            draw_pic(pic_fill, pic_hollow, pic_text, pic_index,
                                     text, name, shape_cur_index, shape_color_box)
                    shape_cur_index = shape_cur_index + 1
            except:
                print('remove one text')
                continue

    pic_dict = {}
    pic_dict['fill'] = pic_fill
    pic_dict['hollow'] = pic_hollow
    pic_dict['text'] = pic_text
    pic_dict['index'] = pic_index

    # ==================================================
    # 图片如果存储，那么直接存储
    # ==================================================
    if pic_flag:
        for pic_level in pic_levels:
            cv2.imwrite(os.path.join(save_path,'pic',pic_level, file4 + '.png'), pic_dict[pic_level])

    # ==================================================
    # 判断框与框之间是否叠加
    # ==================================================

    all_shapes = get_overlap_features(texts_2,shapes_2)

    # ==================================================
    # 信息整理
    # ==================================================
    ppt_width = file_json['width']
    ppt_height = file_json['height']
    # type_unique为统计后的量
    type_unique = ['文本占位符', '内容占位符', '矩形', '文本框', '椭圆', 'TextBox', '燕尾形', '表格', 'Rectangle',
                   'Text', '任意多边形', 'nd_null_2783', 'nd_null_9337', 'nd_null_7143',
                   'nd_null_189', 'nd_null_4593', 'nd_null_9149', '五边形', '矩形标注', 'CustomText1',
                   'CustomText2',
                   'ValueText1', '备注占位符', '标题', '页脚占位符',
                   'nd_null_8998', 'nd_null_418', 'nd_null_826', 'nd_null_8755',
                   '副标题', 'nd_null_9543', 'nd_null_6418', '手动输入', 'AutoShape', '圆角矩形', '平行四边形',
                   '圆角矩形标注', 'Freeform', 'nd_null_9269', 'nd_null_378',
                   'nd_null_1754', 'nd_null_9246', 'nd_null_7016', 'nd_null_5693',
                   '椭圆形标注', '竖排文本占位符', '图片']



    for cur_index,one_shape in enumerate(all_shapes):

        all_info_df = \
            all_info_df.append(get_all_info_df(file_name_2,
                                               cur_index,
                                               one_shape,
                                               ppt_width,
                                               ppt_height,
                                               shape_cur_index,
                                               text_cur_index,
                                               type_unique))

    all_info_df['font_size_estimate_title'] = 0
    all_info_text_df = all_info_df[all_info_df['subject'] == 'texts']
    if len(all_info_text_df) >= 2:
        text_one_font_df = all_info_text_df.copy()
        text_one_font_df = text_one_font_df.sort_values(['font-size'], ascending=[False])
        text_one_font_df = text_one_font_df[~text_one_font_df.content.str.match('\d+')]
        if len(text_one_font_df) >= 2:
            first_text_one_font_size = float(text_one_font_df.iloc[0]['font-size'].replace('pt', ''))
            first_text_one_content_size = int(text_one_font_df.iloc[0]['content_size'])
            first_text_one_key = text_one_font_df.iloc[0]['key']
            second_text_one_font_size = float(text_one_font_df.iloc[1]['font-size'].replace('pt', ''))
            if first_text_one_font_size >= (3 / 2) * second_text_one_font_size and first_text_one_content_size <= 15:
                all_info_df.loc[(all_info_df['key'] == first_text_one_key) & (
                            all_info_df['subject'] == 'texts'), 'font_size_estimate_title'] = 1


    return all_info_df,text_info_df


def parse_json_2_csv_simple(file_path,text_info_columns,all_columns):
    '''
    解析json 到 csv，获取单页ppt的所有shape信息，该函数不存图
    :param raw_path:
    :param save_path:
    :param file1:
    :param file2:
    :param file3:
    :param file4:
    :param one_levels:
    :param text_info_columns:
    :param all_columns:
    :param pic_levels:
    :return:
    '''
    text_info_df = pd.DataFrame(columns=text_info_columns)
    all_info_df = pd.DataFrame(columns=all_columns)

    file_name = '/'.join(file_path.split('/')[1:])
    file_name_2 = '/'.join(file_path.split('/')[2:])
    json_path = file_path
    with open(json_path) as file:
        file_json = json.load(file)

    with open(os.path.join(file_path),'w') as file11:
        file_json1 = json.dumps(file_json,ensure_ascii=False,indent=4)
        file11.write(file_json1)
    file11.close()

    pic_fill = None
    pic_hollow = None
    pic_text = None
    pic_index = None


    #==================================================
    # shape 信息预处理 报告graphic,chart,普通的shape
    #==================================================
    shapes_1 = file_json['Shapes']
    shapes_2 = []
    one_all_shape_names = []
    shape_cur_index = 0
    if len(shapes_1) > 0:
        for shape in shapes_1:
            try:
                name = shape['name']
                shape['subject'] = 'shape'
                if name == '备注占位符 2':
                    continue
                if name == '':
                    name = '无'
                    continue
                name,one_all_shape_names = deal_specail_name(name,one_all_shape_names)
                shape['name'] = name
                shape['key'] = shape_cur_index
                shape['line'] = 0
                shapes_2.append(shape)
                shape_cur_index = shape_cur_index + 1
            except:
                print('remove one shape')
                continue

    # ==================================================
    # text 信息预处理 包括table,text,等
    # ==================================================
    texts_1 = file_json['Texts']
    texts_2 = []
    one_all_text_names = []
    text_cur_index = 0
    if len(texts_1) > 0:
        for text in texts_1:
            try:
                name = text['name']
                if name == '':
                    name = '无'
                    continue
                name,one_all_shape_names = deal_specail_name(name,one_all_text_names)
                text['name'] = name
                cur_info_index = 0
                if 'Infos' in text.keys():
                    infos = text['Infos']
                    info_key = 0
                    all_content = ''
                    len_all_content = 0
                    line = len(infos)
                    for info in infos:
                        if 'content' in info.keys():
                            # 添加文本框的细节信息
                            text_info_df = text_info_df.append(get_text_info_df(text_info_columns, info, info_key, cur_info_index, file_name, name))
                            content = info['content']
                            if content != None and content != '':
                                all_content = all_content + content
                                len_content = get_content_len(info)
                                len_all_content = len_all_content + len_content
                    if all_content == '':
                        text['key'] = shape_cur_index
                        text['line'] = 0
                        text['subject'] = 'shape'
                        shapes_2.append(text)

                        shape_cur_index = shape_cur_index + 1
                    else:
                        text['key'] = text_cur_index
                        text['line'] = line
                        text['subject'] = 'texts'
                        texts_2.append(text)

                        text_cur_index = text_cur_index + 1
                else:
                    text['key'] = shape_cur_index
                    text['line'] = 0
                    text['subject'] = 'shape'
                    shapes_2.append(text)

                    shape_cur_index = shape_cur_index + 1
            except:
                print('remove one text')
                continue

    pic_dict = {}
    pic_dict['fill'] = pic_fill
    pic_dict['hollow'] = pic_hollow
    pic_dict['text'] = pic_text
    pic_dict['index'] = pic_index

    # ==================================================
    # 图片如果存储，那么直接存储
    # ==================================================
    # ==================================================
    # 判断框与框之间是否叠加
    # ==================================================

    all_shapes = get_overlap_features(texts_2,shapes_2)

    # ==================================================
    # 信息整理
    # ==================================================
    ppt_width = file_json['width']
    ppt_height = file_json['height']
    # type_unique为统计后的量
    type_unique = ['文本占位符', '内容占位符', '矩形', '文本框', '椭圆', 'TextBox', '燕尾形', '表格', 'Rectangle',
                   'Text', '任意多边形', 'nd_null_2783', 'nd_null_9337', 'nd_null_7143',
                   'nd_null_189', 'nd_null_4593', 'nd_null_9149', '五边形', '矩形标注', 'CustomText1',
                   'CustomText2',
                   'ValueText1', '备注占位符', '标题', '页脚占位符',
                   'nd_null_8998', 'nd_null_418', 'nd_null_826', 'nd_null_8755',
                   '副标题', 'nd_null_9543', 'nd_null_6418', '手动输入', 'AutoShape', '圆角矩形', '平行四边形',
                   '圆角矩形标注', 'Freeform', 'nd_null_9269', 'nd_null_378',
                   'nd_null_1754', 'nd_null_9246', 'nd_null_7016', 'nd_null_5693',
                   '椭圆形标注', '竖排文本占位符', '图片']

    for cur_index,one_shape in enumerate(all_shapes):

        all_info_df = \
            all_info_df.append(get_all_info_df(file_name_2,
                                               cur_index,
                                               one_shape,
                                               ppt_width,
                                               ppt_height,
                                               shape_cur_index,
                                               text_cur_index,
                                               type_unique))

    all_info_df['font_size_estimate_title'] = 0
    all_info_text_df = all_info_df[all_info_df['subject'] == 'texts']
    if len(all_info_text_df) >= 2:
        text_one_font_df = all_info_text_df.copy()
        text_one_font_df = text_one_font_df.sort_values(['font-size'], ascending=[False])
        text_one_font_df = text_one_font_df[~text_one_font_df.content.str.match('\d+')]
        if len(text_one_font_df) >= 2:
            first_text_one_font_size = float(text_one_font_df.iloc[0]['font-size'].replace('pt', ''))
            first_text_one_content_size = int(text_one_font_df.iloc[0]['content_size'])
            first_text_one_key = text_one_font_df.iloc[0]['key']
            second_text_one_font_size = float(text_one_font_df.iloc[1]['font-size'].replace('pt', ''))


            if first_text_one_font_size >= (3 / 2) * second_text_one_font_size and first_text_one_content_size <= 15:
                all_info_df.loc[(all_info_df['key'] == first_text_one_key) & (all_info_df['subject'] == 'texts'),'font_size_estimate_title'] = 1
    return all_info_df,text_info_df


def post_deal_with_content_itemize(all_info_df,text_info_df):
    # 获取大段文本框
    max_content_size_index = all_info_df['content_size'].argmax(axis=0)
    max_content_df = all_info_df.loc[max_content_size_index]
    all_info_df = all_info_df.drop(max_content_size_index)
    file_name = max_content_df['file_name']
    shape_x = max_content_df['shape_x']
    shape_y = max_content_df['shape_y']
    shape_width = max_content_df['shape_width']
    shape_height = max_content_df['shape_height']
    file_name = '/'.join(file_name.split('/')[1:])
    name = max_content_df['name']

    max_text_info_df = text_info_df[(text_info_df['file_name'].str.contains(file_name))
                                    & (text_info_df['name'] == name)]
    all_content_df = pd.DataFrame()
    for i in range(len(max_text_info_df)):
        one_max_text_info_df = max_text_info_df.iloc[i]
        one_max_text_info_content = one_max_text_info_df['content']
        if len(one_max_text_info_content) > 0 \
                and (re.match('^\d{1,2}[\\.|\\-|\\*|\\,|，｜、｜）｜)]',one_max_text_info_content)
                     or re.match('^[(|（]\d{1,2}[）｜)]',one_max_text_info_content)):
            one_content_df = copy.copy(max_content_df)
            one_content_df['content'] = one_max_text_info_content
            if one_max_text_info_df['language'] == 'en':
                zhmodel = re.compile(u'[\u4e00-\u9fa5]')
                res = zhmodel.search(one_max_text_info_content)
                if res:
                    one_content_df['content_size'] = len(one_max_text_info_content)
                else:
                    one_content_df['content_size'] = int(0.5*len(one_max_text_info_content))
            else:
                one_content_df['content_size'] = len(one_max_text_info_content)

            all_content_df = all_content_df.append(one_content_df,ignore_index=True)

    all_content_df_len = len(all_content_df)
    shape_height_bin = shape_height / all_content_df_len
    for i in range(all_content_df_len):
        all_content_df.loc[i,'shape_y'] = shape_y + i * shape_height_bin
        all_content_df.loc[i,'shape_height'] = shape_height_bin
        all_content_df.loc[i,'shape_area'] \
            = all_content_df.loc[i,'shape_width'] \
                                               * all_content_df.loc[i,'shape_height']
        all_content_df.loc[i,'shape_slope'] \
            = all_content_df.loc[i,'shape_width'] \
              / all_content_df.loc[i,'shape_height']
        all_content_df.loc[i,'name'] = all_content_df.loc[i,'name'] + '_' + str(i)
        all_content_df.loc[i,'key'] = str(all_content_df.loc[i,'key']) + '_' + str(i)

    all_info_df = all_info_df.append(all_content_df,ignore_index=True)
    all_info_df['text_num'] = len(all_info_df[all_info_df['subject'] == 'texts'])
    print('hello')
    return all_info_df

def post_deal_with_time_csv(all_info_df):
    '''
    # 处理包含时间的文本框
    :param all_info_df:
    :return:
    '''

    all_info_time_df = all_info_df[all_info_df.content.str.match(r'^\d{4}')]
    all_info_df['is_time'] = 0
    all_info_df['is_content'] = 0
    all_info_df['time_sequence'] = 0
    all_info_df['content_sequence'] = 0
    all_info_df['content_time'] = 0
    content_time_l = []
    for i in range(len(all_info_time_df)):
        all_info_df = all_info_df.drop(all_info_time_df.iloc[i].name)

    for i in range(len(all_info_time_df)):
        #iloc中i是顺序，loc中i是索引
        one_all_info_time_df = all_info_time_df.iloc[i]
        width = one_all_info_time_df['shape_width']
        height = one_all_info_time_df['shape_height']

        one_all_info_time_content = one_all_info_time_df['content']
        content_all = re.findall('^\d{4}',one_all_info_time_content)
        if len(content_all) > 0:

            content_time = content_all[0]
            content_time_l.append(int(content_time))
            one_all_info_time_time_df = copy.copy(one_all_info_time_df)
            one_all_info_time_time_df['shape_width'] = width / 3
            one_all_info_time_time_df['content'] = content_time
            one_all_info_time_time_df['key'] = one_all_info_time_time_df['key'] + 50
            one_all_info_time_time_df['name'] = one_all_info_time_time_df['name'] + '_50'

            one_all_info_time_time_df['content_size'] = len(content_time)
            one_all_info_time_time_df['is_time'] = 1
            one_all_info_time_time_df['is_content'] = 0
            one_all_info_time_time_df['content_time'] = int(content_time)
            one_all_info_time_time_df['shape_area'] = \
                one_all_info_time_time_df['shape_width'] * one_all_info_time_time_df['shape_height']
            one_all_info_time_time_df['slope'] = \
                one_all_info_time_time_df['shape_width'] / one_all_info_time_time_df['shape_height']






            one_all_info_time_content_df = copy.copy(one_all_info_time_df)
            one_all_info_time_content_df['content'] = re.sub('^\d{4}','',one_all_info_time_content)
            one_all_info_time_content_df['is_time'] = 0
            one_all_info_time_content_df['is_content'] = 1
            one_all_info_time_content_df['content_time'] = int(content_time)

            all_info_df = all_info_df.append(one_all_info_time_time_df, ignore_index=True)
            all_info_df = all_info_df.append(one_all_info_time_content_df, ignore_index=True)

        else:
            print('wrong')

    content_time_l.sort()
    all_info_df['time_sequence'] = all_info_df['content_time'].apply(lambda x:0 if int(x) not in content_time_l else content_time_l.index(x)+1)
    all_info_df['content_sequence'] = all_info_df['content_time'].apply(lambda x:0 if int(x) not in content_time_l else content_time_l.index(x)+1)
    text_num = len(all_info_df[all_info_df['subject'] == 'texts'])
    all_info_df['text_num'] = text_num


    if len(all_info_time_df) == len(all_info_df[all_info_df['is_time'] == 1]):
        all_info_df['time_break'] = 1
    else:
        all_info_df['time_break'] = 0

    print('hello')

    return all_info_df


def post_deal_with_title_separation(all_info_df, text_info_df):
    def _content_size(content):
        zhmodel = re.compile(u'[\u4e00-\u9fa5]')
        res = zhmodel.search(content)
        if res:
            return len(content)
        else:
            return int(0.5 * len(content))

    def _content_len_bool(pre, next):
        """
        依照两个长度来判断是否是标题
        :param pre: 上一个框的内容的长度
        :param next: 下一个框的内容的长度
        :return: pre是否是标题
        """
        # print("pre_conten_long:", pre)
        # print("next_conten_long:", next)
        if 0 in [pre, next]:
            return True
        else:
            if pre / max(pre, next) <= 0.5 or next / max(pre, next) <= 0.5:
                return True
            else:
                return False

    # 思路一：提取同框的
    # text_box = {}
    new_all_info_df = all_info_df.copy()
    new_text_info_df = text_info_df.copy()
    new_all_info_df.drop(new_all_info_df.index, inplace=True)
    for box_name in text_info_df["name"].drop_duplicates():  # 提取处在同框的文字，处理text_info_df

        name_grouped = text_info_df.loc[(text_info_df['name'] == box_name)]

        #lsh修改20200714,
        name_grouped.loc[:,'seq'] = range(len(name_grouped))
        # name_grouped = name_grouped.reset_index(drop=True)

        # 要判断字体大小和长度，然后把name更改
        font_size_grouped = name_grouped['font_size']
        content_grouped = name_grouped['content']

        if len(name_grouped['font_size']) == 1:  # 只有一个文本框，无需分离
            continue
        for box_index in range(1, len(name_grouped)):
            if box_index > 1:
                separation_box_name = name_grouped['name'].iloc[box_index] + '_' + str(box_index)
                # name_grouped['name'].iloc[box_index] = separation_box_name
                # 下面是lsh修改的版本20200714
                name_grouped.loc[name_grouped['seq'] == box_index,'name'] = separation_box_name

                continue
            if abs(int(font_size_grouped.iloc[box_index].replace('pt', '')) - int(
                    font_size_grouped.iloc[box_index - 1].replace('pt', ''))) >= 1 or \
                    _content_len_bool(_content_size(content_grouped.iloc[box_index]),
                                      _content_size(content_grouped.iloc[box_index - 1])):
                separation_box_name = name_grouped['name'].iloc[box_index] + '_' + str(box_index)
                # name_grouped['name'].iloc[box_index] = separation_box_name
                # 下面是lsh修改的版本20200714
                name_grouped.loc[name_grouped['seq'] == box_index,'name'] = separation_box_name

                # name_grouped.loc[name_grouped.index[box_index],'name'] = separation_box_name
                # name_grouped['name'].iloc[box_index] = separation_box_name

        new_text_info_df.loc[(text_info_df['name'] == box_name), 'name'] = name_grouped['name']

        # box_name = '文本框9',new_text_info_df 有框区别,以及对应的content
    content_combine = ''
    pair_flag = 0  # 是否有pair
    one_box_count = 0  # 判断是属于某个文本框
    box_pair_num = 0  # 如'文本框9','文本框9_0','文本框9_1'，则该变量为2,除了标题以外
    for index, new_box_name in enumerate(new_text_info_df['name']):  # '文本框9','文本框9_0','文本框9_1',‘文本框10’，‘文本框10_0'
        main_name = new_box_name.split('_')[0]  # '文本框9'
        if '文本框' not in new_box_name: # 可能名字本身就带有"_",针对只有文本框的进行直接加入
            temp_pd = all_info_df.loc[all_info_df['name'] == new_box_name]
            temp_pd['pair'] = 'no'
            new_all_info_df = new_all_info_df.append(temp_pd, ignore_index=True)
            continue
        if new_box_name == main_name:  # 如果等于main_name 的文本框，则pair 设置为key_0
            temp_pd = all_info_df.loc[all_info_df['name'] == main_name]  # info中的'文本框 9‘
            temp_pd.loc[:,'name'] = main_name

            main_name_num = list(filter(lambda x: re.match('%s_' % main_name, x) is not None,
                                        new_text_info_df['name'].tolist()))
            # print('main_name_num:', main_name_num)

            box_pair_num = len(main_name_num)
            if box_pair_num >= 1:
                pair_flag = 1
                temp_pd.loc[:,'key'] = str(temp_pd['key'].iloc[0]) + '_0'
                temp_pd.loc[:,'pair'] = str(temp_pd['key'].iloc[0])
                temp_pd.loc[:,'line'] = 1
            else:
                pair_flag = 0
                temp_pd.loc[:,'pair'] = 'no'
            temp_group = new_text_info_df.loc[new_text_info_df['name'] == main_name]
            temp_pd.reset_index(drop=True,inplace=True)  # 否则index 不匹配出现错误
            temp_group.reset_index(drop=True,inplace=True)
            temp_pd.loc[:,'content'] = temp_group['content']
            temp_pd.loc[:,'content_size'] = _content_size(temp_pd['content'].iloc[0])
            if pair_flag:
                temp_pd.loc[:,'shape_height'] = temp_pd['shape_height'] / 3
                temp_pd.loc[:,'shape_width'] = temp_pd['shape_width'] / 2
                temp_pd.loc[:,'shape_area'] = \
                    temp_pd['shape_width'] * temp_pd['shape_height']
                temp_pd.loc[:,'slope'] = \
                    temp_pd['shape_width'] / temp_pd['shape_height']

            new_all_info_df = new_all_info_df.append(temp_pd, ignore_index=True)
        elif pair_flag and main_name == new_text_info_df['name'].iloc[index - 1].split('_')[0]:
            temp_group = new_text_info_df.loc[new_text_info_df['name'] == new_box_name]
            content_combine += temp_group['content']  # 累积content
            one_box_count += 1
        if pair_flag and one_box_count == box_pair_num:  # 累积完成，添加
            temp_pd = all_info_df.loc[all_info_df['name'] == main_name]  # temp_pd 是“文本框9”这样的一行，相当于标题的一行
            temp_pd_copy = temp_pd.copy()
            temp_pd.loc[:,'name'] = main_name + '_1'
            temp_pd.loc[:,'key'] = str(temp_pd['key'].iloc[0]) + '_1'
            temp_pd.loc[:,'pair'] = str(temp_pd['key'].iloc[0])
            temp_group = new_text_info_df.loc[
                new_text_info_df['name'] == new_box_name]  # temp_pd 是“文本框9_1”这样的一行，相当于内容的一行
            temp_pd.reset_index(drop=True,inplace=True)
            temp_pd.loc[:,'content'] = content_combine
            temp_pd.loc[:,'font-size'] = temp_group['font_size']
            temp_pd.loc[:,'line'] = 1
            temp_pd.loc[:,'font-size-asian'] = temp_group['font_size_asian']
            temp_pd.loc[:,'language'] = temp_group['language']
            temp_pd.loc[:,'content_size'] = _content_size(temp_pd['content'].iloc[0])
            temp_pd.loc[:,'shape_height'] = temp_pd['shape_height'] / 3 * 2
            temp_pd.loc[:,'shape_y'] = temp_pd['shape_y'] + temp_pd['shape_height'] / 3 * 2
            temp_pd.loc[:,'shape_area'] = \
                temp_pd['shape_width'] * temp_pd['shape_height']
            temp_pd.loc[:,'slope'] = \
                temp_pd['shape_width'] / temp_pd['shape_height']
            new_all_info_df = new_all_info_df.append(temp_pd, ignore_index=True)

            if temp_pd_copy['font-size'].iloc[0] == temp_pd['font-size'].iloc[0]:  # 如果标题和内容字体一样

                font_temp_pd = new_all_info_df.loc[new_all_info_df['name'] == main_name, 'font-size']
                font_temp_pd.iloc[0] = str(
                    int(temp_pd['font-size'].iloc[0].replace('pt', '')) + 1) + 'pt'  # 如果标题和内容字体一样，标题字体＋1
                new_all_info_df.loc[new_all_info_df['name'] == main_name, 'font-size'] = font_temp_pd

                font_temp_pd = new_all_info_df.loc[new_all_info_df['name'] == main_name, 'font-size-asian']
                font_temp_pd.iloc[0] = str(int(temp_pd['font-size-asian'].iloc[0].replace('pt', '')) + 1) + 'pt'
                new_all_info_df.loc[new_all_info_df['name'] == main_name, 'font-size-asian'] = font_temp_pd

            content_combine = ''
            one_box_count = 0
    img_df = all_info_df.loc[all_info_df['subject'] != 'texts']
    if len(img_df) > 0:
        img_df.loc[:,'pair'] = 'no'
        new_all_info_df = pd.concat([new_all_info_df,img_df])

    new_all_info_df.reset_index(drop=True,inplace=True)
    subject_count_list = new_all_info_df['subject'].tolist()
    for subject_type in set(subject_count_list):
        if subject_type == 'texts':
            new_all_info_df.loc[new_all_info_df['subject'] == subject_type,'text_num'] = subject_count_list.count(subject_type)


    return new_all_info_df, new_text_info_df
