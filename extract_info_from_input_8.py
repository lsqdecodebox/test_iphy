#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @Author : jliangqiu
# @Time : 2020/6/8
# @File : extract_info_from_input.py
import os
import json
import glob
import re
import chardet
import pandas as pd
# from utils.parse_utils import parse_json_2_csv


def get_label_map(map_path):
    with open(map_path, 'r', encoding='utf-8') as j_f:
        ss = [fr.strip() for fr in j_f.readlines()]
        ss_str = "".join(ss)
        label_map = json.loads(ss_str)
    return label_map


def get_center_xy(boxes_list):
    return [[b[0] + 0.5 * b[2], b[1] + 0.5 * b[3]] for b in boxes_list]


def get_cxy(b):
    return [b[0] + 0.5 * b[2], b[1] + 0.5 * b[3]]


def extract_text_info(text_info):
    # extract text info:
    t_area, tstr_len, tclass, tname, t_info, t_box = [], [], [], [], [], []
    for t_i in text_info:

        x, y = t_i["x"].replace("cm", ""), t_i["y"].replace("cm", "")
        w, h = t_i["width"].replace("cm", ""), t_i["height"].replace("cm", "")
        x = 0 if len(x) == 0 else max(float(x), 0)
        y = 0 if len(y) == 0 else max(float(y), 0)
        w = 0 if len(w) == 0 else max(float(w), 0)
        h = 0 if len(h) == 0 else max(float(h), 0)
        areas = w * h
        tclass.append(t_i["class"])
        tname.append(t_i["name"].split(" ")[0])
        if len(t_i["Infos"]) > 0:
            infos = t_i["Infos"][0]
            t_info.append(infos)
            if infos["content"] is not None:
                tstr_len.append(len(infos["content"]) * float(infos["font-size"].replace("pt", "")))
            else:
                tstr_len.append(0)
        else:
            t_info.append(None)
            tstr_len.append(0)

        t_area.append(areas)
        t_box.append([x, y, w, h])
    return [t_area, tclass, tname, t_box, tstr_len, t_info]


def extract_tuwen_info(shape_info):
    # extract tuwen info:
    # extract tuwen num:    "/": 0, "1图": 1, "2图": 2, "3图": 3, "多图": 4, "4图": 5
    # extract tuwen lyout:  "/": 0, "小图留白": 1, "横向图区": 2, "竖向图区": 3, "大图片": 4, "多图拼接": 5, "图文均分": 6,"横向": 7, "竖向": 8
    s_area, sclass, sname, s_box = [], [], [], []
    for s_i in shape_info:
        x, y = s_i["x"].replace("cm", ""), s_i["y"].replace("cm", "")
        w, h = s_i["width"].replace("cm", ""), s_i["height"].replace("cm", "")
        x = 0 if len(x) == 0 else max(float(x), 0)
        y = 0 if len(y) == 0 else max(float(y), 0)
        w = 0 if len(w) == 0 else max(float(w), 0)
        h = 0 if len(h) == 0 else max(float(h), 0)
        areas = w * h
        sclass.append(s_i["class"])
        sname.append(s_i["name"].split(" ")[0])
        s_area.append(areas)
        s_box.append([x, y, w, h])
    return [s_area, sclass, sname, s_box]


def compare_position(center1, center2):
    x_dist, y_dist = abs(center1[0] - center2[0]), abs(center1[1] - center2[1])
    if x_dist > y_dist:
        return True
    else:
        return False


def is_triangle(p1, p2, p3):
    x1, y1, x2, y2, x3, y3 = p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]
    return ((x1 - x2) * (y3 - y2) - (x3 - x2) * (y1 - y2)) != 0


def remove_duplicate(in_list):
    out_list = []
    for i_l in in_list:
        if i_l in out_list:
            continue
        else:
            out_list.append(i_l)
    return out_list


def rules_info(ppt_area, t_len, s_len, t_list, s_list):
    t_area, tclass, tname, t_box, tstr_len, t_info = t_list
    s_area, sclass, sname, s_box = s_list
    # rules
    text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num = [0], [0], [0], [0], [0]
    t_num = t_len
    if t_len == 0 and s_len == 0:
        return text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num
    # extract text type:    "/": 0, "分条列举": 1,"关键词句": 2,"大段文本": 3
    elif ("GraphicObjectShape" not in sclass or s_len == 0) and "GraphicObjectShape" not in tclass:
        if t_len == 1:
            if t_area[0] / ppt_area > 0.4:
                if len(t_info) == 1:
                    if not t_info[0] is None:
                        s_tinfo = t_info[0]["content"]
                        if not s_tinfo is None:
                            if s_tinfo.find("1") != -1 and s_tinfo.find("2") != -1:
                                text_type = [1, 3]
                else:
                    for t_i in t_info:
                        if t_i is None:
                            continue
                        if t_i["content"] is None:
                            break
                        if not bool(re.search('[0-9]', t_i["content"])):
                            break
                        text_type = [1, 3]
                if 3 not in text_type:
                    text_type = [3]
            else:
                text_type = [2]
        else:
            if t_len == 2:
                if t_area[0] > t_area[1]:
                    min_a, max_a = t_area[1], t_area[0]
                else:
                    min_a, max_a = t_area[0], t_area[1]
                if max_a / min_a > 10 and max_a / ppt_area > 0.4:
                    text_type = [3]
                else:
                    if t_info[0] is not None and t_info[1] is not None:
                        if abs(len(t_info[0]["content"]) - len(t_info[1]["content"])) < 3 and 0 < len(
                                t_info[0]["content"]) < 8:
                            text_type = [2]
                    if 0 in text_type:
                        text_type = []
                    if min_a / max_a > 0.8:
                        text_type.extend([1])
                    else:
                        text_type.extend([2])
            if 0 in text_type:
                if "TitleTextShape" in tclass and t_len % 2 == 0:
                    text_type = [2, 1]
                else:
                    text_type = [1, 2]
        text_type = remove_duplicate(text_type)
    else:
        # tuwen num: "/": 0, "1图": 1, "2图": 2, "3图": 3, "多图": 4, "4图": 5
        g_num = 0
        if "GraphicObjectShape" in tclass:
            g_num += tclass.count("GraphicObjectShape")
            t_num -= tclass.count("GraphicObjectShape")
        if "GraphicObjectShape" in sclass:
            g_num += sclass.count("GraphicObjectShape")
        if g_num == 4:
            tuwen_num = [5]
        else:
            tuwen_num = [min(g_num, 4)]
        tuwen_lyout = []
        # extract tuwen lyout:  "小图留白": 1, "大图片": 4, "多图拼接": 5, "横向": 7, "竖向": 8
        if t_num == 0:
            if g_num == 1:
                if s_area[0] / (ppt_area + 0.0001) > 0.5:
                    tuwen_lyout.append(4)
                else:
                    tuwen_lyout.append(1)
            else:
                s_center = get_center_xy(s_box)
                tuwen_lyout.extend([7] if compare_position(s_center[0], s_center[1]) else [8])
        else:
            # extract tuwen lyout:  "横向图区": 2, "竖向图区": 3, "图文均分": 6,"
            nmax = max(t_num, g_num)
            nmin = min(t_num, g_num)
            if nmax % nmin <= 1 and nmin > 1:
                tuwen_lyout.append(6)
            if t_num == 1 and g_num == 1:
                if s_area[0] / t_area[0] > 2:
                    tuwen_lyout.append(4)
                else:
                    p_center = get_center_xy(t_box)[0]
                    n_center = get_center_xy(s_box)[0]
                    tuwen_lyout.extend([3, 1] if compare_position(p_center, n_center) else [2, 1])
            else:
                if g_num == 1:
                    if s_area[0] / (ppt_area + 0.0001) > 0.5:
                        tuwen_lyout.append(4)
                if 4 not in tuwen_lyout:
                    t_center = get_center_xy(t_box)
                    s_center = get_center_xy(s_box)
                    tx_sum, ty_sum = 0, 0
                    for t_c in t_center:
                        tx_sum += t_c[0]
                        ty_sum += t_c[1]
                    tx_sum, ty_sum = tx_sum / t_len, ty_sum / t_len
                    sx_sum, sy_sum = 0, 0
                    for s_c in s_center:
                        sx_sum += s_c[0]
                        sy_sum += s_c[1]
                    sx_sum, sy_sum = sx_sum / s_len, sy_sum / s_len
                    tuwen_lyout.extend([3] if compare_position([tx_sum, ty_sum], [sx_sum, sy_sum]) else [2])
        if g_num > 2:
            tuwen_lyout.append(5)
    rgpaph_nmap = {"2": 4, "3": 2, "4": 1, "5": 5, "6": 3, "7": 6}
    # "rgraph_type": "/": 0, "并列": 1, "流程": 2, "循环": 3, "时间轴": 4, "总分": 5, "对比": 6, "金字塔": 7, "象限": 8, "组织": 9
    # "rgpaph_num": "/": 0, "4项": 1, "3项": 2, "6项": 3, "2项": 4, "5项": 5, "更多": 6
    if 1 in text_type and t_num > 1:
        rgraph_type = []
        rgpaph_num = [rgpaph_nmap[str(t_num)] if t_num < 7 else 6]
        # 时间轴是一定包含日期m = re.match(".*\d{4}-\d{2}-\d{2}.*", s)
        n_option = 0
        for t_i in t_info:
            if t_i is None:
                continue
            t_str = t_i["content"]
            if t_str is None:
                break
            if bool(re.match(".*\d{4}-\d{2}-\d{2}.*", t_str)) or bool(re.match("\d{4}.*", t_str)) or bool(
                    re.match(".*\d{4}.*", t_str)):
                rgraph_type.extend([4])
            elif bool(re.match("\d{1}..*", t_str)) or bool(re.match(".*\d{1}..*", t_str)):
                rgraph_type.extend([2])
            else:
                n_option = 1

        if 2 in rgraph_type and n_option == 1:
            if 4 in rgraph_type:
                rgraph_type = [4, 5]
            else:
                rgraph_type = [5]
        # 循环
        if t_num >= 3:
            center_xy = []
            for tc, tb in zip(tclass, t_box):
                if tc == "GraphicObjectShape":
                    continue
                center_xy.append(get_cxy(tb))
            for i in range(0, len(center_xy) - 2, 1):
                if not is_triangle(center_xy[i], center_xy[i + 1], center_xy[i + 2]):
                    break
                rgraph_type.extend([3])
        if len(rgraph_type) < 1:
            if t_num == 2:
                rgraph_type.extend([6, 1])
            elif t_num == 4:
                rgraph_type.extend([8])
            else:
                rgraph_type.extend([1, 2])
            if "TitleTextShape" in tclass:
                rgraph_type.append(5)

    if not tuwen_lyout:
        tuwen_lyout.append(0)
    if not rgraph_type:
        rgraph_type.append(0)
    rgraph_t = remove_duplicate(rgraph_type)
    return text_type, tuwen_num, tuwen_lyout, rgraph_t, rgpaph_num


def extract_info_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        file_json = json.load(file)
    ppt_area = float(file_json["width"].replace("cm", "")) * float(file_json["height"].replace("cm", ""))
    t_len, s_len = len(file_json["Texts"]), len(file_json["Shapes"])
    t_list = extract_text_info(file_json["Texts"])
    s_list = extract_tuwen_info(file_json["Shapes"])

    return rules_info(ppt_area, t_len, s_len, t_list, s_list)


def extract_info_from_df(all_info, text_info):
    a_len = len(all_info)
    text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num = [0], [0], [0], [0], [0]
    if a_len <= 0:
        return text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num
    ppt_w, ppt_h = all_info.loc[0, "width"], all_info.loc[0, "height"]
    ppt_area = ppt_w * ppt_h

    # all_class = all_info["class"].value_counts()    # 统计相同元素个数
    # if "TitleTextShape" in all_class.index: # 默认是index
    #     print("TitleTextShape", True)
    # else:
    #     print("TitleTextShape", False)
    # if "GraphicObjectShape" in all_class.index:
    #     print("GraphicObjectShape", True)

    t_area, tstr_len, tclass, tname, t_info, t_box = [], [], [], [], [], []
    s_area, sclass, sname, s_box = [], [], [], []
    get_colums = ["class", "content", "content_size", "name",
                  "shape_x", "shape_y", "shape_width", "shape_height", "shape_area"]
    for idx in range(len(all_info.values)):
        g_c = all_info.loc[idx, get_colums]
        if "GraphicObjectShape" in g_c.values:
            sclass.append(g_c[0])
            s_area.append(g_c[-1])
            sname.append(g_c[3])
            s_box.append(g_c[4:8])
        else:
            tclass.append(g_c[0])
            t_info.append({"content": g_c[1]})
            tstr_len.append(g_c[2])
            t_area.append(g_c[-1])
            tname.append(g_c[3])
            t_box.append([g_c[4], g_c[5], g_c[6], g_c[7]])
    # a_i = all_class.index
    # a_v = all_class.values

    t_len, s_len = len(tclass), len(sclass)
    if len(text_info) != t_len:
        print("more text")
    t_list = [t_area, tclass, tname, t_box, tstr_len, t_info]
    s_list = [s_area, sclass, sname, s_box]
    return rules_info(ppt_area, t_len, s_len, t_list, s_list)


def compare_json_db(dir_root, db_path):
    with open(db_path, "rb") as f:
        result = chardet.detect(f.read())  # or readline if the file is large
    db_data = pd.read_csv(db_path, encoding=result["encoding"])
    file_name = db_data["file_name"]
    get_colums = ["page_type", "text_type", "chart_type",
                  "tuwen_num", "tuwen_layout", "rgraph_type", "rgpaph_num"]
    get_colums = ["text_type", "tuwen_num", "tuwen_layout", "rgraph_type", "rgpaph_num"]
    chname_map = ["页面类型", "纯文本:类型", "图表",
                  "图文:数量", "图文:板式布局", "关系图:类型", "关系图:项数"]
    for id, f_n in enumerate(file_name):
        f_n = f_n.replace(os.sep, "/")
        json_path = "%s/datasets/raw_data/19_work_template/%s" % (dir_root, f_n)
        print(json_path)
        text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num = extract_info_from_json(json_path)
        print(get_colums)
        print(text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num)
        get_values = db_data.loc[id, get_colums]
        print(get_values[0], get_values[1], get_values[2], get_values[3], get_values[4])


# def main():
#     text_info_columns = ['file_name', 'name', 'info_key',
#                          "font_size", "color", "margin_right", "letter_spacing",
#                          "text_position", "punctuation_wrap", "margin_left", "font_name",
#                          "font_style", "margin_bottom", "content", "font_variant",
#                          "font_weight", "font_size_asian", "text_underline_style", "text_indent",
#                          "text_shadow", "text_line_through_style", "text_align", "writing_mode",
#                          "font_name_asian", "language", "margin_top", "text_transform",
#                          "line_height"]
#     common_columns = ['subject', 'class', 'type', 'name',
#                       'width', 'height', 'file_name', 'type_unique',
#                       'key', 'estimate_title']
#     # 这里的shape指的元素
#     shape_columns = ['shape_height', 'shape_width', 'shape_x', 'shape_y',
#                      'shape_area', 'shape_num', 'text_num', 'over_shape_flag',
#                      'over_shape_num', 'over_shape_area', 'over_shape_area_rate', 'over_text_flag',
#                      'over_text_num', 'over_text_area', 'over_text_area_rate']
#     # 这里的text指的是文本框
#     text_columns = ['content_size', 'content', 'line', 'slope',
#                     'language', 'font-size-asian', 'font-name-asian', 'font-weight', 'font-name',
#                     'font-style', 'font-size']  # 这里的language到font-size指的是文本框中的第一个
#
#     all_columns = common_columns + shape_columns + text_columns
#     rules_list = [['"/": 0, "分条列举": 1,"关键词句": 2,"大段文本": 3'],
#                   ['"/": 0,  "1图": 1, "2图": 2, "3图": 3, "多图": 4, "4图": 5'],
#                   ['"/": 0, "小图留白": 1, "横向图区": 2, "竖向图区": 3,"大图片": 4, "图文均分": 6, "多图拼接": 5, "横向": 7, "竖向": 8'],
#                   ['"/": 0, "并列": 1, "流程": 2, "循环": 3, "时间轴": 4, "总分": 5, "对比": 6, "金字塔": 7, "象限": 8, "组织": 9'],
#                   ['"/": 0, "4项": 1, "3项": 2, "6项": 3, "2项": 4, "5项": 5, "更多": 6']]
#
#     cur_root = os.getcwd()
#     pj_root = os.path.abspath(os.path.dirname(os.getcwd()))
#     labels_path = "map_labels.json"
#     version = 'v1'
#     file1 = '20_work_template'
#     file2 = 'test'
#     # file3 = 'fen_tiao_lie_ju'
#     file3 = 'xiao_tu_liu_bai'
#     file4 = 'lo0.xml.json'
#     file4 = 'lo0.xml_1592553011453.json'
#     raw_path = "%s/datasets/raw_data/" % pj_root
#     file_name = os.path.join(file1, file2, file3, file4)
#     json_path = os.path.join(raw_path, file_name)
#
#     # 大段文本
#     # json_path = "F:/invocation/ppt_search/datasets/lo0.xml_1592552969019.json"
#     # json_path = "F:/invocation/ppt_search/datasets/lo0.xml_1593659918073.json"
#     # json_path = "F:/invocation/ppt_search/datasets/lo0.xml_1593680884631.json"
#
#     # 关键词句
#     # json_path = "F:/invocation/ppt_search/datasets/lo0.xml_1593659953368.json"
#
#     # 分条列举
#     # json_path = "F:/invocation/ppt_search/datasets/lo0.xml_1593662521248.json"
#
#     # 大图
#     # json_path = "F:/invocation/ppt_search/datasets/lo0.xml_1594105480923.json"
#
#     # 图文均分
#     # json_path = "F:/invocation/ppt_search/datasets/lo0.xml_1594194264042.json"
#     json_path = "F:/invocation/ppt_search/datasets/lo0.xml_1594195063443.json"
#
#     all_info, text_info = parse_json_2_csv(json_path, text_info_columns, all_columns)
#     text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num = extract_info_from_df(all_info, text_info)
#     for rl in rules_list:
#         print(rl)
#
#     print(text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num)
#     # text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num = extract_info_from_json(json_path)
#     # print(text_type, tuwen_num, tuwen_lyout, rgraph_type, rgpaph_num)
#     # print(json_path, extract_info_from_json(json_path))
#     # print(label_map)
#     # db_save = "%s/datasets/data_ppt/%s/db/ppt_scd.csv" % (pj_root, version)
#     # compare_json_db(pj_root, db_save)
#     return
#

if __name__ == "__main__":
    # re.search()比re.match()更耗时
    # search：在整个字符串中匹配，如果找不到匹配就返回None
    # match：在字符串开始位置匹配如果不匹配就返回None
    main()
    # s = "Today is 2020-03-04"
