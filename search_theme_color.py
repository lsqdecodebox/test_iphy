#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @Author : jliangqiu
# @Time : 2020/6/23
# @File : search_theme_color.py
import chardet
import numpy as np
import pandas as pd
import ict.themes_utils as itu


def rules_theme_compare(input_theme, gt_theme, n_thr, s_th):
    # compare
    local_loss = 0
    local_num = 0
    themes, scales, ws = input_theme

    for gt in gt_theme:     # gt theme
        gcc = gt.split(";")
        db_hw = gcc[-1].split(",")
        db_scale = float(db_hw[0]) / float(db_hw[1])
        num_r = 1e-6
        dbratio = gcc[-2].split(",")
        for n in range(n_thr):
            num_r += int(dbratio[n])
        dbw = [float(dbratio[n]) / num_r for n in range(n_thr)]
        gt_t = gcc[0].split(":")
        local_id = -1
        local_min = 1e6
        for i_n in range(len(ws)):      # local theme
            hw_scale, wh_scale = scales[i_n]
            w = ws[i_n]
            theme = themes[i_n]
            # print(g_c, db_scale, hw_scale, wh_scale)
            s_thh = 0.45 if db_scale > 2 and hw_scale > 2 else s_th
            s_thw = 0.45 if db_scale > 2 and wh_scale > 2 else s_th
            # if not (abs(db_scale - hw_scale) < s_thh or abs(db_scale - wh_scale) < s_thw):
            if not (0.7*db_scale < hw_scale < 1.3*db_scale):
                continue
            loss_dist = 0
            for i in range(n_thr):
                gc = gt_t[i].split(",")
                th = theme[i]
                h = abs(dbw[i] * int(gc[0]) - w[i] * th[0])
                s = abs(dbw[i] * int(gc[1]) - w[i] * th[1])
                v = abs(dbw[i] * int(gc[2]) - w[i] * th[2])
                loss_dist += (h + s + v)
            if loss_dist < local_min:
                local_min = loss_dist
                local_id = i_n
        print("Loss:", local_min)
        if local_id != -1:
            local_loss += local_min
            local_num += 1
    return local_loss, local_num


def graphic_themes_compare(input_graphic, db_graphic, db_colors,n_thr=3):
    best_id = -1
    num_r, min_v = 1e-6, 1e6
    s_th = 0.25
    img_num = len(input_graphic)
    scales, themes, ws = [], [], []
    for i in range(img_num):
        theme, nratio, hw = input_graphic[i]
        hw_scale = hw[0] / hw[1]
        wh_scale = hw[1] / hw[0]
        for n in range(n_thr):
            num_r += nratio[n]
        w = [nratio[n] / num_r for n in range(n_thr)]
        scales.append([hw_scale, wh_scale])
        themes.append(theme)
        ws.append(w)
    id_list, loss_list = [], []
    for id, g_c in enumerate(db_graphic):
        if g_c != g_c:
            continue
        db_num = g_c.count("$") + g_c.count("!") + 1
        if db_num != img_num:
            continue
        gt_l = []
        if "$" in g_c:
            g_cl = g_c.split("$")
            for g in g_cl:
                if "!" in g:
                    gt_l.extend(g.split("!"))
                else:
                    gt_l.append(g)
        elif "!" in g_c:
            gt_l = g_c.split("!")
        else:
            gt_l = [g_c]
        local_loss, local_num = rules_theme_compare([themes, scales, ws], gt_l, n_thr, s_th)

        tuwen_color_type = db_colors[id]
        flag = True
        if tuwen_color_type == '2':
            for theme,gc in zip(themes,gt_l):
                theme_one = theme[0]
                gc_one = gc.split(':')[0]
                theme_one_h = theme_one[0]
                theme_one_s = theme_one[1]
                theme_one_v = theme_one[2]

                gc_one_h = int(gc_one.split(',')[0])
                gc_one_s = int(gc_one.split(',')[1])
                gc_one_v = int(gc_one.split(',')[2])

                if theme_one_h >= gc_one_h - 15 \
                        and theme_one_h <= gc_one_h + 15 \
                        and theme_one_s >= gc_one_s - 15 \
                        and theme_one_s <= gc_one_s + 15 \
                        and theme_one_v >= gc_one_v - 15 \
                        and theme_one_v <= gc_one_v + 15:
                    flag = True
                else:
                    flag = False


        if local_num > 0 and flag:
            local_loss /= local_num
            id_list.append(id)
            loss_list.append(local_loss)
            if local_loss < min_v:
                min_v = local_loss
                best_id = id
    sorted_nums = sorted(enumerate(loss_list), key=lambda x: x[1])
    idx = [i[0] for i in sorted_nums]
    id_list = [id_list[i] for i in idx]
    loss_list = [loss_list[i] for i in idx]
    return id_list, loss_list


def theme_compare(input_paths, db_graphic,db_colors):
    max_color, resize = 10, 256
    f_call = itu.choice_themes_method(max_color)

    # test PPT search data base excellent PPT
    input_graphics = [itu.get_image_themes_color(f_call, img_path, resize=resize) for img_path in input_paths]
    id_list, loss_list = graphic_themes_compare(input_graphics, db_graphic,db_colors)
    return id_list, loss_list


def main():
    db_path = "F:/invocation/ppt_search/datasets/test_auto_graphic/tuwen_label.csv"
    db_path = '/Users/liushihan/PycharmProjects/ppt_auto_layout/datasets/data_ppt/v3/image/21_work_template/tuwen_label.csv'
    with open(db_path, "rb") as f:
        result = chardet.detect(f.read())  # or readline if the file is large
    db_data = pd.read_csv(db_path, encoding=result["encoding"])
    file_name = db_data["file_name"]
    db_graphic = db_data["image_color"]
    query_input = "../datasets/test_map_ppt/ppt/"
    query_input = '/Users/liushihan/PycharmProjects/ppt_auto_layout/datasets/raw_data/ppt/21_work_template/test_map_ppt/'
    input_paths = ["%stest1.pptx_lo0.xml.jpg" % query_input]*1
    search_id, search_loss = theme_compare(input_paths, db_graphic)
    if search_id != -1:
        print(search_id, [file_name[s_id] for s_id in search_id])
    else:
        print("no search")


if __name__ == "__main__":
    main()
