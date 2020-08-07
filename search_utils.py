import pandas as pd
import os
import random
def get_best_match_ppt_v3(query_df,query_all_info_df,db_df,query_labels,rg_flag):
    '''
    获取最佳匹配ppt,其中tuwen_layout，text_type需要计算得到，目前未完成
    v2版本修改了title，因为发现新版的ppt几乎没有title，所以这里面用new_title_len代替title,
    其中new_title_len表示的是estimate_title只有一个的ppt，也就是estimate_title = 1时，new_title_len=1
    :param query_df:
    :param query_all_info_df:
    :param db_df:
    :return:
    '''
    # tuwen_layout,text_type 是需要后面优化，得到该数据
    tuwen_layout = query_labels['tuwen_layout']
    text_type = query_labels['text_type']
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
    max_graphic_group = query_df.iloc[0]['max_graphic_group']
    subject_class = list(query_all_info_df['subject'].unique())
    ppt_width = query_all_info_df.iloc[0]['width']
    ppt_height = query_all_info_df.iloc[0]['height']

    if 'texts' in subject_class:
        text_query_df = query_all_info_df[query_all_info_df['subject'] == 'texts']
    if 'shape' in subject_class:
        shape_query_df = query_all_info_df[query_all_info_df['subject'] == 'shape']
        shape_class = list(shape_query_df['class'].unique())
        if 'GraphicObjectShape' in shape_class:
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']

    if graphic_len == 1 and 'shape' in subject_class and 'GraphicObjectShape' in shape_class and \
            graphic_query_df.iloc[0]['shape_area'] < (ppt_height * ppt_width) / 5:
        tuwen_layout = 1

    outline_len_m = outline_len
    title_len_m = title_len
    if title_len > 0:
        outline_len_m = 0

    if title_len == 0 and outline_len == 0 and new_title_len == 1:
        title_len_m = 1

    title_combine_len = 0
    if title_len == 1:
        title_combine_len = 1
    elif new_title_len == 1:
        title_combine_len = 1

    if rg_flag:
        # 这里我们彻底放弃 outliner 作为 title
        if max_font_group < max_text_group + 1:
            ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                  | (db_df['new_title_num'] == title_combine_len))
                                  & (db_df['outline_num'] == outline_len_m)
                                  & (db_df['max_text_group'] == max_text_group)
                                  & (db_df['table_num'] == table_len)
                                  & (db_df['chart_num'] == chart_len)
                                  & (db_df['graphic_num'] == graphic_len)
                                  & (db_df['max_graphic_group'] == max_graphic_group)
                                  & (db_df['tuwen_layout'] == tuwen_layout)
                                  & (db_df['text_type'] == text_type)
                                  & (db_df['rgraph_type'] == rgraph_type)
                                  ]
        else:
            ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                  | (db_df['new_title_num'] == title_combine_len))
                                  & (db_df['outline_num'] == outline_len_m)
                                  & (db_df['max_text_group'] == max_font_group)
                                  & (db_df['table_num'] == table_len)
                                  & (db_df['chart_num'] == chart_len)
                                  & (db_df['graphic_num'] == graphic_len)
                                  & (db_df['max_graphic_group'] == max_graphic_group)
                                  & (db_df['tuwen_layout'] == tuwen_layout)
                                  & (db_df['text_type'] == text_type)
                                  & (db_df['rgraph_type'] == rgraph_type)
                                  ]
    else:
        if max_font_group < max_text_group + 1:
            ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                  | (db_df['new_title_num'] == title_combine_len))
                                  & (db_df['outline_num'] == outline_len_m)
                                  & (db_df['max_text_group'] == max_text_group)
                                  & (db_df['table_num'] == table_len)
                                  & (db_df['chart_num'] == chart_len)
                                  & (db_df['graphic_num'] == graphic_len)
                                  & (db_df['max_graphic_group'] == max_graphic_group)
                                  & (db_df['tuwen_layout'] == tuwen_layout)
                                  & (db_df['text_type'] == text_type)
                                  ]
        else:
            ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                  | (db_df['new_title_num'] == title_combine_len))
                                  & (db_df['outline_num'] == outline_len_m)
                                  & (db_df['max_text_group'] == max_font_group)
                                  & (db_df['table_num'] == table_len)
                                  & (db_df['chart_num'] == chart_len)
                                  & (db_df['graphic_num'] == graphic_len)
                                  & (db_df['max_graphic_group'] == max_graphic_group)
                                  & (db_df['tuwen_layout'] == tuwen_layout)
                                  & (db_df['text_type'] == text_type)
                                  ]
    print(len(ppt_db_test1))
    print('第一次匹配', str(len(ppt_db_test1)))
    second_flag = False
    ppt_db_test1_index = ppt_db_test1.index

    # print('第二次匹配', str(len(ppt_db_test1)))

    # 匹配后的数据按照text数量差距，shape数量差距进行降序
    ppt_db_test1['text_diff'] = ppt_db_test1['text_num'].apply(lambda x: abs(x - text_len))
    ppt_db_test1['shape_diff'] = ppt_db_test1['shape_num'].apply(lambda x: abs(x - shape_len))
    ppt_db_test1 = ppt_db_test1[(ppt_db_test1['text_num'] >= text_len)
                                & (ppt_db_test1['graphic_num'] >= graphic_len)]
    ppt_db_test1 = ppt_db_test1.sort_values(by=['text_diff', 'shape_diff'], ascending=[True, True])

    return ppt_db_test1,second_flag

def get_best_match_ppt_2(query_df,query_all_info_df,db_df,query_labels,rg_flag):
    '''
    获取最佳匹配ppt,其中tuwen_layout，text_type需要计算得到，目前未完成
    v2版本修改了title，因为发现新版的ppt几乎没有title，所以这里面用new_title_len代替title,
    其中new_title_len表示的是estimate_title只有一个的ppt，也就是estimate_title = 1时，new_title_len=1
    :param query_df:
    :param query_all_info_df:
    :param db_df:
    :return:
    '''
    # tuwen_layout,text_type 是需要后面优化，得到该数据

    tuwen_layout = query_labels['tuwen_layout']
    text_type = query_labels['text_type']
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
    max_graphic_group = query_df.iloc[0]['max_graphic_group']
    subject_class = list(query_all_info_df['subject'].unique())
    ppt_width = query_all_info_df.iloc[0]['width']
    ppt_height = query_all_info_df.iloc[0]['height']


    max_text_area = query_df.iloc[0]['max_text_area']
    avg_text_area = query_df.iloc[0]['avg_text_area']
    max_shape_area = query_df.iloc[0]['max_shape_area']
    avg_shape_area = query_df.iloc[0]['avg_shape_area']
    max_graphic_area = query_df.iloc[0]['max_graphic_area']
    avg_graphic_area = query_df.iloc[0]['avg_graphic_area']
    max_text_content = query_df.iloc[0]['max_text_content']
    avg_text_content = query_df.iloc[0]['avg_text_content']
    max_text_area_group = query_df.iloc[0]['max_text_area_group']

    max_text_area_group_avg_content_size = query_df.iloc[0]['max_text_area_group_avg_content_size']
    max_text_font_group_avg_content_size = query_df.iloc[0]['max_text_font_group_avg_content_size']



    if 'texts' in subject_class:
        text_query_df = query_all_info_df[query_all_info_df['subject'] == 'texts']
    if 'shape' in subject_class:
        shape_query_df = query_all_info_df[query_all_info_df['subject'] == 'shape']
        shape_class = list(shape_query_df['class'].unique())
        if 'GraphicObjectShape' in shape_class:
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']

    if graphic_len == 1 and 'shape' in subject_class and 'GraphicObjectShape' in shape_class and \
            graphic_query_df.iloc[0]['shape_area'] < (ppt_height * ppt_width) / 5:
        tuwen_layout = 1

    outline_len_m = outline_len
    title_len_m = title_len
    if title_len > 0:
        outline_len_m = 0

    if title_len == 0 and outline_len == 0 and new_title_len == 1:
        title_len_m = 1

    title_combine_len = 0
    if title_len == 1:
        title_combine_len = 1
    elif new_title_len == 1:
        title_combine_len = 1

    first_flag = False













    # 这里我们彻底放弃 outliner 作为 title
    # title处理了new title和title

    if 0 not in rgraph_type:
        rgraph_type.append(0)
    if 0 not in tuwen_layout:
        tuwen_layout.append(0)
    if 0 not in text_type:
        text_type.append(0)

    ppt_db_match = pd.DataFrame()

    for one_text_type in text_type:
        for one_tuwen_layout in tuwen_layout:
            for one_rgraph_type in rgraph_type:
                if max_font_group < max_text_group + 1:
                    ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                          | (db_df['new_title_num'] == title_combine_len))
                                          & (db_df['outline_num'] == outline_len_m)
                                          & (db_df['max_text_group'] == max_text_group)
                                          & (db_df['table_num'] == table_len)
                                          & (db_df['chart_num'] == chart_len)
                                          & (db_df['graphic_num'] == graphic_len)
                                          & (db_df['max_graphic_group'] == max_graphic_group)
                                          & (db_df['tuwen_layout'] == one_tuwen_layout)
                                          & (db_df['text_type'] == one_text_type)
                                          & (db_df['rgraph_type'] == one_rgraph_type)
                                          ]
                else:
                    ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                          | (db_df['new_title_num'] == title_combine_len))
                                          & (db_df['outline_num'] == outline_len_m)
                                          & (db_df['max_text_group'] == max_font_group)
                                          & (db_df['table_num'] == table_len)
                                          & (db_df['chart_num'] == chart_len)
                                          & (db_df['graphic_num'] == graphic_len)
                                          & (db_df['max_graphic_group'] == max_graphic_group)
                                          & (db_df['tuwen_layout'] == one_tuwen_layout)
                                          & (db_df['text_type'] == one_text_type)
                                          & (db_df['rgraph_type'] == one_rgraph_type)
                                          ]

                print('参数 text_type %d tuwen_layout %d rgraph_type %d 匹配'%(one_text_type,one_tuwen_layout,one_rgraph_type), str(len(ppt_db_test1)))
                ppt_db_match = ppt_db_match.append(ppt_db_test1)
                second_flag = False
        #         if len(ppt_db_test1) > 0:
        #             first_flag = True
        #             second_flag = False
        #             break
        #
        #     if first_flag:
        #         second_flag = False
        #         break
        # if first_flag:
        #     second_flag = False
        #     break

    # if len(ppt_db_test1)


    # 匹配后的数据按照text数量差距，shape数量差距进行降序
    ppt_db_match['text_diff'] = ppt_db_match['text_num'].apply(lambda x: abs(x - text_len))
    ppt_db_match['shape_diff'] = ppt_db_match['shape_num'].apply(lambda x: abs(x - shape_len))
    ppt_db_match['max_text_content_diff'] = ppt_db_match['max_text_content'].apply(lambda x: abs(x - max_text_content))
    ppt_db_match['max_text_area_diff'] = ppt_db_match['max_text_area'].apply(lambda x: abs(x - max_text_area))
    ppt_db_match['max_graphic_area_diff'] = ppt_db_match['max_graphic_area'].apply(lambda x: abs(x - max_graphic_area))


    ppt_db_match['max_text_area_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_text_area']/(x['width']*x['height']) - max_text_area/(ppt_width*ppt_height)),axis=1)
    ppt_db_match['max_graphic_area_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_graphic_area']/(x['width']*x['height']) - max_graphic_area/(ppt_width*ppt_height)), axis=1)
    ppt_db_match['max_text_area_group_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_text_area_group']/(x['width']*x['height']) - max_text_area_group/(ppt_width*ppt_height)), axis=1)
    ppt_db_match['max_text_area_group_avg_content_size_diff'] = ppt_db_match.apply(lambda x:abs(x['max_text_area_group_avg_content_size'] - max_text_area_group_avg_content_size), axis=1)
    ppt_db_match['max_text_font_group_avg_content_size_diff'] = ppt_db_match.apply(lambda x:abs(x['max_text_font_group_avg_content_size'] - max_text_font_group_avg_content_size), axis=1)

    # print(query_all_info_df.iloc[0]['content'])
    # print(len(query_all_info_df.iloc[0]['content']))

    ppt_db_match = ppt_db_match[(ppt_db_match['text_num'] >= text_len)
                                & (ppt_db_match['graphic_num'] >= graphic_len)
                                # & (ppt_db_test1['max_text_area'] >= max_text_area)
                                ]
    if max_text_group > 1 or max_font_group > 1:

        if max_font_group < max_text_group + 1:


            ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                        'max_text_area_group_avg_content_size_diff',
                                                        'shape_diff',
                                                        'max_text_content_diff',
                                                        'max_text_area_diff_norm',
                                                        'max_graphic_area_diff_norm'],
                                                    ascending=[True, True, True, True, True, True])
        else:
            ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                        'max_text_font_group_avg_content_size_diff',
                                                        'shape_diff',
                                                        'max_text_content_diff',
                                                        'max_text_area_diff_norm',
                                                        'max_graphic_area_diff_norm'],
                                                    ascending=[True, True, True, True, True, True])


    else:

        ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                    'shape_diff',
                                                    'max_text_content_diff',
                                                    'max_text_area_diff_norm',
                                                    'max_graphic_area_diff_norm'],
                                                ascending=[True, True, True, True, True])

    print('匹配: ' , str(len(ppt_db_match)))
    ppt_db_match_index = ppt_db_match.index
    for i in range(len(ppt_db_match)):
        print(ppt_db_match.loc[ppt_db_match_index[i]]['file_name'],
              ' text_type ',ppt_db_match.loc[ppt_db_match_index[i]]['text_type'],
              ' tuwen_layout ',ppt_db_match.loc[ppt_db_match_index[i]]['tuwen_layout'],
              ' rgraph_type ',ppt_db_match.loc[ppt_db_match_index[i]]['rgraph_type'])

    return ppt_db_match,second_flag

def get_best_match_ppt(query_df,query_all_info_df,db_df):
    '''
    获取最佳匹配ppt,其中tuwen_layout，text_type需要计算得到，目前未完成
    :param query_df:
    :param query_all_info_df:
    :param db_df:
    :return:
    '''
    # tuwen_layout,text_type 是需要后面优化，得到该数据
    tuwen_layout = 1
    text_type = 0
    tuwen_layout = 0
    text_type = 1
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
    max_graphic_group = query_df.iloc[0]['max_graphic_group']
    subject_class = list(query_all_info_df['subject'].unique())
    ppt_width = query_all_info_df.iloc[0]['width']
    ppt_height = query_all_info_df.iloc[0]['height']

    if 'texts' in subject_class:
        text_query_df = query_all_info_df[query_all_info_df['subject'] == 'texts']
    if 'shape' in subject_class:
        shape_query_df = query_all_info_df[query_all_info_df['subject'] == 'shape']
        shape_class = list(shape_query_df['class'].unique())
        if 'GraphicObjectShape' in shape_class:
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']

    if graphic_len == 1 and 'shape' in subject_class and 'GraphicObjectShape' in shape_class and \
            graphic_query_df.iloc[0]['shape_area'] < (ppt_height * ppt_width) / 5:
        tuwen_layout = 1

    outline_len_m = outline_len
    title_len_m = title_len
    if title_len > 0:
        outline_len_m = 0

    if title_len == 0 and outline_len == 0 and new_title_len == 1:
        title_len_m = 1

    if max_font_group < max_text_group + 1:
        ppt_db_test1 = db_df[(db_df['title_num'] == title_len_m)
                              & (db_df['outline_num'] == outline_len_m)
                              & (db_df['max_text_group'] == max_text_group)
                              & (db_df['table_num'] == table_len)
                              & (db_df['chart_num'] == chart_len)
                              & (db_df['graphic_num'] == graphic_len)
                              & (db_df['max_graphic_group'] == max_graphic_group)
                              & (db_df['tuwen_layout'] == tuwen_layout)
                              & (db_df['text_type'] == text_type)
                              ]
    else:
        ppt_db_test1 = db_df[(db_df['title_num'] == title_len_m)
                              & (db_df['outline_num'] == outline_len_m)
                              & (db_df['max_text_group'] == max_font_group)
                              & (db_df['table_num'] == table_len)
                              & (db_df['chart_num'] == chart_len)
                              & (db_df['graphic_num'] == graphic_len)
                              & (db_df['max_graphic_group'] == max_graphic_group)
                              & (db_df['tuwen_layout'] == tuwen_layout)
                              & (db_df['text_type'] == text_type)
                              ]

    print(len(ppt_db_test1))
    print('第一次匹配', str(len(ppt_db_test1)))
    second_flag = False
    if len(ppt_db_test1) == 0:
        second_flag = True
        if max_font_group < max_text_group + 1:
            ppt_db_test1 = db_df[(db_df['outline_num'] == title_len_m)
                                  & (db_df['max_text_group'] == max_text_group)
                                  & (db_df['table_num'] == table_len)
                                  & (db_df['chart_num'] == chart_len)
                                  & (db_df['graphic_num'] == graphic_len)
                                  & (db_df['max_graphic_group'] == max_graphic_group)
                                  & (db_df['tuwen_layout'] == tuwen_layout)
                                  & (db_df['text_type'] == text_type)
                                  ]
        else:
            ppt_db_test1 = db_df[(db_df['outline_num'] == title_len_m)
                                  & (db_df['max_text_group'] == max_font_group)
                                  & (db_df['table_num'] == table_len)
                                  & (db_df['chart_num'] == chart_len)
                                  & (db_df['graphic_num'] == graphic_len)
                                  & (db_df['max_graphic_group'] == max_graphic_group)
                                  & (db_df['tuwen_layout'] == tuwen_layout)
                                  & (db_df['text_type'] == text_type)
                                  ]
    ppt_db_test1_index = ppt_db_test1.index
    for i in range(len(ppt_db_test1)):
        print(ppt_db_test1.loc[ppt_db_test1_index[i]]['file_name'])
    print('第二次匹配', str(len(ppt_db_test1)))

    # 匹配后的数据按照text数量差距，shape数量差距进行降序
    ppt_db_test1['text_diff'] = ppt_db_test1['text_num'].apply(lambda x: abs(x - text_len))
    ppt_db_test1['shape_diff'] = ppt_db_test1['shape_num'].apply(lambda x: abs(x - shape_len))
    ppt_db_test1 = ppt_db_test1[ppt_db_test1['text_num'] >= text_len]
    ppt_db_test1 = ppt_db_test1.sort_values(by=['text_diff', 'shape_diff'], ascending=[True, True])
    return ppt_db_test1,second_flag


def get_best_match_ppt_p1(query_df, query_all_info_df, db_df):
    '''
    获取最佳匹配ppt,这个是早起的版本，不需要tuwen_layout和text_type
    :param query_df:
    :param query_all_info_df:
    :param db_df:
    :return:
    '''
    tuwen_layout = 0
    text_type = 1
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
    max_graphic_group = query_df.iloc[0]['max_graphic_group']
    subject_class = list(query_all_info_df['subject'].unique())
    ppt_width = query_all_info_df.iloc[0]['width']
    ppt_height = query_all_info_df.iloc[0]['height']

    if 'texts' in subject_class:
        text_query_df = query_all_info_df[query_all_info_df['subject'] == 'texts']
    if 'shape' in subject_class:
        shape_query_df = query_all_info_df[query_all_info_df['subject'] == 'shape']
        shape_class = list(shape_query_df['class'].unique())
        if 'GraphicObjectShape' in shape_class:
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']

    if graphic_len == 1 and 'shape' in subject_class and 'GraphicObjectShape' in shape_class and \
            graphic_query_df.iloc[0]['shape_area'] < (ppt_height * ppt_width) / 5:
        tuwen_type = 1

    outline_len_m = outline_len
    title_len_m = title_len
    if title_len > 0:
        outline_len_m = 0

    if title_len == 0 and outline_len == 0 and new_title_len == 1:
        title_len_m = 1

    if max_font_group < max_text_group + 1:
        ppt_db_test1 = db_df[(db_df['title_num'] == title_len_m)
                             & (db_df['outline_num'] == outline_len_m)
                             & (db_df['max_text_group'] == max_text_group)
                             & (db_df['table_num'] == table_len)
                             & (db_df['chart_num'] == chart_len)
                             & (db_df['graphic_num'] == graphic_len)
                             & (db_df['max_graphic_group'] == max_graphic_group)

                             ]
    else:
        ppt_db_test1 = db_df[(db_df['title_num'] == title_len_m)
                             & (db_df['outline_num'] == outline_len_m)
                             & (db_df['max_text_group'] == max_font_group)
                             & (db_df['table_num'] == table_len)
                             & (db_df['chart_num'] == chart_len)
                             & (db_df['graphic_num'] == graphic_len)
                             & (db_df['max_graphic_group'] == max_graphic_group)

                             ]

    print(len(ppt_db_test1))
    print('第一次匹配', str(len(ppt_db_test1)))
    second_flag = False
    if len(ppt_db_test1) == 0:
        second_flag = True
        if max_font_group < max_text_group + 1:
            ppt_db_test1 = db_df[(db_df['outline_num'] == title_len_m)
                                 & (db_df['max_text_group'] == max_text_group)
                                 & (db_df['table_num'] == table_len)
                                 & (db_df['chart_num'] == chart_len)
                                 & (db_df['graphic_num'] == graphic_len)
                                 & (db_df['max_graphic_group'] == max_graphic_group)

                                 ]
        else:
            ppt_db_test1 = db_df[(db_df['outline_num'] == title_len_m)
                                 & (db_df['max_text_group'] == max_font_group)
                                 & (db_df['table_num'] == table_len)
                                 & (db_df['chart_num'] == chart_len)
                                 & (db_df['graphic_num'] == graphic_len)
                                 & (db_df['max_graphic_group'] == max_graphic_group)

                                 ]
    ppt_db_test1_index = ppt_db_test1.index
    for i in range(len(ppt_db_test1)):
        print(ppt_db_test1.loc[ppt_db_test1_index[i]]['file_name'])
    print('第二次匹配', str(len(ppt_db_test1)))

    # 匹配后的数据按照text数量差距，shape数量差距进行降序
    ppt_db_test1['text_diff'] = ppt_db_test1['text_num'].apply(lambda x: abs(x - text_len))
    ppt_db_test1['shape_diff'] = ppt_db_test1['shape_num'].apply(lambda x: abs(x - shape_len))
    ppt_db_test1 = ppt_db_test1[ppt_db_test1['text_num'] >= text_len]
    ppt_db_test1 = ppt_db_test1.sort_values(by=['text_diff', 'shape_diff'], ascending=[True, True])
    return ppt_db_test1,second_flag

def get_best_match_ppt_3(query_df,query_all_info_df,db_df,query_labels,rg_flag):
    '''
    获取最佳匹配ppt,其中tuwen_layout，text_type需要计算得到，目前未完成
    v2版本修改了title，因为发现新版的ppt几乎没有title，所以这里面用new_title_len代替title,
    其中new_title_len表示的是estimate_title只有一个的ppt，也就是estimate_title = 1时，new_title_len=1
    :param query_df:
    :param query_all_info_df:
    :param db_df:
    :return:
    '''
    # tuwen_layout,text_type 是需要后面优化，得到该数据
    pair_flag = True
    if 'pair' not in query_all_info_df.columns:
        query_all_info_df['pair'] = 'no'
        pair_flag = False

    tuwen_layout = query_labels['tuwen_layout']
    text_type = query_labels['text_type']
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
    max_graphic_group = query_df.iloc[0]['max_graphic_group']
    subject_class = list(query_all_info_df['subject'].unique())
    ppt_width = query_all_info_df.iloc[0]['width']
    ppt_height = query_all_info_df.iloc[0]['height']


    max_text_area = query_df.iloc[0]['max_text_area']
    avg_text_area = query_df.iloc[0]['avg_text_area']
    max_shape_area = query_df.iloc[0]['max_shape_area']
    avg_shape_area = query_df.iloc[0]['avg_shape_area']
    max_graphic_area = query_df.iloc[0]['max_graphic_area']
    avg_graphic_area = query_df.iloc[0]['avg_graphic_area']
    max_text_content = query_df.iloc[0]['max_text_content']
    avg_text_content = query_df.iloc[0]['avg_text_content']
    max_text_area_group = query_df.iloc[0]['max_text_area_group']




    # time_break = query_all_info_df.iloc[0]['time_break']
    time_break = 0

    max_text_group_num = query_df.iloc[0]['max_text_group_num']
    max_font_group_num = query_df.iloc[0]['max_font_group_num']

    max_text_area_group_avg_content_size = query_df.iloc[0]['max_text_area_group_avg_content_size']
    max_text_font_group_avg_content_size = query_df.iloc[0]['max_text_font_group_avg_content_size']



    if 'texts' in subject_class:
        text_query_df = query_all_info_df[query_all_info_df['subject'] == 'texts']
    if 'shape' in subject_class:
        shape_query_df = query_all_info_df[query_all_info_df['subject'] == 'shape']
        shape_class = list(shape_query_df['class'].unique())
        if 'GraphicObjectShape' in shape_class:
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']

    if graphic_len == 1 and 'shape' in subject_class and 'GraphicObjectShape' in shape_class and \
            graphic_query_df.iloc[0]['shape_area'] < (ppt_height * ppt_width) / 5:
        tuwen_layout = [1]

    outline_len_m = outline_len
    title_len_m = title_len
    if title_len > 0:
        outline_len_m = 0

    if title_len == 0 and outline_len == 0 and new_title_len == 1:
        title_len_m = 1

    title_combine_len = 0
    if title_len == 1:
        title_combine_len = 1
    elif new_title_len == 1:
        title_combine_len = 1

    first_flag = False













    # 这里我们彻底放弃 outliner 作为 title
    # title处理了new title和title

    if 0 not in rgraph_type:
        rgraph_type.append(0)
    if 0 not in tuwen_layout:
        tuwen_layout.append(0)
    if 0 not in text_type:
        text_type.append(0)

    ppt_db_match = pd.DataFrame()

    '''
    调整 max_font_group
    '''
    font_pair_flag = False
    # 1.解决标题的影响
    if title_combine_len == 1 and text_type == [3,0] and max_font_group > 1:

        title_pd = query_all_info_df[query_all_info_df['class'] == 'TitleTextShape']
        if len(title_pd) == 0:
            title_pd = query_all_info_df[query_all_info_df['estimate_title'] == 1]
        text_query_df_font_group = query_all_info_df[query_all_info_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                                      'font-name',
                                                                                                      'font-weight',
                                                                                                      'font-size-asian',
                                                                                                      'font-name-asian',
                                                                                                      'font-style'],
                                                                                                     as_index=False)[
            'class'].count()

        font_group_font_size = text_query_df_font_group.iloc[0]['font-size']
        font_group_font_name = text_query_df_font_group.iloc[0]['font-name']
        font_group_font_weight = text_query_df_font_group.iloc[0]['font-weight']
        font_group_font_size_asian = text_query_df_font_group.iloc[0]['font-size-asian']
        font_group_font_name_asian = text_query_df_font_group.iloc[0]['font-name-asian']
        font_group_font_style = text_query_df_font_group.iloc[0]['font-style']

        title_font_size = title_pd.iloc[0]['font-size']
        title_font_name = title_pd.iloc[0]['font-name']
        title_font_weight = title_pd.iloc[0]['font-weight']
        title_font_size_asian = title_pd.iloc[0]['font-size-asian']
        title_font_name_asian = title_pd.iloc[0]['font-name-asian']
        title_font_style = title_pd.iloc[0]['font-style']

        if font_group_font_size == title_font_size \
                and font_group_font_name == title_font_name \
                and font_group_font_weight == title_font_weight \
                and font_group_font_size_asian == title_font_size_asian \
                and font_group_font_name_asian == title_font_name_asian \
                and font_group_font_style == title_font_style:
            max_font_group = max_font_group -1
            print('hello')
    # 解决小标题问题
    elif max_font_group % 2 == 0 and max_font_group >= 4 and max_font_group >= 2*max_text_group:
        text_query_df_font_group = \
        query_all_info_df[query_all_info_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                   'font-name',
                                                                                   'font-weight',
                                                                                   'font-size-asian',
                                                                                   'font-name-asian',
                                                                                   'font-style'],
                                                                                  as_index=False)[
            'class'].count()

        font_group_font_size = text_query_df_font_group.iloc[0]['font-size']
        font_group_font_name = text_query_df_font_group.iloc[0]['font-name']
        font_group_font_weight = text_query_df_font_group.iloc[0]['font-weight']
        font_group_font_size_asian = text_query_df_font_group.iloc[0]['font-size-asian']
        font_group_font_name_asian = text_query_df_font_group.iloc[0]['font-name-asian']
        font_group_font_style = text_query_df_font_group.iloc[0]['font-style']

        query_all_info_font_df = query_all_info_df[(query_all_info_df['class'] != 'TitleTextShape') &
                                                   (query_all_info_df['font-size'] == font_group_font_size) &
                                                   (query_all_info_df['font-name'] == font_group_font_name) &
                                                   (query_all_info_df['font-weight'] == font_group_font_weight) &
                                                   (query_all_info_df['font-size-asian'] == font_group_font_size_asian) &
                                                   (query_all_info_df['font-name-asian'] == font_group_font_name_asian) &
                                                   (query_all_info_df['font-style'] == font_group_font_style)]

        avg_content_size = query_all_info_font_df['content_size'].mean()
        avg_content_size_lt = query_all_info_font_df[query_all_info_font_df['content_size'] < avg_content_size]
        avg_content_size_lt_num = len(avg_content_size_lt)
        if max_font_group == 2*avg_content_size_lt_num:
            max_font_group = max_font_group/2

            if pair_flag == False:
                pair_flag = True
                font_pair_flag = True
                max_font_group_num = max_font_group_num + 1
                avg_content_size_gt = query_all_info_font_df[query_all_info_font_df['content_size'] >= avg_content_size]
                avg_content_size_lt = avg_content_size_lt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
                avg_content_size_gt = avg_content_size_gt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

                for i in range(avg_content_size_lt_num):
                    lt_key = avg_content_size_lt.iloc[i]['key']
                    lt_name = avg_content_size_lt.iloc[i]['name']

                    gt_key = avg_content_size_gt.iloc[i]['key']
                    gt_name = avg_content_size_gt.iloc[i]['name']

                    query_all_info_df.loc[(query_all_info_df['key'] == lt_key)&(query_all_info_df['name'] == lt_name),'pair'] = str(lt_key) + '_' + '0'
                    query_all_info_df.loc[(query_all_info_df['key'] == gt_key)&(query_all_info_df['name'] == gt_name),'pair'] = str(lt_key) + '_' + '1'


            print('hello')





        # print('hello')
    print('hello')

    # 类型排名




    for one_text_type in text_type:
        for one_tuwen_layout in tuwen_layout:
            for one_rgraph_type in rgraph_type:
                if ((max_font_group < max_text_group + 1) or (time_break == 1)) and font_pair_flag == False:
                    ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                          | (db_df['new_title_num'] == title_combine_len))
                                          # & (db_df['outline_num'] == outline_len_m)
                                          & (db_df['max_text_group'] == max_text_group)
                                          & (db_df['table_num'] == table_len)
                                          & (db_df['chart_num'] == chart_len)
                                          & (db_df['graphic_num'] == graphic_len)
                                          & (db_df['max_graphic_group'] == max_graphic_group)
                                          & (db_df['tuwen_layout'] == one_tuwen_layout)
                                          & (db_df['text_type'] == one_text_type)
                                          & (db_df['rgraph_type'] == one_rgraph_type)
                                          & (db_df['max_text_group_num'] >= max_text_group_num)
                                          ]
                else:
                    ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                          | (db_df['new_title_num'] == title_combine_len))
                                          # & (db_df['outline_num'] == outline_len_m)
                                          & (db_df['max_text_group'] == max_font_group)
                                          & (db_df['table_num'] == table_len)
                                          & (db_df['chart_num'] == chart_len)
                                          & (db_df['graphic_num'] == graphic_len)
                                          & (db_df['max_graphic_group'] == max_graphic_group)
                                          & (db_df['tuwen_layout'] == one_tuwen_layout)
                                          & (db_df['text_type'] == one_text_type)
                                          & (db_df['rgraph_type'] == one_rgraph_type)
                                          & (db_df['max_font_group_num'] >= max_font_group_num)
                                          ]

                print('参数 text_type %d tuwen_layout %d rgraph_type %d 匹配'%(one_text_type,one_tuwen_layout,one_rgraph_type), str(len(ppt_db_test1)))
                ppt_db_match = ppt_db_match.append(ppt_db_test1)
                second_flag = False
        #         if len(ppt_db_test1) > 0:
        #             first_flag = True
        #             second_flag = False
        #             break
        #
        #     if first_flag:
        #         second_flag = False
        #         break
        # if first_flag:
        #     second_flag = False
        #     break

    # if len(ppt_db_test1)

    if len(ppt_db_match) == 0:
        print('no ppt')
        return ppt_db_match, second_flag

    # 匹配后的数据按照text数量差距，shape数量差距进行降序
    ppt_db_match['text_diff'] = ppt_db_match['text_num'].apply(lambda x: abs(x - text_len))
    ppt_db_match['shape_diff'] = ppt_db_match['shape_num'].apply(lambda x: abs(x - shape_len))
    ppt_db_match['max_text_content_diff'] = ppt_db_match['max_text_content'].apply(lambda x: abs(x - max_text_content))
    ppt_db_match['max_text_area_diff'] = ppt_db_match['max_text_area'].apply(lambda x: abs(x - max_text_area))
    ppt_db_match['max_graphic_area_diff'] = ppt_db_match['max_graphic_area'].apply(lambda x: abs(x - max_graphic_area))


    ppt_db_match['max_text_area_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_text_area']/(x['width']*x['height']) - max_text_area/(ppt_width*ppt_height)),axis=1)
    ppt_db_match['max_graphic_area_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_graphic_area']/(x['width']*x['height']) - max_graphic_area/(ppt_width*ppt_height)), axis=1)
    ppt_db_match['max_text_area_group_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_text_area_group']/(x['width']*x['height']) - max_text_area_group/(ppt_width*ppt_height)), axis=1)
    ppt_db_match['max_text_area_group_avg_content_size_diff'] = ppt_db_match.apply(lambda x:abs(x['max_text_area_group_avg_content_size'] - max_text_area_group_avg_content_size), axis=1)
    ppt_db_match['max_text_font_group_avg_content_size_diff'] = ppt_db_match.apply(lambda x:abs(x['max_text_font_group_avg_content_size'] - max_text_font_group_avg_content_size), axis=1)

    # print(query_all_info_df.iloc[0]['content'])
    # print(len(query_all_info_df.iloc[0]['content']))

    ppt_db_match = ppt_db_match[(ppt_db_match['text_num'] >= text_len)
                                & (ppt_db_match['graphic_num'] >= graphic_len)
                                # & (ppt_db_test1['max_text_area'] >= max_text_area)
                                ]
    if max_text_group > 1 or max_font_group > 1:

        if (max_font_group < max_text_group + 1) or time_break == 1:


            ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                        'max_text_area_group_avg_content_size_diff',
                                                        'shape_diff',
                                                        'max_text_content_diff',
                                                        'max_text_area_diff_norm',
                                                        'max_graphic_area_diff_norm'],
                                                    ascending=[True, True, True, True, True, True])
        else:
            ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                        'max_text_font_group_avg_content_size_diff',
                                                        'shape_diff',
                                                        'max_text_content_diff',
                                                        'max_text_area_diff_norm',
                                                        'max_graphic_area_diff_norm'],
                                                    ascending=[True, True, True, True, True, True])


    else:

        ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                    'shape_diff',
                                                    'max_text_content_diff',
                                                    'max_text_area_diff_norm',
                                                    'max_graphic_area_diff_norm'],
                                                ascending=[True, True, True, True, True])

    print('第一次原始匹配: ' , str(len(ppt_db_match)))
    ppt_db_match_index = ppt_db_match.index
    for i in range(len(ppt_db_match)):
        print(ppt_db_match.loc[ppt_db_match_index[i]]['file_name'],
              ' text_type ',ppt_db_match.loc[ppt_db_match_index[i]]['text_type'],
              ' tuwen_layout ',ppt_db_match.loc[ppt_db_match_index[i]]['tuwen_layout'],
              ' rgraph_type ',ppt_db_match.loc[ppt_db_match_index[i]]['rgraph_type'])

    ppt_db_match['text_type_rank'] = ppt_db_match['text_type'].apply(lambda x:text_type.index(x))
    ppt_db_match['tuwen_layout_rank'] = ppt_db_match['tuwen_layout'].apply(lambda x:tuwen_layout.index(x))
    ppt_db_match['rgraph_type_rank'] = ppt_db_match['rgraph_type'].apply(lambda x:rgraph_type.index(x))
    ppt_db_match['origin_rank'] = range(len(ppt_db_match))

    ppt_db_match = ppt_db_match.sort_values(by=['text_type_rank',
                                                'tuwen_layout_rank',
                                                'rgraph_type_rank',
                                                'origin_rank'],
                                                    ascending=[True, True, True, True])
    print(''
          '\n'
          '\n'
          '\n')

    print('第二次类型匹配: ', str(len(ppt_db_match)))
    ppt_db_match_index = ppt_db_match.index
    for i in range(len(ppt_db_match)):
        print(ppt_db_match.loc[ppt_db_match_index[i]]['file_name'],
              ' text_type ', ppt_db_match.loc[ppt_db_match_index[i]]['text_type'],
              ' tuwen_layout ', ppt_db_match.loc[ppt_db_match_index[i]]['tuwen_layout'],
              ' rgraph_type ', ppt_db_match.loc[ppt_db_match_index[i]]['rgraph_type'])

    return ppt_db_match,second_flag


def get_font_size(x):
    x = x.replace('pt','')
    if x == '':
        x = 0.0
    else:
        x = float(x)
    return x

def get_best_match_ppt_v4(query_df,query_all_info_df,db_df,query_labels,rg_flag):
    '''
    获取最佳匹配ppt,其中tuwen_layout，text_type需要计算得到，目前未完成
    v2版本修改了title，因为发现新版的ppt几乎没有title，所以这里面用new_title_len代替title,
    其中new_title_len表示的是estimate_title只有一个的ppt，也就是estimate_title = 1时，new_title_len=1
    :param query_df:
    :param query_all_info_df:
    :param db_df:
    :return:
    '''
    # tuwen_layout,text_type 是需要后面优化，得到该数据
    pair_flag = False
    if len(query_all_info_df[query_all_info_df['pair'] != 'no']) > 0:
        pair_flag = True

    tuwen_layout = query_labels['tuwen_layout']
    text_type = query_labels['text_type']
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

    max_graphic_group = query_df.iloc[0]['max_graphic_group']
    subject_class = list(query_all_info_df['subject'].unique())
    ppt_width = query_all_info_df.iloc[0]['width']
    ppt_height = query_all_info_df.iloc[0]['height']


    max_text_area = query_df.iloc[0]['max_text_area']
    avg_text_area = query_df.iloc[0]['avg_text_area']
    max_shape_area = query_df.iloc[0]['max_shape_area']
    avg_shape_area = query_df.iloc[0]['avg_shape_area']
    max_graphic_area = query_df.iloc[0]['max_graphic_area']
    avg_graphic_area = query_df.iloc[0]['avg_graphic_area']
    max_text_content = query_df.iloc[0]['max_text_content']
    avg_text_content = query_df.iloc[0]['avg_text_content']
    max_text_area_group = query_df.iloc[0]['max_text_area_group']




    # time_break = query_all_info_df.iloc[0]['time_break']
    time_break = 0

    max_text_group_num = query_df.iloc[0]['max_text_group_num']
    max_font_group_num = query_df.iloc[0]['max_font_group_num']

    max_text_area_group_avg_content_size = query_df.iloc[0]['max_text_area_group_avg_content_size']
    max_text_font_group_avg_content_size = query_df.iloc[0]['max_text_font_group_avg_content_size']



    if 'texts' in subject_class:
        text_query_df = query_all_info_df[query_all_info_df['subject'] == 'texts']
    if 'shape' in subject_class:
        shape_query_df = query_all_info_df[query_all_info_df['subject'] == 'shape']
        shape_class = list(shape_query_df['class'].unique())
        if 'GraphicObjectShape' in shape_class:
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']

    if graphic_len == 1 and 'shape' in subject_class and 'GraphicObjectShape' in shape_class and \
            graphic_query_df.iloc[0]['shape_area'] < (ppt_height * ppt_width) / 5:
        tuwen_layout = [1]

    outline_len_m = outline_len
    title_len_m = title_len
    if title_len > 0:
        outline_len_m = 0

    if title_len == 0 and outline_len == 0 and new_title_len == 1:
        title_len_m = 1

    title_combine_len = 0
    if title_len == 1:
        title_combine_len = 1
    elif new_title_len == 1:
        title_combine_len = 1
    elif font_size_estimate_title_num == 1:
        title_combine_len = 1

    first_flag = False













    # 这里我们彻底放弃 outliner 作为 title
    # title处理了new title和title

    if 0 not in rgraph_type:
        rgraph_type.append(0)
    if 0 not in tuwen_layout:
        tuwen_layout.append(0)
    if 0 not in text_type:
        text_type.append(0)

    ppt_db_match = pd.DataFrame()

    '''
    调整 max_font_group
    '''
    font_pair_flag = False
    # 1.解决标题的影响
    if title_combine_len == 1 and text_type == [3,0] and max_font_group > 1:

        title_pd = query_all_info_df[query_all_info_df['class'] == 'TitleTextShape']
        if len(title_pd) == 0:
            title_pd = query_all_info_df[query_all_info_df['estimate_title'] == 1]
        text_query_df_font_group = query_all_info_df[query_all_info_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                                      'font-name',
                                                                                                      'font-weight',
                                                                                                      'font-size-asian',
                                                                                                      'font-name-asian',
                                                                                                      'font-style'],
                                                                                                     as_index=False)[
            'class'].count()

        font_group_font_size = text_query_df_font_group.iloc[0]['font-size']
        font_group_font_name = text_query_df_font_group.iloc[0]['font-name']
        font_group_font_weight = text_query_df_font_group.iloc[0]['font-weight']
        font_group_font_size_asian = text_query_df_font_group.iloc[0]['font-size-asian']
        font_group_font_name_asian = text_query_df_font_group.iloc[0]['font-name-asian']
        font_group_font_style = text_query_df_font_group.iloc[0]['font-style']

        title_font_size = title_pd.iloc[0]['font-size']
        title_font_name = title_pd.iloc[0]['font-name']
        title_font_weight = title_pd.iloc[0]['font-weight']
        title_font_size_asian = title_pd.iloc[0]['font-size-asian']
        title_font_name_asian = title_pd.iloc[0]['font-name-asian']
        title_font_style = title_pd.iloc[0]['font-style']

        if font_group_font_size == title_font_size \
                and font_group_font_name == title_font_name \
                and font_group_font_weight == title_font_weight \
                and font_group_font_size_asian == title_font_size_asian \
                and font_group_font_name_asian == title_font_name_asian \
                and font_group_font_style == title_font_style:
            max_font_group = max_font_group -1
            print('hello')
    # 解决小标题问题
    elif max_font_group % 2 == 0 and max_font_group >= 4 and max_font_group >= 2*max_text_group:
        text_query_df_font_group = \
        query_all_info_df[query_all_info_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                   'font-name',
                                                                                   'font-weight',
                                                                                   'font-size-asian',
                                                                                   'font-name-asian',
                                                                                   'font-style'],
                                                                                  as_index=False)[
            'class'].count()

        font_group_font_size = text_query_df_font_group.iloc[0]['font-size']
        font_group_font_name = text_query_df_font_group.iloc[0]['font-name']
        font_group_font_weight = text_query_df_font_group.iloc[0]['font-weight']
        font_group_font_size_asian = text_query_df_font_group.iloc[0]['font-size-asian']
        font_group_font_name_asian = text_query_df_font_group.iloc[0]['font-name-asian']
        font_group_font_style = text_query_df_font_group.iloc[0]['font-style']

        query_all_info_font_df = query_all_info_df[(query_all_info_df['class'] != 'TitleTextShape') &
                                                   (query_all_info_df['font-size'] == font_group_font_size) &
                                                   (query_all_info_df['font-name'] == font_group_font_name) &
                                                   (query_all_info_df['font-weight'] == font_group_font_weight) &
                                                   (query_all_info_df['font-size-asian'] == font_group_font_size_asian) &
                                                   (query_all_info_df['font-name-asian'] == font_group_font_name_asian) &
                                                   (query_all_info_df['font-style'] == font_group_font_style)]

        avg_content_size = query_all_info_font_df['content_size'].mean()
        avg_content_size_lt = query_all_info_font_df[query_all_info_font_df['content_size'] < avg_content_size]
        avg_content_size_lt_num = len(avg_content_size_lt)
        if max_font_group == 2*avg_content_size_lt_num:
            max_font_group = max_font_group/2

            if pair_flag == False:
                pair_flag = True
                font_pair_flag = True
                max_font_group_num = max_font_group_num + 1
                avg_content_size_gt = query_all_info_font_df[query_all_info_font_df['content_size'] >= avg_content_size]
                avg_content_size_lt = avg_content_size_lt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
                avg_content_size_gt = avg_content_size_gt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

                for i in range(avg_content_size_lt_num):
                    lt_key = avg_content_size_lt.iloc[i]['key']
                    lt_name = avg_content_size_lt.iloc[i]['name']

                    gt_key = avg_content_size_gt.iloc[i]['key']
                    gt_name = avg_content_size_gt.iloc[i]['name']

                    query_all_info_df.loc[(query_all_info_df['key'] == lt_key)&(query_all_info_df['name'] == lt_name),'pair'] = str(lt_key) + '_' + '0'
                    query_all_info_df.loc[(query_all_info_df['key'] == gt_key)&(query_all_info_df['name'] == gt_name),'pair'] = str(lt_key) + '_' + '1'


            print('hello')





        # print('hello')
    print('hello')

    # 类型排名

    # 这里调整近似分条列举
    if 1 in text_type \
            and max_font_group < len(text_query_df[text_query_df['class']!='TitleTextShape']) \
            and max_text_group < len(text_query_df[text_query_df['class']!='TitleTextShape']) :
        text_query_estimate_group_df = text_query_df[text_query_df['class']!='TitleTextShape']
        text_query_estimate_group_df.loc[:,'shape_width_bias'] \
            = abs(text_query_estimate_group_df['shape_width'] - text_query_estimate_group_df['shape_width'].mean())
        text_query_estimate_group_df.loc[:, 'shape_height_bias'] \
            = abs(text_query_estimate_group_df['shape_height'] - text_query_estimate_group_df['shape_height'].mean())
        text_query_estimate_group_df.loc[:, 'font_size_bias'] \
            = abs(text_query_estimate_group_df['font-size'].apply(lambda x:get_font_size(x)) - text_query_estimate_group_df['font-size'].apply(lambda x:get_font_size(x)).mean())

        text_query_estimate_group_match_df = text_query_estimate_group_df[(text_query_estimate_group_df['shape_width_bias'] < 1) & (text_query_estimate_group_df['shape_height_bias'] < 0.2) & (text_query_estimate_group_df['font_size_bias'] < 2)]
        if len(text_query_estimate_group_match_df) == len(text_query_estimate_group_df):
            query_all_info_df.loc[(query_all_info_df['class']!='TitleTextShape') & (query_all_info_df['subject']=='texts'),'shape_area'] = text_query_estimate_group_df['shape_area'].mean()
            max_text_group = len(text_query_estimate_group_match_df)
            query_df.loc[:, 'max_text_group'] = max_text_group
            query_df.loc[:, 'max_text_group_num'] = 1
        print('如果几个文本框差距不是很大，那么认为是一组的')




    for one_text_type in text_type:
        for one_tuwen_layout in tuwen_layout:
            for one_rgraph_type in rgraph_type:
                if ((max_font_group < max_text_group + 1) or (time_break == 1)) and font_pair_flag == False:
                    ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                          | (db_df['new_title_num'] == title_combine_len)
                                          | (db_df['font_size_estimate_title_num'] == title_combine_len)) #如果是1的化，这三个必须满足一个
                                          # & (db_df['outline_num'] == outline_len_m)
                                          & (db_df['max_text_group'] == max_text_group)
                                          & (db_df['table_num'] == table_len)
                                          & (db_df['chart_num'] == chart_len)
                                          & (db_df['graphic_num'] == graphic_len)
                                          & (db_df['max_graphic_group'] == max_graphic_group)
                                          & (db_df['tuwen_layout'] == one_tuwen_layout)
                                          & (db_df['text_type'] == one_text_type)
                                          & (db_df['rgraph_type'] == one_rgraph_type)
                                          & (db_df['max_text_group_num'] >= max_text_group_num)
                                          ]
                else:
                    ppt_db_test1 = db_df[((db_df['title_num'] == title_combine_len)
                                          | (db_df['new_title_num'] == title_combine_len)
                                          | (db_df['font_size_estimate_title_num'] == title_combine_len))
                                          # & (db_df['outline_num'] == outline_len_m)
                                          & (db_df['max_text_group'] == max_font_group)
                                          & (db_df['table_num'] == table_len)
                                          & (db_df['chart_num'] == chart_len)
                                          & (db_df['graphic_num'] == graphic_len)
                                          & (db_df['max_graphic_group'] == max_graphic_group)
                                          & (db_df['tuwen_layout'] == one_tuwen_layout)
                                          & (db_df['text_type'] == one_text_type)
                                          & (db_df['rgraph_type'] == one_rgraph_type)
                                          & (db_df['max_font_group_num'] >= max_font_group_num)
                                          ]

                print('参数 text_type %d tuwen_layout %d rgraph_type %d 匹配'%(one_text_type,one_tuwen_layout,one_rgraph_type), str(len(ppt_db_test1)))
                ppt_db_match = ppt_db_match.append(ppt_db_test1)
                second_flag = False


    if len(ppt_db_match) == 0:
        print('no ppt')
        return ppt_db_match, second_flag,query_df,query_all_info_df

    # 匹配后的数据按照text数量差距，shape数量差距进行降序
    ppt_db_match['text_diff'] = ppt_db_match['text_num'].apply(lambda x: abs(x - text_len))
    ppt_db_match['shape_diff'] = ppt_db_match['shape_num'].apply(lambda x: abs(x - shape_len))
    ppt_db_match['max_text_content_diff'] = ppt_db_match['max_text_content'].apply(lambda x: abs(x - max_text_content))
    ppt_db_match['max_text_content_rate'] = ppt_db_match['max_text_content'].apply(lambda x: abs((x + 1) / (max_text_content + 1)))

    ppt_db_match['max_text_area_diff'] = ppt_db_match['max_text_area'].apply(lambda x: abs(x - max_text_area))
    ppt_db_match['max_graphic_area_diff'] = ppt_db_match['max_graphic_area'].apply(lambda x: abs(x - max_graphic_area))


    ppt_db_match['max_text_area_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_text_area']/(x['width']*x['height']) - max_text_area/(ppt_width*ppt_height)),axis=1)
    ppt_db_match['max_graphic_area_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_graphic_area']/(x['width']*x['height']) - max_graphic_area/(ppt_width*ppt_height)), axis=1)
    ppt_db_match['max_text_area_group_diff_norm'] = ppt_db_match.apply(lambda x:abs(x['max_text_area_group']/(x['width']*x['height']) - max_text_area_group/(ppt_width*ppt_height)), axis=1)
    ppt_db_match['max_text_area_group_avg_content_size_diff'] = ppt_db_match.apply(lambda x:abs(x['max_text_area_group_avg_content_size'] - max_text_area_group_avg_content_size), axis=1)
    ppt_db_match['max_text_area_group_avg_content_size_rate'] = ppt_db_match.apply(lambda x:abs((x['max_text_area_group_avg_content_size'] + 1) / (max_text_area_group_avg_content_size + 1)), axis=1)
    ppt_db_match['max_text_font_group_avg_content_size_diff'] = ppt_db_match.apply(lambda x:abs(x['max_text_font_group_avg_content_size'] - max_text_font_group_avg_content_size), axis=1)
    ppt_db_match['max_text_font_group_avg_content_size_rate'] = ppt_db_match.apply(lambda x:abs((x['max_text_font_group_avg_content_size'] + 1) / (max_text_font_group_avg_content_size + 1)), axis=1)

    print('第一次原始匹配: ', str(len(ppt_db_match)))


    # print(query_all_info_df.iloc[0]['content'])
    # print(len(query_all_info_df.iloc[0]['content']))

    ppt_db_match = ppt_db_match[(ppt_db_match['text_num'] >= text_len)
                                & (ppt_db_match['graphic_num'] >= graphic_len)
                                & (2*ppt_db_match['max_text_content'] >= max_text_content)
                                # & (ppt_db_test1['max_text_area'] >= max_text_area)
                                ]
    print('第二次筛选: ', str(len(ppt_db_match)))
    if max_text_group > 1 or max_font_group > 1:

        if (max_font_group < max_text_group + 1) or time_break == 1:

            ppt_db_match = ppt_db_match[2*ppt_db_match['max_text_area_group_avg_content_size'] >= max_text_area_group_avg_content_size]

            if max_text_area_group_avg_content_size >= 10:
                ppt_db_match = ppt_db_match[ppt_db_match['max_text_area_group_avg_content_size_rate'] <= 2]
            elif max_text_area_group_avg_content_size < 10:
                ppt_db_match = ppt_db_match[ppt_db_match['max_text_area_group_avg_content_size_rate'] <= 3]



            ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                        'max_text_area_group_avg_content_size_diff',
                                                        'shape_diff',
                                                        'max_text_content_diff',
                                                        'max_text_area_diff_norm',
                                                        'max_graphic_area_diff_norm'],
                                                    ascending=[True, True, True, True, True, True])
        else:
            ppt_db_match = ppt_db_match[2*ppt_db_match['max_text_font_group_avg_content_size'] >= max_text_font_group_avg_content_size]


            if max_text_font_group_avg_content_size >= 10:
                ppt_db_match = ppt_db_match[ppt_db_match['max_text_font_group_avg_content_size_rate'] <= 2]
            elif max_text_font_group_avg_content_size < 10:
                ppt_db_match = ppt_db_match[ppt_db_match['max_text_font_group_avg_content_size_rate'] <= 3]

            ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                        'max_text_font_group_avg_content_size_diff',
                                                        'shape_diff',
                                                        'max_text_content_diff',
                                                        'max_text_area_diff_norm',
                                                        'max_graphic_area_diff_norm'],
                                                    ascending=[True, True, True, True, True, True])


    else:

        if max_text_content >= 10:
            ppt_db_match = ppt_db_match[ppt_db_match['max_text_content_rate'] <= 2]
        elif max_text_content < 10:
            ppt_db_match = ppt_db_match[ppt_db_match['max_text_content_rate'] <= 3]

        ppt_db_match = ppt_db_match.sort_values(by=['text_diff',
                                                    'shape_diff',
                                                    'max_text_content_diff',
                                                    'max_text_area_diff_norm',
                                                    'max_graphic_area_diff_norm'],
                                                ascending=[True, True, True, True, True])

    print('第三次筛选: ', str(len(ppt_db_match)))
    ppt_db_match_index = ppt_db_match.index
    for i in range(len(ppt_db_match)):
        print(ppt_db_match.loc[ppt_db_match_index[i]]['file_name'],
              ' text_type ',ppt_db_match.loc[ppt_db_match_index[i]]['text_type'],
              ' tuwen_layout ',ppt_db_match.loc[ppt_db_match_index[i]]['tuwen_layout'],
              ' rgraph_type ',ppt_db_match.loc[ppt_db_match_index[i]]['rgraph_type'])

    ppt_db_match['text_type_rank'] = ppt_db_match['text_type'].apply(lambda x:text_type.index(x))
    ppt_db_match['tuwen_layout_rank'] = ppt_db_match['tuwen_layout'].apply(lambda x:tuwen_layout.index(x))
    ppt_db_match['rgraph_type_rank'] = ppt_db_match['rgraph_type'].apply(lambda x:rgraph_type.index(x))
    ppt_db_match['origin_rank'] = range(len(ppt_db_match))

    # ppt_db_match = ppt_db_match.sort_values(by=['text_type_rank',
    #                                             'tuwen_layout_rank',
    #                                             'rgraph_type_rank',
    #                                             'origin_rank'],
    #                                                 ascending=[True, True, True, True])
    #目前先不考虑rgraph_type_rank
    ppt_db_match = ppt_db_match.sort_values(by=['text_type_rank',
                                                'tuwen_layout_rank',
                                                'origin_rank'],
                                            ascending=[True, True, True])
    print(''
          '\n'
          '\n'
          '\n')




    print('第四次类型筛选: ', str(len(ppt_db_match)))
    ppt_db_match_index = ppt_db_match.index
    for i in range(len(ppt_db_match)):
        print(ppt_db_match.loc[ppt_db_match_index[i]]['file_name'],
              ' text_type ', ppt_db_match.loc[ppt_db_match_index[i]]['text_type'],
              ' tuwen_layout ', ppt_db_match.loc[ppt_db_match_index[i]]['tuwen_layout'],
              ' rgraph_type ', ppt_db_match.loc[ppt_db_match_index[i]]['rgraph_type'])

    return ppt_db_match,second_flag,query_df,query_all_info_df

def deal_pair(query_df,query_all_info_df):
    max_font_group = query_df.iloc[0]['max_font_group']
    max_text_group = query_df.iloc[0]['max_text_group']
    max_text_group_num = query_df.iloc[0]['max_text_group_num']
    max_font_group_num = query_df.iloc[0]['max_font_group_num']
    pair_flag = False
    if max_font_group % 2 == 0 and max_font_group >= 4 and max_font_group >= 2 * max_text_group:
        text_query_df_font_group = \
            query_all_info_df[query_all_info_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                       'font-name',
                                                                                       'font-weight',
                                                                                       'font-size-asian',
                                                                                       'font-name-asian',
                                                                                       'font-style'],
                                                                                      as_index=False)[
                'class'].count()

        font_group_font_size = text_query_df_font_group.iloc[0]['font-size']
        font_group_font_name = text_query_df_font_group.iloc[0]['font-name']
        font_group_font_weight = text_query_df_font_group.iloc[0]['font-weight']
        font_group_font_size_asian = text_query_df_font_group.iloc[0]['font-size-asian']
        font_group_font_name_asian = text_query_df_font_group.iloc[0]['font-name-asian']
        font_group_font_style = text_query_df_font_group.iloc[0]['font-style']

        query_all_info_font_df = query_all_info_df[(query_all_info_df['class'] != 'TitleTextShape') &
                                                   (query_all_info_df['font-size'] == font_group_font_size) &
                                                   (query_all_info_df['font-name'] == font_group_font_name) &
                                                   (query_all_info_df['font-weight'] == font_group_font_weight) &
                                                   (query_all_info_df['font-size-asian'] == font_group_font_size_asian) &
                                                   (query_all_info_df['font-name-asian'] == font_group_font_name_asian) &
                                                   (query_all_info_df['font-style'] == font_group_font_style)]

        avg_content_size = query_all_info_font_df['content_size'].mean()
        avg_content_size_lt = query_all_info_font_df[query_all_info_font_df['content_size'] < avg_content_size]
        avg_content_size_lt_num = len(avg_content_size_lt)
        if max_font_group == 2 * avg_content_size_lt_num:
            max_font_group = max_font_group / 2

            if pair_flag == False:
                pair_flag = True
                font_pair_flag = True
                max_font_group_num = max_font_group_num + 1
                avg_content_size_gt = query_all_info_font_df[query_all_info_font_df['content_size'] >= avg_content_size]
                avg_content_size_lt = avg_content_size_lt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
                avg_content_size_gt = avg_content_size_gt.sort_values(['shape_y', 'shape_x'], ascending=[True, True])

                for i in range(avg_content_size_lt_num):
                    lt_key = avg_content_size_lt.iloc[i]['key']
                    lt_name = avg_content_size_lt.iloc[i]['name']

                    gt_key = avg_content_size_gt.iloc[i]['key']
                    gt_name = avg_content_size_gt.iloc[i]['name']

                    query_all_info_df.loc[
                        (query_all_info_df['key'] == lt_key) & (query_all_info_df['name'] == lt_name), 'pair'] = str(
                        lt_key) + '_' + '0'
                    query_all_info_df.loc[
                        (query_all_info_df['key'] == gt_key) & (query_all_info_df['name'] == gt_name), 'pair'] = str(
                        lt_key) + '_' + '1'

    return query_all_info_df
