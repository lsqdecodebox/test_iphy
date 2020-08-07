import os
import shutil
import pandas as pd
import json
import numpy as np
import re
def get_match_element(shape_ppt,i):
    one_shape = {}
    one_shape['name'] = shape_ppt.iloc[i]['name']
    one_shape['x'] = '%.3f' % shape_ppt.iloc[i]['shape_x']
    one_shape['y'] = '%.3f' % shape_ppt.iloc[i]['shape_y']
    one_shape['height'] = '%.3f' % shape_ppt.iloc[i]['shape_height']
    one_shape['width'] = '%.3f' % shape_ppt.iloc[i]['shape_width']
    return one_shape

def deal_graphic(shape_best_ppt,shape_query_df,
                 input_shape_list,output_shape_list,
                 deal_shape_query_key,deal_shape_best_key,
                 shape_i_to_j,shape_i_to_j_adjust,
                 graphic_query_df_area_group):
    '''
    处理图片
    :param shape_best_ppt:
    :param shape_query_df:
    :param input_shape_list:
    :param output_shape_list:
    :param deal_shape_query_key:
    :param deal_shape_best_key:
    :param shape_i_to_j:
    :param graphic_query_df_area_group:
    :return:
    '''
    shape_best_ppt.loc[:,'graphic_area_group'] = 1
    graphic_best_df_area_group = \
        shape_best_ppt[shape_best_ppt['class'] == 'GraphicObjectShape'].groupby(['shape_area'], as_index=False)[
            'class'].count()
    graphic_best_df_area_group.rename(columns={'class': 'count'}, inplace=True)
    graphic_best_df_area_group = graphic_best_df_area_group.sort_values(['count', 'shape_area'],
                                                                        ascending=[False, False])

    for i in range(len(graphic_best_df_area_group)):
        area = graphic_best_df_area_group.iloc[i]['shape_area']
        count = graphic_best_df_area_group.iloc[i]['count']
        shape_best_ppt.loc[(shape_best_ppt['shape_area'] == area)
                                             & (shape_best_ppt['class'] == 'GraphicObjectShape'),'graphic_area_group'] = count

    graphic_query_df_area_group = graphic_query_df_area_group.sort_values(['count', 'shape_area'],
                                                                          ascending=[False, False])

    for i in range(len(graphic_query_df_area_group)):
        query_area = graphic_query_df_area_group.iloc[i]['shape_area']
        query_count = graphic_query_df_area_group.iloc[i]['count']
        if query_count < 2:
            break
        for j in range(len(graphic_best_df_area_group)):
            best_area = graphic_best_df_area_group.iloc[i]['shape_area']
            best_count = graphic_best_df_area_group.iloc[i]['count']

            if best_count < 2:
                break

            if query_count == best_count:
                area_shape_query_ppt = shape_query_df[(shape_query_df['shape_area'] == query_area)
                                                      & (shape_query_df['class'] == 'GraphicObjectShape')]
                area_shape_query_ppt = area_shape_query_ppt.sort_values(['shape_y', 'shape_x'],
                                                                        ascending=[True, True])

                area_shape_best_ppt = shape_best_ppt[(shape_best_ppt['shape_area'] == best_area)
                                                     & (shape_best_ppt['class'] == 'GraphicObjectShape')]
                area_shape_best_ppt = area_shape_best_ppt.sort_values(['shape_y', 'shape_x'],
                                                                      ascending=[True, True])

                for i in range(int(query_count)):

                    query_key = area_shape_query_ppt.iloc[i]['key']
                    best_key = area_shape_best_ppt.iloc[i]['key']

                    shape_i_to_j_adjust = get_adjust_image(area_shape_query_ppt, area_shape_best_ppt, i, shape_i_to_j_adjust)

                    deal_shape_query_key.append(query_key)
                    deal_shape_best_key.append(best_key)

                    shape_i_to_j[query_key] = best_key
                    one_query_shape = get_match_element(area_shape_query_ppt, i)
                    one_best_shape = get_match_element(area_shape_best_ppt, i)
                    input_shape_list.append(one_query_shape)
                    output_shape_list.append(one_best_shape)

    left_graphic_query = shape_query_df[(shape_query_df['class'] != 'Chart')
                                        & (shape_query_df['class'] == 'GraphicObjectShape')
                                        & (shape_query_df['graphic_area_group'] < 2)]

    left_graphic_best = shape_best_ppt[(shape_best_ppt['class'] != 'Chart')
                                       & (shape_best_ppt['class'] == 'GraphicObjectShape')
                                       & (shape_best_ppt['graphic_area_group'] < 2)]

    left_graphic_query = left_graphic_query.sort_values(['shape_area', 'shape_y', 'shape_x'],
                                                        ascending=[True, True, True])
    left_graphic_best = left_graphic_best.sort_values(['shape_area', 'shape_y', 'shape_x'],
                                                      ascending=[True, True, True])

    for i in range(len(left_graphic_query)):

        query_key = left_graphic_query.iloc[i]['key']
        best_key = left_graphic_best.iloc[i]['key']
        shape_i_to_j_adjust = get_adjust_image(left_graphic_query, left_graphic_best, i, shape_i_to_j_adjust)

        deal_shape_query_key.append(query_key)
        deal_shape_best_key.append(best_key)

        shape_i_to_j[query_key] = best_key
        one_query_shape = get_match_element(left_graphic_query, i)
        one_best_shape = get_match_element(left_graphic_best, i)

        input_shape_list.append(one_query_shape)
        output_shape_list.append(one_best_shape)

    return input_shape_list,output_shape_list,deal_shape_query_key,deal_shape_best_key,shape_i_to_j,shape_i_to_j_adjust

def deal_chart(shape_best_ppt,shape_query_df,input_shape_list,output_shape_list,deal_shape_query_key,deal_shape_best_key,shape_i_to_j,chart_len):
    '''
    处理chart
    :param shape_best_ppt:
    :param shape_query_df:
    :param input_shape_list:
    :param output_shape_list:
    :param deal_shape_query_key:
    :param deal_shape_best_key:
    :param shape_i_to_j:
    :param chart_len:
    :return:
    '''
    chart_shape_best_ppt = shape_best_ppt[shape_best_ppt['class'] == 'Chart']
    chart_shape_query_ppt = shape_query_df[shape_query_df['class'] == 'Chart']
    chart_shape_best_ppt = chart_shape_best_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
    chart_shape_query_ppt = chart_shape_query_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

    for i in range(chart_len):
        query_key = chart_shape_query_ppt.iloc[i]['key']
        best_key = chart_shape_best_ppt.iloc[i]['key']
        deal_shape_query_key.append(query_key)
        deal_shape_best_key.append(best_key)
        shape_i_to_j[query_key] = best_key
        one_query_shape = get_match_element(chart_shape_query_ppt, i)
        one_best_shape = get_match_element(chart_shape_best_ppt, i)
        input_shape_list.append(one_query_shape)
        output_shape_list.append(one_best_shape)

        return input_shape_list,output_shape_list,deal_shape_query_key,deal_shape_best_key,shape_i_to_j

def get_adjust_image(area_shape_query_ppt,area_shape_best_ppt,i,shape_i_to_j_adjust):
    query_key = area_shape_query_ppt.iloc[i]['key']
    best_key = area_shape_best_ppt.iloc[i]['key']
    input_dict = {}
    input_dict['id'] = query_key
    output_dict = {}
    output_dict['id'] = best_key
    shape_i_to_j_adjust['input'].append(input_dict)
    shape_i_to_j_adjust['output'].append(output_dict)
    return shape_i_to_j_adjust

def get_adjust_text(area_text_query_ppt,area_text_best_ppt,i,text_i_to_j_adjust):

    font_list = [8,9,10,12,14,16,18,20,24,28,32,36,40,44,48,54,60,66,72,80,88,96]
    query_key = area_text_query_ppt.iloc[i]['key']
    best_key = area_text_best_ppt.iloc[i]['key']

    query_content_size = area_text_query_ppt.iloc[i]['content_size']
    best_content_size = area_text_best_ppt.iloc[i]['content_size']

    query_content = area_text_query_ppt.iloc[i]['content']
    best_content = area_text_best_ppt.iloc[i]['content']

    query_lan = area_text_query_ppt.iloc[i]['language']
    best_lan = area_text_best_ppt.iloc[i]['language']

    len_rate = 1.0
    len_query_rate = 1.0
    len_best_rate = 1.0

    if query_lan == 'en':
        zhmodel = re.compile(u'[\u4e00-\u9fa5]')
        res = zhmodel.search(query_content)
        if res:
            len_query_rate = 1.0
        else:
            len_query_rate = 1.3

    if best_lan == 'en':
        zhmodel = re.compile(u'[\u4e00-\u9fa5]')
        res = zhmodel.search(best_content)
        if res:
            len_best_rate = 1.0
        else:
            len_best_rate = 1.3

    len_rate = len_best_rate/len_query_rate
    query_font_size = float(0.0 if area_text_query_ppt.iloc[i]['font-size'].replace('pt','') == '' else float(area_text_query_ppt.iloc[i]['font-size'].replace('pt','')))
    best_font_size = float(0.0 if area_text_best_ppt.iloc[i]['font-size'].replace('pt','') == '' else float(area_text_best_ppt.iloc[i]['font-size'].replace('pt','')))

    font_rate = (float(best_content_size)/query_content_size)/len_rate
    adjust_rate = font_rate
    if font_rate > 5:
        adjust_rate = 5.0
    elif font_rate < 0.2:
        adjust_rate = 0.2

    adjust_best_font_size = best_font_size*adjust_rate

    for k in range(len(font_list)):
        if k == 0 and adjust_best_font_size < font_list[k]:
            adjust_best_font_size = font_list[k]
            break
        elif k == len(font_list) - 1:
            adjust_best_font_size = font_list[k]
            break
        elif (adjust_best_font_size < font_list[k+1] and adjust_best_font_size >= font_list[k]):
            adjust_best_font_size = font_list[k]
            break

    input_dict = {}
    input_dict['id'] = query_key
    text_i_to_j_adjust['input'].append(input_dict)
    output_dict = {}
    output_dict['id'] = best_key
    output_dict['font-size'] = adjust_best_font_size

    text_i_to_j_adjust['output'].append(output_dict)




    return text_i_to_j_adjust

def deal_text_group_v4(text_best_ppt, text_query_df,
                      input_text_list, output_text_list,
                      deal_query_key, deal_best_key,
                      text_i_to_j,text_i_to_j_adjust,
                      max_text_group, max_font_group,
                      title_len,
                      second_flag,
                      pair_font_flag,
                      text_best_df_area_group, text_best_df_font_group, text_query_df_area_group,
                      text_query_df_font_group,
                      rgraph_type):
    if (max_font_group < max_text_group + 1) and pair_font_flag == False:

        text_query_df_area_group = text_query_df_area_group.sort_values(['count', 'shape_area'],
                                                                        ascending=[False, False])

        for k in range(len(text_query_df_area_group)):
            query_area = text_query_df_area_group.iloc[k]['shape_area']
            query_count = text_query_df_area_group.iloc[k]['count']
            if query_count < 2:
                break
            for j in range(len(text_best_df_area_group)):
                best_area = text_best_df_area_group.iloc[j]['shape_area']
                best_count = text_best_df_area_group.iloc[j]['count']

                if best_count < 2:
                    break

                if query_count == best_count:
                    if [5, 0] == rgraph_type:
                        area_text_query_ppt = text_query_df[(text_query_df['shape_area'] == query_area) & (
                                    text_query_df['area_group'] == max_text_group)]

                        # area_text_query_ppt = text_query_df[text_query_df['shape_area'] == query_area]
                    else:
                        area_text_query_ppt = text_query_df[text_query_df['shape_area'] == query_area]

                        # area_text_query_ppt = text_query_df[(text_query_df['shape_area'] == query_area) & (text_query_df['area_group'] == max_text_group)]

                    # 由于匹配的问题,特别是高度，有些几乎一样高，但是差那么零点几
                    area_text_query_ppt.loc[:, 'shape_y_round'] = area_text_query_ppt['shape_y'].map(
                        lambda x: np.floor(x))
                    area_text_query_ppt.loc[:, 'shape_x_round'] = area_text_query_ppt['shape_x'].map(
                        lambda x: np.floor(x))
                    area_text_query_ppt = area_text_query_ppt.sort_values(['shape_y_round', 'shape_x_round'],
                                                                          ascending=[True, True])

                    area_text_best_ppt = text_best_ppt[text_best_ppt['shape_area'] == best_area]
                    area_text_best_ppt.loc[:, 'shape_y_round'] = area_text_best_ppt['shape_y'].map(
                        lambda x: np.floor(x))
                    area_text_best_ppt.loc[:, 'shape_x_round'] = area_text_best_ppt['shape_x'].map(
                        lambda x: np.floor(x))

                    area_text_best_ppt = area_text_best_ppt.sort_values(['shape_y_round', 'shape_x_round'],
                                                                        ascending=[True, True])

                    for i in range(int(query_count)):
                        query_key = area_text_query_ppt.iloc[i]['key']
                        best_key = area_text_best_ppt.iloc[i]['key']

                        if (query_key in deal_query_key) | (best_key in deal_best_key):
                            break

                        text_i_to_j_adjust = get_adjust_text(area_text_query_ppt,
                                                             area_text_best_ppt,
                                                             i,
                                                             text_i_to_j_adjust)

                        deal_query_key.append(query_key)
                        deal_best_key.append(best_key)

                        text_i_to_j[query_key] = best_key
                        one_query_shape = get_match_element(area_text_query_ppt, i)
                        one_best_shape = get_match_element(area_text_best_ppt, i)

                        input_text_list.append(one_query_shape)
                        output_text_list.append(one_best_shape)

        if title_len > 0:
            left_text_query = text_query_df[(text_query_df['class'] != 'TitleTextShape')
                                            & (text_query_df['estimate_title'] != 1)
                                            & (text_query_df['class'] != 'Table')
                                            & (text_query_df['area_group'] < 2)]

            if second_flag:

                left_text_best = text_best_ppt[(text_best_ppt['class'] != 'TitleTextShape')
                                               & (text_best_ppt['class'] != 'OutlinerShape')
                                               & (text_best_ppt['estimate_title'] != 1)
                                               & (text_best_ppt['class'] != 'Table')
                                               & (text_best_ppt['area_group'] < 2)]
            else:
                left_text_best = text_best_ppt[(text_best_ppt['class'] != 'TitleTextShape')
                                               & (text_best_ppt['estimate_title'] != 1)
                                               & (text_best_ppt['class'] != 'Table')
                                               & (text_best_ppt['area_group'] < 2)]

        else:
            left_text_query = text_query_df[(text_query_df['class'] != 'TitleTextShape')
                                            # & (text_query_df['class'] != 'OutlinerShape')
                                            & (text_query_df['class'] != 'Table')
                                            & (text_query_df['area_group'] < 2)]

            left_text_best = text_best_ppt[(text_best_ppt['class'] != 'TitleTextShape')
                                           # & (text_best_ppt['class'] != 'OutlinerShape')
                                           & (text_best_ppt['class'] != 'Table')
                                           & (text_best_ppt['area_group'] < 2)]

        # left_text_query = left_text_query.sort_values(['shape_area', 'shape_y', 'shape_x'],
        #                                               ascending=[True, True, True])
        # left_text_best = left_text_best.sort_values(['shape_area', 'shape_y', 'shape_x'],
        #                                             ascending=[True, True, True])

        left_text_query = left_text_query.sort_values(['content_size', 'shape_area', 'shape_y', 'shape_x'],
                                                      ascending=[False, False, True, True])
        left_text_best = left_text_best.sort_values(['content_size', 'shape_area', 'shape_y', 'shape_x'],
                                                    ascending=[False, False, True, True])

        for i in range(len(left_text_query)):
            query_key = left_text_query.iloc[i]['key']
            best_key = left_text_best.iloc[i]['key']

            text_i_to_j_adjust = get_adjust_text(left_text_query,
                                                 left_text_best,
                                                 i,
                                                 text_i_to_j_adjust)

            deal_query_key.append(query_key)
            deal_best_key.append(best_key)

            text_i_to_j[query_key] = best_key
            one_query_shape = get_match_element(left_text_query, i)
            one_best_shape = get_match_element(left_text_best, i)

            input_text_list.append(one_query_shape)
            output_text_list.append(one_best_shape)

    else:
        text_query_df_font_group = text_query_df_font_group.sort_values(['count', 'font-size'],
                                                                        ascending=[False, False])

        for i in range(len(text_query_df_font_group)):
            query_font_size = text_query_df_font_group.iloc[i]['font-size']
            query_font_name = text_query_df_font_group.iloc[i]['font-name']
            query_font_weight = text_query_df_font_group.iloc[i]['font-weight']
            query_font_size_asian = text_query_df_font_group.iloc[i]['font-size-asian']
            query_font_name_asian = text_query_df_font_group.iloc[i]['font-name-asian']
            query_font_style = text_query_df_font_group.iloc[i]['font-style']
            query_count = text_query_df_font_group.iloc[i]['count']
            if query_count < 2:
                break
            for j in range(len(text_best_df_font_group)):
                # best_area = text_best_df_font_group.iloc[i]['shape_area']
                best_font_size = text_best_df_font_group.iloc[j]['font-size']
                best_font_name = text_best_df_font_group.iloc[j]['font-name']
                best_font_weight = text_best_df_font_group.iloc[j]['font-weight']
                best_font_size_asian = text_best_df_font_group.iloc[j]['font-size-asian']
                best_font_name_asian = text_best_df_font_group.iloc[j]['font-name-asian']
                best_font_style = text_best_df_font_group.iloc[j]['font-style']
                best_count = text_best_df_font_group.iloc[j]['count']

                if best_count < 2:
                    break

                if query_count == best_count:
                    font_text_query_ppt = text_query_df[(text_query_df['font-size'] == query_font_size) &
                                                        (text_query_df['font-name'] == query_font_name) &
                                                        (text_query_df['font-weight'] == query_font_weight) &
                                                        (text_query_df[
                                                             'font-size-asian'] == query_font_size_asian) &
                                                        (text_query_df[
                                                             'font-name-asian'] == query_font_name_asian) &
                                                        (text_query_df['font-style'] == query_font_style)]
                    font_text_query_ppt = font_text_query_ppt.sort_values(['shape_y', 'shape_x'],
                                                                          ascending=[True, True])

                    font_text_best_ppt = text_best_ppt[(text_best_ppt['font-size'] == best_font_size) &
                                                       (text_best_ppt['font-name'] == best_font_name) &
                                                       (text_best_ppt['font-weight'] == best_font_weight) &
                                                       (text_best_ppt[
                                                            'font-size-asian'] == best_font_size_asian) &
                                                       (text_best_ppt[
                                                            'font-name-asian'] == best_font_name_asian) &
                                                       (text_best_ppt['font-style'] == best_font_style)]

                    font_text_best_ppt = font_text_best_ppt.sort_values(['shape_y', 'shape_x'],
                                                                        ascending=[True, True])

                    for i in range(int(query_count)):
                        query_key = font_text_query_ppt.iloc[i]['key']
                        best_key = font_text_best_ppt.iloc[i]['key']

                        if (query_key in deal_query_key) | (best_key in deal_best_key):
                            break

                        text_i_to_j_adjust = get_adjust_text(font_text_query_ppt,
                                                             font_text_best_ppt,
                                                             i,
                                                             text_i_to_j_adjust)

                        deal_query_key.append(query_key)
                        deal_best_key.append(best_key)

                        text_i_to_j[query_key] = best_key
                        one_query_shape = get_match_element(font_text_query_ppt, i)
                        one_best_shape = get_match_element(font_text_best_ppt, i)

                        input_text_list.append(one_query_shape)
                        output_text_list.append(one_best_shape)

        if title_len > 0:
            left_text_query = text_query_df[(text_query_df['class'] != 'TitleTextShape')
                                            & (text_query_df['class'] != 'Table')
                                            & (text_query_df['font_group'] < 2)]

            if second_flag:

                left_text_best = text_best_ppt[(text_best_ppt['class'] != 'TitleTextShape')
                                               & (text_best_ppt['class'] != 'OutlinerShape')
                                               & (text_best_ppt['class'] != 'Table')
                                               & (text_best_ppt['area_group'] < 2)]
            else:
                left_text_best = text_best_ppt[(text_best_ppt['class'] != 'TitleTextShape')
                                               & (text_best_ppt['class'] != 'Table')
                                               & (text_best_ppt['area_group'] < 2)]

        else:
            left_text_query = text_query_df[(text_query_df['class'] != 'TitleTextShape')
                                            & (text_query_df['class'] != 'OutlinerShape')
                                            & (text_query_df['class'] != 'Table')
                                            & (text_query_df['font_group'] < 2)]

            left_text_best = text_best_ppt[(text_best_ppt['class'] != 'TitleTextShape')
                                           & (text_best_ppt['class'] != 'OutlinerShape')
                                           & (text_best_ppt['class'] != 'Table')
                                           & (text_best_ppt['area_group'] < 2)]

        # left_text_query = left_text_query.sort_values(['shape_area', 'shape_y', 'shape_x'],
        #                                               ascending=[True, True, True])
        # left_text_best = left_text_best.sort_values(['shape_area', 'shape_y', 'shape_x'],
        #                                             ascending=[True, True, True])

        left_text_query = left_text_query.sort_values(['content_size', 'shape_area', 'shape_y', 'shape_x'],
                                                      ascending=[False, False, True, True])
        left_text_best = left_text_best.sort_values(['content_size', 'shape_area', 'shape_y', 'shape_x'],
                                                    ascending=[False, False, True, True])

        for i in range(len(left_text_query)):
            query_key = left_text_query.iloc[i]['key']
            best_key = left_text_best.iloc[i]['key']

            text_i_to_j_adjust = get_adjust_text(left_text_query,
                                                 left_text_best,
                                                 i,
                                                 text_i_to_j_adjust)

            deal_query_key.append(query_key)
            deal_best_key.append(best_key)

            text_i_to_j[query_key] = best_key
            one_query_shape = get_match_element(left_text_query, i)
            one_best_shape = get_match_element(left_text_best, i)

            input_text_list.append(one_query_shape)
            output_text_list.append(one_best_shape)
    return input_text_list, output_text_list, deal_query_key, deal_best_key, text_i_to_j,text_i_to_j_adjust


def deal_table_v4(text_best_ppt,text_query_df,input_text_list,output_text_list,deal_query_key,deal_best_key,text_i_to_j,table_len):
    '''
    处理table
    :param text_best_ppt:
    :param text_query_df:
    :param input_text_list:
    :param output_text_list:
    :param deal_query_key:
    :param deal_best_key:
    :param text_i_to_j:
    :param table_len:
    :return:
    '''
    table_text_best_ppt = text_best_ppt[text_best_ppt['class'] == 'Table']
    table_text_query_ppt = text_query_df[text_query_df['class'] == 'Table']
    table_text_best_ppt = table_text_best_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
    table_text_query_ppt = table_text_query_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

    for i in range(table_len):

        query_key = table_text_query_ppt.iloc[i]['key']
        best_key = table_text_best_ppt.iloc[i]['key']

        deal_query_key.append(query_key)
        deal_best_key.append(best_key)

        text_i_to_j[query_key] = best_key
        one_query_shape = get_match_element(table_text_query_ppt, i)

        one_best_shape = get_match_element(table_text_best_ppt, i)

        input_text_list.append(one_query_shape)
        output_text_list.append(one_best_shape)
    return input_text_list,output_text_list,deal_query_key,deal_best_key,text_i_to_j


def deal_title_v4(text_best_df,text_query_df,
                  input_text_list,output_text_list,
                  deal_query_key,deal_best_key,
                  text_i_to_j,text_i_to_j_adjust,
                  title_combine_len,
                  second_flag,
                  best_ppt_stat):
    '''
    处理title
    :param text_best_ppt:
    :param text_query_df:
    :param input_text_list:
    :param output_text_list:
    :param deal_query_key:
    :param deal_best_key:
    :param text_i_to_j:
    :param title_len:
    :param outline_len:
    :param new_title_len:
    :param second_flag:
    :return:
    '''

    if title_combine_len != 0:
        # outline_len = best_ppt_stat.iloc[0]['outline_num']
        title_len = best_ppt_stat.iloc[0]['title_num']
        new_title_num = best_ppt_stat.iloc[0]['new_title_num']
        font_size_estimate_title_num = best_ppt_stat.iloc[0]['font_size_estimate_title_num']
        if title_len == 0 and font_size_estimate_title_num == 1:
            text_best_df.loc[text_best_df['font_size_estimate_title'] == 1, 'new_class'] = 'title'
            text_best_df.loc[text_best_df['font_size_estimate_title'] == 1, 'class'] = 'TitleTextShape'

        elif title_len == 0  and font_size_estimate_title_num == 0 and new_title_num == 1:

            text_best_df.loc[text_best_df['estimate_title'] == 1, 'new_class'] = 'title'
            text_best_df.loc[text_best_df['estimate_title'] == 1, 'class'] = 'TitleTextShape'



        if second_flag:
            title_text_best_df = text_best_df[text_best_df['class'] == 'OutlinerShape']
            title_text_best_df = title_text_best_df.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
        else:
            title_text_best_df = text_best_df[(text_best_df['class'] == 'TitleTextShape')]
            title_text_best_df = title_text_best_df.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

        title_text_query_df = text_query_df[text_query_df['class'] == 'TitleTextShape']
        title_text_query_df = title_text_query_df.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

        for i in range(title_combine_len):

            query_key = title_text_query_df.iloc[i]['key']
            best_key = title_text_best_df.iloc[i]['key']

            text_i_to_j_adjust = get_adjust_text(title_text_query_df,
                                                 title_text_best_df,
                                                 i,
                                                 text_i_to_j_adjust)

            deal_query_key.append(query_key)
            deal_best_key.append(best_key)

            text_i_to_j[query_key] = best_key
            one_query_shape = get_match_element(title_text_query_df, i)
            one_best_shape = get_match_element(title_text_best_df, i)



            input_text_list.append(one_query_shape)
            output_text_list.append(one_best_shape)
    return text_best_df, text_query_df, input_text_list, output_text_list, deal_query_key, deal_best_key, text_i_to_j,text_i_to_j_adjust

def deal_title(text_best_ppt,text_query_df,input_text_list,output_text_list,deal_query_key,deal_best_key,text_i_to_j,
               title_len,outline_len,new_title_len,new_title,second_flag):
    '''
    处理title
    :param text_best_ppt:
    :param text_query_df:
    :param input_text_list:
    :param output_text_list:
    :param deal_query_key:
    :param deal_best_key:
    :param text_i_to_j:
    :param title_len:
    :param outline_len:
    :param new_title_len:
    :param second_flag:
    :return:
    '''
    if title_len != 0:
        if second_flag:
            title_text_best_ppt = text_best_ppt[text_best_ppt['class'] == 'OutlinerShape']
            title_text_best_ppt = title_text_best_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
        else:
            title_text_best_ppt = text_best_ppt[text_best_ppt['class'] == 'TitleTextShape']
            title_text_best_ppt = title_text_best_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

        title_text_query_ppt = text_query_df[text_query_df['class'] == 'TitleTextShape']
        title_text_query_ppt = title_text_query_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

        for i in range(title_len):

            query_key = title_text_query_ppt.iloc[i]['key']
            best_key = title_text_best_ppt.iloc[i]['key']

            deal_query_key.append(query_key)
            deal_best_key.append(best_key)

            text_i_to_j[query_key] = best_key
            one_query_shape = get_match_element(title_text_query_ppt, i)
            one_best_shape = get_match_element(title_text_best_ppt, i)



            input_text_list.append(one_query_shape)
            output_text_list.append(one_best_shape)
    elif outline_len != 0:
        out_text_best_ppt = text_best_ppt[text_best_ppt['class'] == 'OutlinerShape']
        out_text_query_ppt = text_query_df[text_query_df['class'] == 'OutlinerShape']
        out_text_best_ppt = out_text_best_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
        out_text_query_ppt = out_text_query_ppt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

        for i in range(outline_len):

            query_key = out_text_query_ppt.iloc[i]['key']
            best_key = out_text_best_ppt.iloc[i]['key']
            deal_query_key.append(query_key)
            deal_best_key.append(best_key)

            text_i_to_j[query_key] = best_key
            one_query_shape = get_match_element(out_text_query_ppt, i)
            one_best_shape = get_match_element(out_text_best_ppt, i)

            input_text_list.append(one_query_shape)
            output_text_list.append(one_best_shape)
    elif new_title_len == 1:

        title_text_query_ppt = text_query_df.loc[new_title[0]]
        title_text_best_ppt = text_best_ppt[text_best_ppt['class'] == 'TitleTextShape']

        query_key = title_text_query_ppt.iloc[0]['key']
        best_key = title_text_best_ppt.iloc[0]['key']
        deal_query_key.append(query_key)
        deal_best_key.append(best_key)

        one_query_shape = get_match_element(title_text_query_ppt, 0)
        one_best_shape = get_match_element(title_text_best_ppt, 0)


        input_text_list.append(one_query_shape)
        output_text_list.append(one_best_shape)

        text_i_to_j[query_key] = best_key

        return text_best_ppt, text_query_df, input_text_list, output_text_list, deal_query_key, deal_best_key,text_i_to_j

    return text_best_ppt, text_query_df, input_text_list, output_text_list, deal_query_key, deal_best_key, text_i_to_j





def deal_elements_match_v4(query_df,query_all_info_df,recommend_df,
                        second_flag,
                        root_path,version,file1,file2,file3,file4,
                        file1_db,query_labels,db_df,all_db):
    '''
    元素匹配
    :param query_df:
    :param query_all_info_df:
    :param recommend_df:
    :param second_flag:
    :param root_path:
    :param version:
    :param file1:
    :param file2:
    :param file3:
    :param file4:
    :param file1_db:
    :return:
    '''
    # ==================================================
    # 统计数据
    # ==================================================
    rgraph_type = query_labels['rgraph_type']
    max_font_group = query_df.iloc[0]['max_font_group']
    max_text_group = query_df.iloc[0]['max_text_group']
    text_len = query_df.iloc[0]['text_num']
    shape_len = query_df.iloc[0]['shape_num']
    outline_len = query_df.iloc[0]['outline_num']
    title_len = query_df.iloc[0]['title_num']
    table_len = query_df.iloc[0]['table_num']
    chart_len = query_df.iloc[0]['chart_num']
    graphic_len = query_df.iloc[0]['graphic_num']
    new_title_len = query_df.iloc[0]['new_title_num']
    font_size_estimate_title_num = query_df.iloc[0]['font_size_estimate_title_num']
    new_title = []
    # ==================================================
    # 查询数据预处理
    # ==================================================
    subject_class = list(query_all_info_df['subject'].unique())
    if 'texts' in subject_class:
        text_query_df = query_all_info_df[query_all_info_df['subject'] == 'texts']

        if title_len == 0 and outline_len == 0 and font_size_estimate_title_num == 1:
            text_query_df.loc[text_query_df['font_size_estimate_title'] == 1, 'new_class'] = 'title'
            text_query_df.loc[text_query_df['font_size_estimate_title'] == 1, 'class'] = 'TitleTextShape'

        elif title_len == 0 and outline_len == 0 and font_size_estimate_title_num == 0:

            # 制造新的title
            new_title = []
            for i in range(text_len):
                one_text = text_query_df[i:i + 1]
                one_text_x = one_text.iloc[0]['shape_x']
                one_text_y = one_text.iloc[0]['shape_y']
                one_text_w = one_text.iloc[0]['shape_width']
                one_text_h = one_text.iloc[0]['shape_height']
                one_w = one_text.iloc[0]['width']
                one_h = one_text.iloc[0]['height']

                if one_text_y + one_text_h < one_h / 5:
                    new_title.append(i)

            if len(new_title) == 1:
                new_title_len = 1
                text_query_df.loc[new_title[0], 'new_class'] = 'title'
                text_query_df.loc[new_title[0], 'class'] = 'TitleTextShape'
            else:
                new_title_len = 0

        if title_len > 1:
            title_text_query_df = text_query_df[text_query_df['class'] == 'TitleTextShape']

            title_text_query_df = title_text_query_df.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
            top_key = title_text_query_df.iloc[0]['key']
            all_key = list(title_text_query_df['key'].unique())
            all_key.remove(top_key)
            for key in all_key:
                text_query_df['class'][text_query_df['key'] == key] = 'TextShape'

        title_combine_len = 0
        if title_len == 1:
            title_combine_len = 1
        elif new_title_len == 1:
            title_combine_len = 1
        elif font_size_estimate_title_num == 1:
            title_combine_len = 1

        text_query_df_area_group = \
        text_query_df[text_query_df['class'] != 'TitleTextShape'].groupby(['shape_area'], as_index=False)[
            'class'].count()

        text_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)

        # 将area的分组结果对每一个元素赋值
        text_query_df.loc[:,'area_group'] = 1
        if len(text_query_df_area_group) == 0:
            max_text_group = 1
        else:
            max_text_group = max(text_query_df_area_group['count'])

        if [5,0] == rgraph_type:
            max_text_group = max_text_group - 1
            for i in range(len(text_query_df_area_group)):
                area = text_query_df_area_group.iloc[i]['shape_area']
                count = text_query_df_area_group.iloc[i]['count']
                text_query_df_area_group.loc[i,'count'] = count - 1
                text_query_df['area_group'][(text_query_df['shape_area'] == area)
                                            & (text_query_df.content.str.match('^\d{1,2}[\\.|\\-|\\*|\\,|，｜、｜）｜)]'))] = count - 1
        else:
            for i in range(len(text_query_df_area_group)):
                area = text_query_df_area_group.iloc[i]['shape_area']
                count = text_query_df_area_group.iloc[i]['count']
                # text_query_df['area_group'][text_query_df['shape_area'] == area] = count
                text_query_df.loc[text_query_df['shape_area'] == area,'area_group'] = count


        # 字体
        text_query_df_font_group = text_query_df[text_query_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                                      'font-name',
                                                                                                      'font-weight',
                                                                                                      'font-size-asian',
                                                                                                      'font-name-asian',
                                                                                                      'font-style'],
                                                                                                     as_index=False)[
            'class'].count()
        text_query_df_font_group.rename(columns={'class': 'count'}, inplace=True)

        text_query_df.loc[:,'font_group'] = 1

        if len(text_query_df_font_group) == 0:
            max_font_group = 1
        else:
            max_font_group = max(text_query_df_font_group['count'])


        # 针对总分
        if [5,0] == rgraph_type:
            max_font_group = max_font_group - 1
            for i in range(len(text_query_df_font_group)):
                font_size = text_query_df_font_group.iloc[i]['font-size']
                font_name = text_query_df_font_group.iloc[i]['font-name']
                font_weight = text_query_df_font_group.iloc[i]['font-weight']
                font_size_asian = text_query_df_font_group.iloc[i]['font-size-asian']
                font_name_asian = text_query_df_font_group.iloc[i]['font-name-asian']
                font_style = text_query_df_font_group.iloc[i]['font-style']
                count = text_query_df_font_group.iloc[i]['count']
                text_query_df_font_group.loc[i, 'count'] = count - 1
                # 满足font分组的元素属于分组大小为count,那么font_count = count
                text_query_df['font_group'][(text_query_df['font-size'] == font_size) &
                                            (text_query_df['font-name'] == font_name) &
                                            (text_query_df['font-weight'] == font_weight) &
                                            (text_query_df['font-size-asian'] == font_size_asian) &
                                            (text_query_df['font-name-asian'] == font_name_asian) &
                                            (text_query_df['font-style'] == font_style) &
                                            (text_query_df.content.str.match('^\d{1,2}[\\.|\\-|\\*|\\,|，｜、｜）｜)]'))] = count - 1

        else:
            for i in range(len(text_query_df_font_group)):
                font_size = text_query_df_font_group.iloc[i]['font-size']
                font_name = text_query_df_font_group.iloc[i]['font-name']
                font_weight = text_query_df_font_group.iloc[i]['font-weight']
                font_size_asian = text_query_df_font_group.iloc[i]['font-size-asian']
                font_name_asian = text_query_df_font_group.iloc[i]['font-name-asian']
                font_style = text_query_df_font_group.iloc[i]['font-style']
                count = text_query_df_font_group.iloc[i]['count']
                # 满足font分组的元素属于分组大小为count,那么font_count = count
                text_query_df.loc[(text_query_df['font-size'] == font_size) &
                                            (text_query_df['font-name'] == font_name) &
                                            (text_query_df['font-weight'] == font_weight) &
                                            (text_query_df['font-size-asian'] == font_size_asian) &
                                            (text_query_df['font-name-asian'] == font_name_asian) &
                                            (text_query_df['font-style'] == font_style),'font_group'] = count

        pair_font_flag = False

        if len(text_query_df[text_query_df['pair']!='no']) == max_font_group:
            text_query_title_df = text_query_df[text_query_df.pair.str.match('^\d_0')]
            text_query_content_df = text_query_df[text_query_df.pair.str.match('^\d_1')]
            text_query_no_df = text_query_df[text_query_df.pair.str.match('no')]

            text_query_df_max_font_group = text_query_df_font_group[text_query_df_font_group['count'] == max_font_group]
            text_query_df_other_font_group = text_query_df_font_group[text_query_df_font_group['count'] != max_font_group]

            max_font_group = max_font_group / 2
            text_query_df_max_font_group = text_query_df_max_font_group.append(text_query_df_max_font_group,ignore_index = True)
            text_query_df_max_font_group['count'] = max_font_group
            font_size = text_query_df_max_font_group.iloc[0]['font-size']
            font_size_asian = text_query_df_max_font_group.iloc[0]['font-size-asian']
            title_font_size = str(int(font_size.split('pt')[0]) + 1) + 'pt'
            title_font_size_asian = str(int(font_size_asian.split('pt')[0]) + 1) + 'pt'
            text_query_df_max_font_group.loc[0,'font-size'] = title_font_size
            text_query_df_max_font_group.loc[0, 'font-size-asian'] = title_font_size_asian
            text_query_df_font_group = text_query_df_max_font_group.append(text_query_df_other_font_group,ignore_index = True)
            text_query_title_df.reset_index(inplace=True)
            for i in range(len(text_query_title_df)):
                text_query_title_df.loc[i,'font-size'] = title_font_size
                text_query_title_df.loc[i, 'font-size-asian'] = title_font_size_asian

            text_query_title_df = text_query_title_df.drop(['index'], axis=1)
            text_query_df = text_query_title_df.append(text_query_content_df,ignore_index = True)
            text_query_df = text_query_df.append(text_query_no_df,ignore_index = True)



            for i in range(len(text_query_df_font_group)):
                font_size = text_query_df_font_group.iloc[i]['font-size']
                font_name = text_query_df_font_group.iloc[i]['font-name']
                font_weight = text_query_df_font_group.iloc[i]['font-weight']
                font_size_asian = text_query_df_font_group.iloc[i]['font-size-asian']
                font_name_asian = text_query_df_font_group.iloc[i]['font-name-asian']
                font_style = text_query_df_font_group.iloc[i]['font-style']
                count = text_query_df_font_group.iloc[i]['count']
                # 满足font分组的元素属于分组大小为count,那么font_count = count
                text_query_df['font_group'][(text_query_df['font-size'] == font_size) &
                                            (text_query_df['font-name'] == font_name) &
                                            (text_query_df['font-weight'] == font_weight) &
                                            (text_query_df['font-size-asian'] == font_size_asian) &
                                            (text_query_df['font-name-asian'] == font_name_asian) &
                                            (text_query_df['font-style'] == font_style)] = count


            pair_font_flag = True



            print('hello')





    if 'shape' in subject_class:
        shape_query_df = query_all_info_df[query_all_info_df['subject'] == 'shape']
        shape_query_df.loc[:,'graphic_area_group'] = 1
        shape_class = list(shape_query_df['class'].unique())
        if 'GraphicObjectShape' in shape_class:
            graphic_len = len(shape_query_df[shape_query_df['class'] == 'GraphicObjectShape'])
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']
            graphic_query_df_area_group = graphic_query_df.groupby(['shape_area'], as_index=False)['class'].count()
            graphic_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)

            for i in range(len(graphic_query_df_area_group)):
                area = graphic_query_df_area_group.iloc[i]['shape_area']
                count = graphic_query_df_area_group.iloc[i]['count']
                shape_query_df.loc[(shape_query_df['shape_area'] == area)
                                                     & (shape_query_df['class'] == 'GraphicObjectShape'),'graphic_area_group'] = count

            max_graphic_group = max(graphic_query_df_area_group['count'])

    # ==================================================
    # 元素对比
    # ==================================================
    text_i_to_j = {}
    # 这里的 adjust 表示具体的属性可以调整
    text_i_to_j_adjust = {'input':[],'output':[]}
    shape_i_to_j = {}
    # 这里的 adjust 表示具体的属性可以调整
    shape_i_to_j_adjust = {'input':[],'output':[]}
    best_json = {}
    shapes_json = {}
    texts_json = {}
    input_shape_list = []
    output_shape_list = []
    input_text_list = []
    output_text_list = []
    # ==================================================
    # 最佳匹配
    # ==================================================
    best_ppt_file_name = recommend_df.iloc[0]['file_name']
    file234_db = best_ppt_file_name

    # ==================================================
    # 数据迁移，主要是为了后期的对比
    # ==================================================
    os.makedirs(os.path.join(root_path,version,'elements'), exist_ok=True)
    os.makedirs(os.path.join(root_path,version,'elements', file1), exist_ok=True)
    os.makedirs(os.path.join(root_path,version,'elements', file1, file1_db), exist_ok=True)
    os.makedirs(os.path.join(root_path,version,'elements', file1, file1_db,file2), exist_ok=True)
    os.makedirs(os.path.join(root_path,version,'elements', file1, file1_db,file2,file3), exist_ok=True)
    os.makedirs(os.path.join(root_path,version,'elements', file1, file1_db,file2,file3,file4.replace('.', '_')), exist_ok=True)

    shutil.copy(os.path.join(root_path,version, 'pic', 'index', file1, file2, file3, file4 + '.png'),
                os.path.join(root_path,version,'elements', file1, file1_db, file2,file3,file4.replace('.', '_'), file4 + '_index.png'))
    shutil.copy(os.path.join(root_path,version, 'pic', 'text', file1, file2, file3, file4 + '.png'),
                os.path.join(root_path,version,'elements', file1, file1_db, file2,file3,file4.replace('.', '_'), file4 + '_text.png'))
    shutil.copy(os.path.join(root_path,version, 'data_ppt', file1, file2, file3, file4),
                os.path.join(root_path,version,'elements', file1, file1_db, file2,file3,file4.replace('.', '_'), file4))


    all_best_name_list = [os.path.join(file1_db, file234_db)]
    for key, one_best_name in enumerate(all_best_name_list):
        shutil.copy(os.path.join(root_path,version, 'pic', 'index', one_best_name + '.png'),
                    os.path.join(root_path,version,'elements', file1, file1_db, file2,file3,file4.replace('.', '_'),
                                 file4 + '_index' + str(key) + '.png'))
        shutil.copy(os.path.join(root_path,version, 'pic', 'text', one_best_name + '.png'),
                    os.path.join(root_path,version,'elements', file1, file1_db, file2,file3,file4.replace('.', '_'),
                                 file4 + '_text' + str(key) + '.png'))
        shutil.copy(os.path.join(root_path,version, 'data_ppt', one_best_name),
                    os.path.join(root_path,version,'elements', file1, file1_db, file2,file3,file4.replace('.', '_'), file4 + str(key)))


    # ==================================================
    # 元素匹配
    # ==================================================

    best_ppt = all_db[all_db['file_name'] == file234_db]
    best_ppt_stat = db_df[db_df['file_name'] == file234_db]
    best_ppt_subject = list(best_ppt['subject'].unique())
    if text_len == 0:
        print('no text')

    if text_len > 0 and 'texts' in best_ppt_subject:
        deal_query_key = []
        deal_best_key = []
        text_best_ppt = best_ppt[best_ppt['subject'] == 'texts']
        # 处理table
        if table_len != 0:
            input_text_list,output_text_list,deal_query_key,deal_best_key,text_i_to_j \
                = deal_table_v4(text_best_ppt,text_query_df,
                             input_text_list,output_text_list,deal_query_key,deal_best_key,text_i_to_j,
                             table_len)
        # 处理title

        text_best_ppt, text_query_df, \
        input_text_list, output_text_list, \
        deal_query_key, deal_best_key,\
        text_i_to_j,text_i_to_j_adjust = deal_title_v4(text_best_ppt, text_query_df,
                                 input_text_list, output_text_list,
                                 deal_query_key, deal_best_key,
                                 text_i_to_j,text_i_to_j_adjust,
                                 title_combine_len,second_flag,best_ppt_stat)

        # 处理成对出现的text
        # 处理area_group
        text_best_ppt.loc[:,'area_group'] = 1
        text_best_df_area_group = text_best_ppt.groupby(['shape_area'], as_index=False)['class'].count()
        text_best_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        text_best_df_area_group = text_best_df_area_group.sort_values(['count', 'shape_area'], ascending=[False, False])
        for i in range(len(text_best_df_area_group)):
            area = text_best_df_area_group.iloc[i]['shape_area']
            count = text_best_df_area_group.iloc[i]['count']
            text_best_ppt.loc[text_best_ppt['shape_area'] == area,'area_group'] = count
        # 处理font_group
        text_best_ppt.loc[:,'font_group'] = 1
        text_best_df_font_group = text_best_ppt[text_best_ppt['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                                      'font-name',
                                                                                                      'font-weight',
                                                                                                      'font-size-asian',
                                                                                                      'font-name-asian',
                                                                                                      'font-style'],
                                                                                                     as_index=False)[
            'class'].count()
        text_best_df_font_group.rename(columns={'class': 'count'}, inplace=True)
        text_best_df_font_group = text_best_df_font_group.sort_values(['count', 'font-size'],
                                                                        ascending=[False, False])
        for i in range(len(text_best_df_font_group)):
            font_size = text_best_df_font_group.iloc[i]['font-size']
            font_name = text_best_df_font_group.iloc[i]['font-name']
            font_weight = text_best_df_font_group.iloc[i]['font-weight']
            font_size_asian = text_best_df_font_group.iloc[i]['font-size-asian']
            font_name_asian = text_best_df_font_group.iloc[i]['font-name-asian']
            font_style = text_best_df_font_group.iloc[i]['font-style']
            count = text_best_df_font_group.iloc[i]['count']
            # 满足font分组的元素属于分组大小为count,那么font_count = count
            text_best_ppt.loc[(text_best_ppt['font-size'] == font_size) &
                                        (text_best_ppt['font-name'] == font_name) &
                                        (text_best_ppt['font-weight'] == font_weight) &
                                        (text_best_ppt['font-size-asian'] == font_size_asian) &
                                        (text_best_ppt['font-name-asian'] == font_name_asian) &
                                        (text_best_ppt['font-style'] == font_style),'font_group'] = count

        input_text_list, \
        output_text_list, \
        deal_query_key, \
        deal_best_key, \
        text_i_to_j,\
        text_i_to_j_adjust\
            = deal_text_group_v4(text_best_ppt,text_query_df,
                    input_text_list,output_text_list,
                    deal_query_key,deal_best_key,
                    text_i_to_j,text_i_to_j_adjust,
                    max_text_group,max_font_group,
                    title_len,
                    second_flag,
                    pair_font_flag,
                    text_best_df_area_group,text_best_df_font_group,text_query_df_area_group,text_query_df_font_group,
                                rgraph_type)


    ###################################################3
    if shape_len == 0:
        print('no shape')

    if shape_len > 0 and 'shape' in best_ppt_subject:
        deal_shape_query_key = []
        deal_shape_best_key = []
        shape_best_ppt = best_ppt[best_ppt['subject'] == 'shape']

        # 处理 chart
        if chart_len != 0:
            input_shape_list,output_shape_list,\
            deal_shape_query_key,deal_shape_best_key,\
            shape_i_to_j = deal_chart(shape_best_ppt,shape_query_df,
                                      input_shape_list,output_shape_list,
                                      deal_shape_query_key,deal_shape_best_key,
                                      shape_i_to_j,chart_len)

        # 处理graphic
        if graphic_len != 0:
            input_shape_list, output_shape_list, \
            deal_shape_query_key, deal_shape_best_key, \
            shape_i_to_j,shape_i_to_j_adjust = \
                deal_graphic(shape_best_ppt, shape_query_df,
                             input_shape_list, output_shape_list,
                             deal_shape_query_key,deal_shape_best_key,
                             shape_i_to_j, shape_i_to_j_adjust,
                             graphic_query_df_area_group)

    # ==================================================
    # json保存
    # ==================================================
    map_json = {}
    map_json['text'] = text_i_to_j_adjust
    map_json['image'] = shape_i_to_j_adjust
    result_json = {}
    result_json['input'] = os.path.join(file2, file3, file4).replace('.json', '')
    result_json['output'] = [best_ppt_file_name]

    shapes_json['input_shape'] = input_shape_list
    shapes_json['output_shape'] = output_shape_list

    texts_json['input_text'] = input_text_list
    texts_json['output_text'] = output_text_list

    best_json['shape'] = shapes_json
    best_json['text'] = texts_json

    result_json['match'] = [best_json]

    result = json.dumps(result_json, ensure_ascii=False)
    os.makedirs(os.path.join(root_path,version,'json_match'), exist_ok=True)
    os.makedirs(os.path.join(root_path,version,'json_match', file1), exist_ok=True)
    os.makedirs(os.path.join(root_path,version,'json_match', file1, file2), exist_ok=True)
    os.makedirs(os.path.join(root_path,version,'json_match', file1, file2, file3), exist_ok=True)
    with open(os.path.join(root_path,version,'json_match', file1, file2, file3, file4), 'w') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=4)

    print(str(result).replace('\'', '\"'))

    with open(os.path.join(root_path,version,'elements', file1, file1_db, file2,file3, file4.replace('.', '_'), file4 + '.txt'), 'w') as f:
        # f.writelines('第一次匹配到了' + str(first_num) + '个'+ '\n')
        # f.writelines('第二次匹配到了' + str(second_num) + '个' + '\n')
        for index, one_name in enumerate(all_best_name_list):
            if one_name == '':
                break
            f.writelines(str(index + 1) + '  ' + one_name + '\n')
        f.writelines('best_ppt\n')
        f.writelines('text i to j\n')
        f.writelines(str(text_i_to_j) + '\n')
        f.writelines('shape i to j' + '\n')
        f.writelines(str(shape_i_to_j) + '\n')

    print(text_i_to_j_adjust)
    print(shape_i_to_j_adjust)



def deal_elements_match_v4_server(query_df,query_all_info_df,recommend_df,
                        second_flag,
                        root_path,db_path,version,file4,
                        file1_db,query_labels,db_df,all_db):
    '''
    元素匹配
    :param query_df:
    :param query_all_info_df:
    :param recommend_df:
    :param second_flag:
    :param root_path:
    :param version:
    :param file1:
    :param file2:
    :param file3:
    :param file4:
    :param file1_db:
    :return:
    '''
    # ==================================================
    # 统计数据
    # ==================================================
    rgraph_type = query_labels['rgraph_type']
    max_font_group = query_df.iloc[0]['max_font_group']
    max_text_group = query_df.iloc[0]['max_text_group']
    text_len = query_df.iloc[0]['text_num']
    shape_len = query_df.iloc[0]['shape_num']
    outline_len = query_df.iloc[0]['outline_num']
    title_len = query_df.iloc[0]['title_num']
    table_len = query_df.iloc[0]['table_num']
    chart_len = query_df.iloc[0]['chart_num']
    graphic_len = query_df.iloc[0]['graphic_num']
    new_title_len = query_df.iloc[0]['new_title_num']
    font_size_estimate_title_num = query_df.iloc[0]['font_size_estimate_title_num']
    new_title = []
    # ==================================================
    # 查询数据预处理
    # ==================================================
    subject_class = list(query_all_info_df['subject'].unique())
    if 'texts' in subject_class:
        text_query_df = query_all_info_df[query_all_info_df['subject'] == 'texts']

        if title_len == 0 and outline_len == 0 and font_size_estimate_title_num == 1:
            text_query_df.loc[text_query_df['font_size_estimate_title'] == 1, 'new_class'] = 'title'
            text_query_df.loc[text_query_df['font_size_estimate_title'] == 1, 'class'] = 'TitleTextShape'

        elif title_len == 0 and outline_len == 0 and font_size_estimate_title_num == 0:

            # 制造新的title
            new_title = []
            for i in range(text_len):
                one_text = text_query_df[i:i + 1]
                one_text_x = one_text.iloc[0]['shape_x']
                one_text_y = one_text.iloc[0]['shape_y']
                one_text_w = one_text.iloc[0]['shape_width']
                one_text_h = one_text.iloc[0]['shape_height']
                one_w = one_text.iloc[0]['width']
                one_h = one_text.iloc[0]['height']

                if one_text_y + one_text_h < one_h / 5:
                    new_title.append(i)

            if len(new_title) == 1:
                new_title_len = 1
                text_query_df.loc[new_title[0], 'new_class'] = 'title'
                text_query_df.loc[new_title[0], 'class'] = 'TitleTextShape'
            else:
                new_title_len = 0

        if title_len > 1:
            title_text_query_df = text_query_df[text_query_df['class'] == 'TitleTextShape']

            title_text_query_df = title_text_query_df.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
            top_key = title_text_query_df.iloc[0]['key']
            all_key = list(title_text_query_df['key'].unique())
            all_key.remove(top_key)
            for key in all_key:
                text_query_df['class'][text_query_df['key'] == key] = 'TextShape'

        title_combine_len = 0
        if title_len == 1:
            title_combine_len = 1
        elif new_title_len == 1:
            title_combine_len = 1
        elif font_size_estimate_title_num == 1:
            title_combine_len = 1

        text_query_df_area_group = \
        text_query_df[text_query_df['class'] != 'TitleTextShape'].groupby(['shape_area'], as_index=False)[
            'class'].count()

        text_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)

        # 将area的分组结果对每一个元素赋值
        text_query_df.loc[:,'area_group'] = 1
        if len(text_query_df_area_group) == 0:
            max_text_group = 1
        else:
            max_text_group = max(text_query_df_area_group['count'])

        if [5,0] == rgraph_type:
            max_text_group = max_text_group - 1
            for i in range(len(text_query_df_area_group)):
                area = text_query_df_area_group.iloc[i]['shape_area']
                count = text_query_df_area_group.iloc[i]['count']
                text_query_df_area_group.loc[i,'count'] = count - 1
                text_query_df['area_group'][(text_query_df['shape_area'] == area)
                                            & (text_query_df.content.str.match('^\d{1,2}[\\.|\\-|\\*|\\,|，｜、｜）｜)]'))] = count - 1
        else:
            for i in range(len(text_query_df_area_group)):
                area = text_query_df_area_group.iloc[i]['shape_area']
                count = text_query_df_area_group.iloc[i]['count']
                # text_query_df['area_group'][text_query_df['shape_area'] == area] = count
                text_query_df.loc[text_query_df['shape_area'] == area,'area_group'] = count


        # 字体
        text_query_df_font_group = text_query_df[text_query_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                                      'font-name',
                                                                                                      'font-weight',
                                                                                                      'font-size-asian',
                                                                                                      'font-name-asian',
                                                                                                      'font-style'],
                                                                                                     as_index=False)[
            'class'].count()
        text_query_df_font_group.rename(columns={'class': 'count'}, inplace=True)

        text_query_df.loc[:,'font_group'] = 1

        if len(text_query_df_font_group) == 0:
            max_font_group = 1
        else:
            max_font_group = max(text_query_df_font_group['count'])


        # 针对总分
        if [5,0] == rgraph_type:
            max_font_group = max_font_group - 1
            for i in range(len(text_query_df_font_group)):
                font_size = text_query_df_font_group.iloc[i]['font-size']
                font_name = text_query_df_font_group.iloc[i]['font-name']
                font_weight = text_query_df_font_group.iloc[i]['font-weight']
                font_size_asian = text_query_df_font_group.iloc[i]['font-size-asian']
                font_name_asian = text_query_df_font_group.iloc[i]['font-name-asian']
                font_style = text_query_df_font_group.iloc[i]['font-style']
                count = text_query_df_font_group.iloc[i]['count']
                text_query_df_font_group.loc[i, 'count'] = count - 1
                # 满足font分组的元素属于分组大小为count,那么font_count = count
                text_query_df['font_group'][(text_query_df['font-size'] == font_size) &
                                            (text_query_df['font-name'] == font_name) &
                                            (text_query_df['font-weight'] == font_weight) &
                                            (text_query_df['font-size-asian'] == font_size_asian) &
                                            (text_query_df['font-name-asian'] == font_name_asian) &
                                            (text_query_df['font-style'] == font_style) &
                                            (text_query_df.content.str.match('^\d{1,2}[\\.|\\-|\\*|\\,|，｜、｜）｜)]'))] = count - 1

        else:
            for i in range(len(text_query_df_font_group)):
                font_size = text_query_df_font_group.iloc[i]['font-size']
                font_name = text_query_df_font_group.iloc[i]['font-name']
                font_weight = text_query_df_font_group.iloc[i]['font-weight']
                font_size_asian = text_query_df_font_group.iloc[i]['font-size-asian']
                font_name_asian = text_query_df_font_group.iloc[i]['font-name-asian']
                font_style = text_query_df_font_group.iloc[i]['font-style']
                count = text_query_df_font_group.iloc[i]['count']
                # 满足font分组的元素属于分组大小为count,那么font_count = count
                text_query_df.loc[(text_query_df['font-size'] == font_size) &
                                            (text_query_df['font-name'] == font_name) &
                                            (text_query_df['font-weight'] == font_weight) &
                                            (text_query_df['font-size-asian'] == font_size_asian) &
                                            (text_query_df['font-name-asian'] == font_name_asian) &
                                            (text_query_df['font-style'] == font_style),'font_group'] = count

        pair_font_flag = False

        if len(text_query_df[text_query_df['pair']!='no']) == max_font_group:
            text_query_title_df = text_query_df[text_query_df.pair.str.match('^\d_0')]
            text_query_content_df = text_query_df[text_query_df.pair.str.match('^\d_1')]
            text_query_no_df = text_query_df[text_query_df.pair.str.match('no')]

            text_query_df_max_font_group = text_query_df_font_group[text_query_df_font_group['count'] == max_font_group]
            text_query_df_other_font_group = text_query_df_font_group[text_query_df_font_group['count'] != max_font_group]

            max_font_group = max_font_group / 2
            text_query_df_max_font_group = text_query_df_max_font_group.append(text_query_df_max_font_group,ignore_index = True)
            text_query_df_max_font_group['count'] = max_font_group
            font_size = text_query_df_max_font_group.iloc[0]['font-size']
            font_size_asian = text_query_df_max_font_group.iloc[0]['font-size-asian']
            title_font_size = str(int(font_size.split('pt')[0]) + 1) + 'pt'
            title_font_size_asian = str(int(font_size_asian.split('pt')[0]) + 1) + 'pt'
            text_query_df_max_font_group.loc[0,'font-size'] = title_font_size
            text_query_df_max_font_group.loc[0, 'font-size-asian'] = title_font_size_asian
            text_query_df_font_group = text_query_df_max_font_group.append(text_query_df_other_font_group,ignore_index = True)
            text_query_title_df.reset_index(inplace=True)
            for i in range(len(text_query_title_df)):
                text_query_title_df.loc[i,'font-size'] = title_font_size
                text_query_title_df.loc[i, 'font-size-asian'] = title_font_size_asian

            text_query_title_df = text_query_title_df.drop(['index'], axis=1)
            text_query_df = text_query_title_df.append(text_query_content_df,ignore_index = True)
            text_query_df = text_query_df.append(text_query_no_df,ignore_index = True)



            for i in range(len(text_query_df_font_group)):
                font_size = text_query_df_font_group.iloc[i]['font-size']
                font_name = text_query_df_font_group.iloc[i]['font-name']
                font_weight = text_query_df_font_group.iloc[i]['font-weight']
                font_size_asian = text_query_df_font_group.iloc[i]['font-size-asian']
                font_name_asian = text_query_df_font_group.iloc[i]['font-name-asian']
                font_style = text_query_df_font_group.iloc[i]['font-style']
                count = text_query_df_font_group.iloc[i]['count']
                # 满足font分组的元素属于分组大小为count,那么font_count = count
                text_query_df['font_group'][(text_query_df['font-size'] == font_size) &
                                            (text_query_df['font-name'] == font_name) &
                                            (text_query_df['font-weight'] == font_weight) &
                                            (text_query_df['font-size-asian'] == font_size_asian) &
                                            (text_query_df['font-name-asian'] == font_name_asian) &
                                            (text_query_df['font-style'] == font_style)] = count


            pair_font_flag = True



            print('hello')





    if 'shape' in subject_class:
        shape_query_df = query_all_info_df[query_all_info_df['subject'] == 'shape']
        shape_query_df.loc[:,'graphic_area_group'] = 1
        shape_class = list(shape_query_df['class'].unique())
        if 'GraphicObjectShape' in shape_class:
            graphic_len = len(shape_query_df[shape_query_df['class'] == 'GraphicObjectShape'])
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']
            graphic_query_df_area_group = graphic_query_df.groupby(['shape_area'], as_index=False)['class'].count()
            graphic_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)

            for i in range(len(graphic_query_df_area_group)):
                area = graphic_query_df_area_group.iloc[i]['shape_area']
                count = graphic_query_df_area_group.iloc[i]['count']
                shape_query_df.loc[(shape_query_df['shape_area'] == area)
                                                     & (shape_query_df['class'] == 'GraphicObjectShape'),'graphic_area_group'] = count

            max_graphic_group = max(graphic_query_df_area_group['count'])

    # ==================================================
    # 元素对比
    # ==================================================
    text_i_to_j = {}
    # 这里的 adjust 表示具体的属性可以调整
    text_i_to_j_adjust = {'input':[],'output':[]}
    shape_i_to_j = {}
    # 这里的 adjust 表示具体的属性可以调整
    shape_i_to_j_adjust = {'input':[],'output':[]}
    best_json = {}
    shapes_json = {}
    texts_json = {}
    input_shape_list = []
    output_shape_list = []
    input_text_list = []
    output_text_list = []
    # ==================================================
    # 最佳匹配
    # ==================================================
    best_ppt_file_name = recommend_df.iloc[0]['file_name']
    file234_db = best_ppt_file_name

    # ==================================================
    # 数据迁移，主要是为了后期的对比
    # ==================================================
    os.makedirs(os.path.join(root_path,'elements'), exist_ok=True)
    os.makedirs(os.path.join(root_path,'elements', file1_db), exist_ok=True)
    os.makedirs(os.path.join(root_path,'elements', file1_db,file4.replace('.', '_')), exist_ok=True)

    shutil.copy(os.path.join(root_path, 'pic', 'index', file4 + '.png'),
                os.path.join(root_path,'elements',file1_db,file4.replace('.', '_'), file4 + '_index.png'))
    shutil.copy(os.path.join(root_path, 'pic', 'text', file4 + '.png'),
                os.path.join(root_path,'elements',  file1_db ,file4.replace('.', '_'), file4 + '_text.png'))
    shutil.copy(os.path.join(root_path, 'data_ppt', file4),
                os.path.join(root_path,'elements', file1_db,file4.replace('.', '_'), file4))


    all_best_name_list = [os.path.join(file1_db, file234_db)]
    for key, one_best_name in enumerate(all_best_name_list):
        shutil.copy(os.path.join(db_path,version, 'pic', 'index', one_best_name + '.png'),
                    os.path.join(root_path,'elements', file1_db, file4.replace('.', '_'),
                                 file4 + '_index' + str(key) + '.png'))
        shutil.copy(os.path.join(db_path,version, 'pic', 'text', one_best_name + '.png'),
                    os.path.join(root_path,'elements', file1_db, file4.replace('.', '_'),
                                 file4 + '_text' + str(key) + '.png'))
        shutil.copy(os.path.join(db_path,version, 'data_ppt', one_best_name),
                    os.path.join(root_path,'elements', file1_db, file4.replace('.', '_'), file4 + str(key)))


    # ==================================================
    # 元素匹配
    # ==================================================

    best_ppt = all_db[all_db['file_name'] == file234_db]
    best_ppt_stat = db_df[db_df['file_name'] == file234_db]
    best_ppt_subject = list(best_ppt['subject'].unique())
    if text_len == 0:
        print('no text')

    if text_len > 0 and 'texts' in best_ppt_subject:
        deal_query_key = []
        deal_best_key = []
        text_best_ppt = best_ppt[best_ppt['subject'] == 'texts']
        # 处理table
        if table_len != 0:
            input_text_list,output_text_list,deal_query_key,deal_best_key,text_i_to_j \
                = deal_table_v4(text_best_ppt,text_query_df,
                             input_text_list,output_text_list,deal_query_key,deal_best_key,text_i_to_j,
                             table_len)
        # 处理title

        text_best_ppt, text_query_df, \
        input_text_list, output_text_list, \
        deal_query_key, deal_best_key,\
        text_i_to_j,text_i_to_j_adjust = deal_title_v4(text_best_ppt, text_query_df,
                                 input_text_list, output_text_list,
                                 deal_query_key, deal_best_key,
                                 text_i_to_j,text_i_to_j_adjust,
                                 title_combine_len,second_flag,best_ppt_stat)

        # 处理成对出现的text
        # 处理area_group
        text_best_ppt.loc[:,'area_group'] = 1
        text_best_df_area_group = text_best_ppt.groupby(['shape_area'], as_index=False)['class'].count()
        text_best_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        text_best_df_area_group = text_best_df_area_group.sort_values(['count', 'shape_area'], ascending=[False, False])
        for i in range(len(text_best_df_area_group)):
            area = text_best_df_area_group.iloc[i]['shape_area']
            count = text_best_df_area_group.iloc[i]['count']
            text_best_ppt.loc[text_best_ppt['shape_area'] == area,'area_group'] = count
        # 处理font_group
        text_best_ppt.loc[:,'font_group'] = 1
        text_best_df_font_group = text_best_ppt[text_best_ppt['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                                      'font-name',
                                                                                                      'font-weight',
                                                                                                      'font-size-asian',
                                                                                                      'font-name-asian',
                                                                                                      'font-style'],
                                                                                                     as_index=False)[
            'class'].count()
        text_best_df_font_group.rename(columns={'class': 'count'}, inplace=True)
        text_best_df_font_group = text_best_df_font_group.sort_values(['count', 'font-size'],
                                                                        ascending=[False, False])
        for i in range(len(text_best_df_font_group)):
            font_size = text_best_df_font_group.iloc[i]['font-size']
            font_name = text_best_df_font_group.iloc[i]['font-name']
            font_weight = text_best_df_font_group.iloc[i]['font-weight']
            font_size_asian = text_best_df_font_group.iloc[i]['font-size-asian']
            font_name_asian = text_best_df_font_group.iloc[i]['font-name-asian']
            font_style = text_best_df_font_group.iloc[i]['font-style']
            count = text_best_df_font_group.iloc[i]['count']
            # 满足font分组的元素属于分组大小为count,那么font_count = count
            text_best_ppt.loc[(text_best_ppt['font-size'] == font_size) &
                                        (text_best_ppt['font-name'] == font_name) &
                                        (text_best_ppt['font-weight'] == font_weight) &
                                        (text_best_ppt['font-size-asian'] == font_size_asian) &
                                        (text_best_ppt['font-name-asian'] == font_name_asian) &
                                        (text_best_ppt['font-style'] == font_style),'font_group'] = count

        input_text_list, \
        output_text_list, \
        deal_query_key, \
        deal_best_key, \
        text_i_to_j,\
        text_i_to_j_adjust\
            = deal_text_group_v4(text_best_ppt,text_query_df,
                    input_text_list,output_text_list,
                    deal_query_key,deal_best_key,
                    text_i_to_j,text_i_to_j_adjust,
                    max_text_group,max_font_group,
                    title_len,
                    second_flag,
                    pair_font_flag,
                    text_best_df_area_group,text_best_df_font_group,text_query_df_area_group,text_query_df_font_group,
                                rgraph_type)


    ###################################################3
    if shape_len == 0:
        print('no shape')

    if shape_len > 0 and 'shape' in best_ppt_subject:
        deal_shape_query_key = []
        deal_shape_best_key = []
        shape_best_ppt = best_ppt[best_ppt['subject'] == 'shape']

        # 处理 chart
        if chart_len != 0:
            input_shape_list,output_shape_list,\
            deal_shape_query_key,deal_shape_best_key,\
            shape_i_to_j = deal_chart(shape_best_ppt,shape_query_df,
                                      input_shape_list,output_shape_list,
                                      deal_shape_query_key,deal_shape_best_key,
                                      shape_i_to_j,chart_len)

        # 处理graphic
        if graphic_len != 0:
            input_shape_list, output_shape_list, \
            deal_shape_query_key, deal_shape_best_key, \
            shape_i_to_j,shape_i_to_j_adjust = \
                deal_graphic(shape_best_ppt, shape_query_df,
                             input_shape_list, output_shape_list,
                             deal_shape_query_key,deal_shape_best_key,
                             shape_i_to_j, shape_i_to_j_adjust,
                             graphic_query_df_area_group)

    # ==================================================
    # json保存
    # ==================================================
    map_json = {}
    map_json['text'] = text_i_to_j_adjust
    map_json['image'] = shape_i_to_j_adjust
    result_json = {}
    result_json['input'] = os.path.join(file4).replace('.json', '')
    result_json['output'] = [best_ppt_file_name]

    shapes_json['input_shape'] = input_shape_list
    shapes_json['output_shape'] = output_shape_list

    texts_json['input_text'] = input_text_list
    texts_json['output_text'] = output_text_list

    best_json['shape'] = shapes_json
    best_json['text'] = texts_json

    result_json['match'] = [best_json]

    result = json.dumps(result_json, ensure_ascii=False)
    os.makedirs(os.path.join(root_path,'json_match'), exist_ok=True)

    with open(os.path.join(root_path,'json_match',  file4), 'w') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=4)

    print(str(result).replace('\'', '\"'))

    with open(os.path.join(root_path,'elements', file1_db, file4.replace('.', '_'), file4 + '.txt'), 'w') as f:
        # f.writelines('第一次匹配到了' + str(first_num) + '个'+ '\n')
        # f.writelines('第二次匹配到了' + str(second_num) + '个' + '\n')
        for index, one_name in enumerate(all_best_name_list):
            if one_name == '':
                break
            f.writelines(str(index + 1) + '  ' + one_name + '\n')
        f.writelines('best_ppt\n')
        f.writelines('text i to j\n')
        f.writelines(str(text_i_to_j) + '\n')
        f.writelines('shape i to j' + '\n')
        f.writelines(str(shape_i_to_j) + '\n')

    print(text_i_to_j_adjust)
    print(shape_i_to_j_adjust)

    return map_json





