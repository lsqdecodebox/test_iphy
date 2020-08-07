import os
import pandas as pd
def get_stat_db(one_df,cur_index):
    '''
    单页ppt统计量
    :param one_df:
    :return:
    '''
    one_ppt = {}
    one_ppt['file_name'] = one_df.iloc[0]['file_name']
    subject_class = list(one_df['subject'].unique())
    if 'texts' in subject_class:

        text_one_df = one_df[one_df['subject'] == 'texts']
        text_one_df['font-name'].fillna('none',inplace=True)
        text_one_df['font-name-asian'].fillna('none',inplace=True)
        text_one_df['new_class'] = 'none'
        text_len = len(text_one_df)
        text_class = list(text_one_df['class'].unique())
        text_one_df_area_group = text_one_df.groupby(['shape_area'], as_index=False)['class'].count()
        text_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        max_text_group = max(text_one_df_area_group['count'])

        # 字体
        text_df_font_group = text_one_df.groupby(['font-size',
                                                  'font-name',
                                                  'font-weight',
                                                  'font-size-asian',
                                                  'font-name-asian',
                                                  'font-style'],
                                                 as_index=False)['class'].count()
        text_df_font_group.rename(columns={'class': 'count'}, inplace=True)
        max_font_group = max(text_df_font_group['count'])

        if 'Table' in text_class:
            table_len = len(text_one_df[text_one_df['class'] == 'Table'])
        else:
            table_len = 0

        if 'TitleTextShape' in text_class:
            title_len = len(text_one_df[text_one_df['class'] == 'TitleTextShape'])
        else:
            title_len = 0



        if 'OutlinerShape' in text_class:
            outline_len = len(text_one_df[text_one_df['class'] == 'OutlinerShape'])
        else:
            outline_len = 0

        estimate_title_len = len(text_one_df[text_one_df['estimate_title'] == 1])

        new_title_len = 0
        # new_title_len = 1,表示只有唯一的一个estimate_title,也就是estimate_title_num = 1
        if title_len == 0 and outline_len == 0:
            # 制造新的title
            new_title = []
            for i in range(text_len):
                one_text = text_one_df[i:i + 1]
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
                text_one_df.loc[new_title[0], 'new_class'] = 'title'
            else:
                new_title_len = 0
    else:
        text_len = 0
        max_text_group = 0
        table_len = 0
        title_len = 0
        outline_len = 0
        new_title_len = 0
        max_font_group = 0
        estimate_title_len = 0

    if 'shape' in subject_class:
        shape_one_df = one_df[one_df['subject'] == 'shape']
        shape_len = len(shape_one_df)

        shape_class = list(shape_one_df['class'].unique())

        shape_one_df_area_group = shape_one_df.groupby(['shape_area'], as_index=False)['class'].count()
        shape_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        max_shape_group = max(shape_one_df_area_group['count'])
        if 'Chart' in shape_class:
            chart_len = len(shape_one_df[shape_one_df['class'] == 'Chart'])
        else:
            chart_len = 0

        if 'GraphicObjectShape' in shape_class:
            graphic_len = len(shape_one_df[shape_one_df['class'] == 'GraphicObjectShape'])
            graphic_one_df = shape_one_df[shape_one_df['class'] == 'GraphicObjectShape']
            graphic_one_df_area_group = graphic_one_df.groupby(['shape_area'], as_index=False)['class'].count()
            graphic_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
            max_graphic_group = max(graphic_one_df_area_group['count'])
        else:
            graphic_len = 0
            max_graphic_group = 0
    else:
        shape_len = 0
        max_shape_group = 0
        chart_len = 0
        graphic_len = 0
        max_graphic_group = 0

    one_ppt['max_text_group'] = max_text_group
    one_ppt['max_shape_group'] = max_shape_group
    one_ppt['max_graphic_group'] = max_graphic_group

    one_ppt['text_num'] = text_len
    one_ppt['shape_num'] = shape_len
    one_ppt['table_num'] = table_len
    one_ppt['graphic_num'] = graphic_len
    one_ppt['chart_num'] = chart_len
    one_ppt['outline_num'] = outline_len
    one_ppt['title_num'] = title_len
    one_ppt['estimate_title_num'] = estimate_title_len
    one_ppt['new_title_num'] = new_title_len
    one_ppt['max_font_group'] = max_font_group

    one_stat = pd.DataFrame(one_ppt,index=[cur_index])

    return one_stat

def get_stat_db_2(one_df,cur_index):
    '''
    单页ppt统计量
    :param one_df:
    :return:
    '''
    # 初始变量
    max_text_area = 0
    avg_text_area = 0
    max_shape_area = 0
    avg_shape_area = 0
    max_graphic_area = 0
    avg_graphic_area = 0
    max_text_content = 0
    avg_text_content = 0
    max_text_area_group = 0
    max_text_area_group_avg_content_size = 0
    max_text_font_group_avg_content_size = 0

    one_ppt = {}
    one_ppt['file_name'] = one_df.iloc[0]['file_name']
    one_ppt['width'] = one_df.iloc[0]['width']
    one_ppt['height'] = one_df.iloc[0]['height']
    subject_class = list(one_df['subject'].unique())
    if 'texts' in subject_class:

        text_one_df = one_df[one_df['subject'] == 'texts']
        text_one_df['font-name'].fillna('none',inplace=True)
        text_one_df['font-name-asian'].fillna('none',inplace=True)
        text_one_df['new_class'] = 'none'
        text_len = len(text_one_df)
        text_class = list(text_one_df['class'].unique())
        text_one_df_area_group = text_one_df[text_one_df['class'] != 'TitleTextShape'].groupby(['shape_area'], as_index=False)['class'].count()
        text_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        max_text_group = max(text_one_df_area_group['count'])

        if max_text_group > 2:
            text_one_df_area_group = text_one_df_area_group.sort_values(['count', 'shape_area'],
                                                                          ascending=[False, False])
            max_text_area_group = text_one_df_area_group.iloc[0]['shape_area']

            max_text_area_df = text_one_df[
                (text_one_df['class'] != 'TitleTextShape') & (text_one_df['shape_area'] == max_text_area_group)]

            max_text_area_group_avg_content_size = max_text_area_df['content_size'].mean()

        # 字体
        text_df_font_group = text_one_df[text_one_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                  'font-name',
                                                  'font-weight',
                                                  'font-size-asian',
                                                  'font-name-asian',
                                                  'font-style'],
                                                 as_index=False)['class'].count()
        text_df_font_group.rename(columns={'class': 'count'}, inplace=True)

        max_font_group = max(text_df_font_group['count'])







        if 'Table' in text_class:
            table_len = len(text_one_df[text_one_df['class'] == 'Table'])
        else:
            table_len = 0

        if 'TitleTextShape' in text_class:
            title_len = len(text_one_df[text_one_df['class'] == 'TitleTextShape'])
        else:
            title_len = 0



        if 'OutlinerShape' in text_class:
            outline_len = len(text_one_df[text_one_df['class'] == 'OutlinerShape'])
        else:
            outline_len = 0

        estimate_title_len = len(text_one_df[text_one_df['estimate_title'] == 1])

        new_title_len = 0
        # new_title_len = 1,表示只有唯一的一个estimate_title,也就是estimate_title_num = 1
        if title_len == 0 and outline_len == 0:
            # 制造新的title
            new_title = []
            for i in range(text_len):
                one_text = text_one_df[i:i + 1]
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
                text_one_df.loc[new_title[0], 'new_class'] = 'title'
            else:
                new_title_len = 0
        # 针对area
        text_one_area_df = text_one_df['shape_area'].describe()
        max_text_area = text_one_area_df['max']
        avg_text_area = text_one_area_df['mean']

        text_one_content_df = text_one_df['content_size'].describe()
        max_text_content = text_one_content_df['max']
        avg_text_content = text_one_content_df['mean']



    else:
        text_len = 0
        max_text_group = 0
        table_len = 0
        title_len = 0
        outline_len = 0
        new_title_len = 0
        max_font_group = 0
        estimate_title_len = 0

    if 'shape' in subject_class:
        shape_one_df = one_df[one_df['subject'] == 'shape']
        shape_len = len(shape_one_df)

        shape_class = list(shape_one_df['class'].unique())

        shape_one_df_area_group = shape_one_df.groupby(['shape_area'], as_index=False)['class'].count()
        shape_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        max_shape_group = max(shape_one_df_area_group['count'])
        if 'Chart' in shape_class:
            chart_len = len(shape_one_df[shape_one_df['class'] == 'Chart'])
        else:
            chart_len = 0

        if 'GraphicObjectShape' in shape_class:
            graphic_len = len(shape_one_df[shape_one_df['class'] == 'GraphicObjectShape'])
            graphic_one_df = shape_one_df[shape_one_df['class'] == 'GraphicObjectShape']
            graphic_one_df_area_group = graphic_one_df.groupby(['shape_area'], as_index=False)['class'].count()
            graphic_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
            max_graphic_group = max(graphic_one_df_area_group['count'])

            graphic_one_area_df = graphic_one_df['shape_area'].describe()
            max_graphic_area = graphic_one_area_df['max']
            avg_graphic_area = graphic_one_area_df['mean']
        else:
            graphic_len = 0
            max_graphic_group = 0

        shape_one_area_df = shape_one_df['shape_area'].describe()
        max_shape_area = shape_one_area_df['max']
        avg_shape_area = shape_one_area_df['mean']
    else:
        shape_len = 0
        max_shape_group = 0
        chart_len = 0
        graphic_len = 0
        max_graphic_group = 0

    one_ppt['max_text_group'] = max_text_group
    one_ppt['max_shape_group'] = max_shape_group
    one_ppt['max_graphic_group'] = max_graphic_group

    one_ppt['text_num'] = text_len
    one_ppt['shape_num'] = shape_len
    one_ppt['table_num'] = table_len
    one_ppt['graphic_num'] = graphic_len
    one_ppt['chart_num'] = chart_len
    one_ppt['outline_num'] = outline_len
    one_ppt['title_num'] = title_len
    one_ppt['estimate_title_num'] = estimate_title_len
    one_ppt['new_title_num'] = new_title_len
    one_ppt['max_font_group'] = max_font_group

    one_ppt['max_text_area'] = max_text_area
    one_ppt['avg_text_area'] = avg_text_area
    one_ppt['max_text_content'] = max_text_content
    one_ppt['avg_text_content'] = avg_text_content
    one_ppt['max_shape_area'] = max_shape_area
    one_ppt['avg_shape_area'] = avg_shape_area
    one_ppt['max_graphic_area'] = max_graphic_area
    one_ppt['avg_graphic_area'] = avg_graphic_area
    one_ppt['max_text_area_group'] = max_text_area_group
    one_ppt['max_text_area_group_avg_content_size'] = max_text_area_group_avg_content_size
    one_ppt['max_text_font_group_avg_content_size'] = max_text_font_group_avg_content_size


    one_stat = pd.DataFrame(one_ppt,index=[cur_index])

    return one_stat



def get_query_stat_db(one_df,cur_index):
    '''
    单页ppt，这里单页，指的是查询的统计量，和db有小小的差异，后面是要整合的
    :param one_df:
    :param cur_index:
    :return:
    '''

    one_ppt = {}
    one_ppt['file_name'] = one_df.iloc[0]['file_name']
    subject_class = list(one_df['subject'].unique())
    if 'texts' in subject_class:

        text_query_df = one_df[one_df['subject'] == 'texts']
        text_query_df['font-name'].fillna('none', inplace=True)
        text_query_df['font-name-asian'].fillna('none', inplace=True)

        # 判断是不是title
        text_query_df['new_class'] = 'none'
        text_query_df['area_group'] = 1
        text_query_df['font_group'] = 1
        text_query_df['class_bak'] = text_query_df['class']
        text_len = len(text_query_df)
        text_class = list(text_query_df['class'].unique())

        if 'TitleTextShape' in text_class:
            title_len = len(text_query_df[text_query_df['class'] == 'TitleTextShape'])
        else:
            title_len = 0

        if 'OutlinerShape' in text_class:
            outline_len = len(text_query_df[text_query_df['class'] == 'OutlinerShape'])
        else:
            outline_len = 0

        estimate_title_len = len(text_query_df[text_query_df['estimate_title'] == 1])


        new_title_len = 0
        if title_len == 0 and outline_len == 0:
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

        text_query_df_area_group = \
        text_query_df[text_query_df['class'] != 'TitleTextShape'].groupby(['shape_area'], as_index=False)[
            'class'].count()
        text_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        if len(text_query_df_area_group) == 0:
            max_text_group = 1
        else:
            max_text_group = max(text_query_df_area_group['count'])

        for i in range(len(text_query_df_area_group)):
            area = text_query_df_area_group.iloc[i]['shape_area']
            count = text_query_df_area_group.iloc[i]['count']
            text_query_df['area_group'][text_query_df['shape_area'] == area] = count

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
        if len(text_query_df_font_group) != 0:
            max_font_group = max(text_query_df_font_group['count'])
        else:
            max_font_group = 1

        for i in range(len(text_query_df_font_group)):
            font_size = text_query_df_font_group.iloc[i]['font-size']
            font_name = text_query_df_font_group.iloc[i]['font-name']
            font_weight = text_query_df_font_group.iloc[i]['font-weight']
            font_size_asian = text_query_df_font_group.iloc[i]['font-size-asian']
            font_name_asian = text_query_df_font_group.iloc[i]['font-name-asian']
            font_style = text_query_df_font_group.iloc[i]['font-style']
            count = text_query_df_font_group.iloc[i]['count']
            text_query_df['font_group'][(text_query_df['font-size'] == font_size) &
                                        (text_query_df['font-name'] == font_name) &
                                        (text_query_df['font-weight'] == font_weight) &
                                        (text_query_df['font-size-asian'] == font_size_asian) &
                                        (text_query_df['font-name-asian'] == font_name_asian) &
                                        (text_query_df['font-style'] == font_style)] = count

        if 'Table' in text_class:
            table_len = len(text_query_df[text_query_df['class'] == 'Table'])
        else:
            table_len = 0







    else:
        text_len = 0
        max_text_group = 0
        table_len = 0
        title_len = 0
        outline_len = 0
        max_font_group = 0
        new_title_len = 0

    if 'shape' in subject_class:
        shape_query_df = one_df[one_df['subject'] == 'shape']
        shape_query_df['graphic_area_group'] = 1
        shape_len = len(shape_query_df)

        shape_class = list(shape_query_df['class'].unique())

        shape_query_df_area_group = shape_query_df.groupby(['shape_area'], as_index=False)['class'].count()
        shape_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        max_shape_group = max(shape_query_df_area_group['count'])
        if 'Chart' in shape_class:
            chart_len = len(shape_query_df[shape_query_df['class'] == 'Chart'])
        else:
            chart_len = 0

        if 'GraphicObjectShape' in shape_class:
            graphic_len = len(shape_query_df[shape_query_df['class'] == 'GraphicObjectShape'])
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']
            graphic_query_df_area_group = graphic_query_df.groupby(['shape_area'], as_index=False)['class'].count()
            graphic_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)

            for i in range(len(graphic_query_df_area_group)):
                area = graphic_query_df_area_group.iloc[i]['shape_area']
                count = graphic_query_df_area_group.iloc[i]['count']
                shape_query_df['graphic_area_group'][(shape_query_df['shape_area'] == area)
                                                     & (shape_query_df['class'] == 'GraphicObjectShape')] = count

            max_graphic_group = max(graphic_query_df_area_group['count'])



        else:
            graphic_len = 0
            max_graphic_group = 0
    else:
        shape_len = 0
        max_shape_group = 0
        chart_len = 0
        graphic_len = 0
        max_graphic_group = 0
        estimate_title_len = 0

    one_ppt['max_text_group'] = max_text_group
    one_ppt['max_shape_group'] = max_shape_group
    one_ppt['max_graphic_group'] = max_graphic_group

    one_ppt['text_num'] = text_len
    one_ppt['shape_num'] = shape_len
    one_ppt['table_num'] = table_len
    one_ppt['graphic_num'] = graphic_len
    one_ppt['chart_num'] = chart_len
    one_ppt['outline_num'] = outline_len
    one_ppt['title_num'] = title_len
    one_ppt['estimate_title_num'] = estimate_title_len
    one_ppt['new_title_num'] = new_title_len
    one_ppt['max_font_group'] = max_font_group

    one_stat = pd.DataFrame(one_ppt, index=[cur_index])

    return one_stat


def get_query_stat_db_2(one_df, cur_index):
    '''
    单页ppt，这里单页，指的是查询的统计量，和db有小小的差异，后面是要整合的
    :param one_df:
    :param cur_index:
    :return:
    '''
    max_text_area = 0
    avg_text_area = 0
    max_shape_area = 0
    avg_shape_area = 0
    max_graphic_area = 0
    avg_graphic_area = 0
    max_text_content = 0
    avg_text_content = 0
    max_text_area_group = 0
    max_text_area_group_avg_content_size = 0
    max_text_font_group_avg_content_size = 0
    one_ppt = {}
    one_ppt['file_name'] = one_df.iloc[0]['file_name']
    one_ppt['width'] = one_df.iloc[0]['width']
    one_ppt['height'] = one_df.iloc[0]['height']
    subject_class = list(one_df['subject'].unique())
    if 'texts' in subject_class:

        text_query_df = one_df[one_df['subject'] == 'texts']
        text_query_df['font-name'].fillna('none', inplace=True)
        text_query_df['font-name-asian'].fillna('none', inplace=True)

        # 判断是不是title
        text_query_df['new_class'] = 'none'
        text_query_df['area_group'] = 1
        text_query_df['font_group'] = 1
        text_query_df['class_bak'] = text_query_df['class']
        text_len = len(text_query_df)
        text_class = list(text_query_df['class'].unique())

        if 'TitleTextShape' in text_class:
            title_len = len(text_query_df[text_query_df['class'] == 'TitleTextShape'])
        else:
            title_len = 0

        if 'OutlinerShape' in text_class:
            outline_len = len(text_query_df[text_query_df['class'] == 'OutlinerShape'])
        else:
            outline_len = 0

        estimate_title_len = len(text_query_df[text_query_df['estimate_title'] == 1])

        new_title_len = 0
        if title_len == 0 and outline_len == 0:
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

        text_query_df_area_group = \
            text_query_df[text_query_df['class'] != 'TitleTextShape'].groupby(['shape_area'], as_index=False)[
                'class'].count()
        text_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        if len(text_query_df_area_group) == 0:
            max_text_group = 1
        else:
            max_text_group = max(text_query_df_area_group['count'])


        if max_text_group > 2:
            text_query_df_area_group = text_query_df_area_group.sort_values(['count', 'shape_area'],
                                                                          ascending=[False, False])
            max_text_area_group = text_query_df_area_group.iloc[0]['shape_area']

            max_text_area_df = text_query_df[(text_query_df['class'] != 'TitleTextShape') & (text_query_df['shape_area'] == max_text_area_group)]

            max_text_area_group_avg_content_size = max_text_area_df['content_size'].mean()



        # 字体
        text_query_df_font_group = \
            text_query_df[text_query_df['class'] != 'TitleTextShape'].groupby(
                ['font-size','font-name','font-weight','font-size-asian','font-name-asian','font-style'],as_index=False)['class'].count()

        text_query_df_font_group.rename(columns={'class': 'count'}, inplace=True)
        if len(text_query_df_font_group) != 0:
            max_font_group = max(text_query_df_font_group['count'])
        else:
            max_font_group = 1

        if max_font_group > 2:
            text_query_df_font_group = text_query_df_font_group.sort_values(['count', 'font-size'],
                                                                            ascending=[False, False])
            query_font_size = text_query_df_font_group.iloc[0]['font-size']
            query_font_name = text_query_df_font_group.iloc[0]['font-name']
            query_font_weight = text_query_df_font_group.iloc[0]['font-weight']
            query_font_size_asian = text_query_df_font_group.iloc[0]['font-size-asian']
            query_font_name_asian = text_query_df_font_group.iloc[0]['font-name-asian']
            query_font_style = text_query_df_font_group.iloc[0]['font-style']

            max_text_font_df = text_query_df[(text_query_df['class'] != 'TitleTextShape') &
                                             (text_query_df['font-size'] == query_font_size) &
                                             (text_query_df['font-name'] == query_font_name) &
                                             (text_query_df['font-weight'] == query_font_weight) &
                                             (text_query_df['font-size-asian'] == query_font_size_asian) &
                                             (text_query_df['font-name-asian'] == query_font_name_asian) &
                                             (text_query_df['font-style'] == query_font_style)]

            max_text_font_group_avg_content_size = max_text_font_df['content_size'].mean()






        if 'Table' in text_class:
            table_len = len(text_query_df[text_query_df['class'] == 'Table'])
        else:
            table_len = 0
        text_one_area_df = text_query_df['shape_area'].describe()
        max_text_area = text_one_area_df['max']
        avg_text_area = text_one_area_df['mean']

        text_query_df['content_size'] = text_query_df['content_size'].values.astype(float)
        text_one_content_df = text_query_df['content_size'].describe()
        # print(text_one_content_df)
        max_text_content = text_one_content_df['max']
        avg_text_content = text_one_content_df['mean']

    else:
        text_len = 0
        max_text_group = 0
        table_len = 0
        title_len = 0
        outline_len = 0
        max_font_group = 0
        new_title_len = 0

    if 'shape' in subject_class:
        shape_query_df = one_df[one_df['subject'] == 'shape']
        shape_query_df['graphic_area_group'] = 1
        shape_len = len(shape_query_df)

        shape_class = list(shape_query_df['class'].unique())

        shape_query_df_area_group = shape_query_df.groupby(['shape_area'], as_index=False)['class'].count()
        shape_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        max_shape_group = max(shape_query_df_area_group['count'])
        if 'Chart' in shape_class:
            chart_len = len(shape_query_df[shape_query_df['class'] == 'Chart'])
        else:
            chart_len = 0

        if 'GraphicObjectShape' in shape_class:
            graphic_len = len(shape_query_df[shape_query_df['class'] == 'GraphicObjectShape'])
            graphic_query_df = shape_query_df[shape_query_df['class'] == 'GraphicObjectShape']
            graphic_query_df_area_group = graphic_query_df.groupby(['shape_area'], as_index=False)['class'].count()
            graphic_query_df_area_group.rename(columns={'class': 'count'}, inplace=True)
            max_graphic_group = max(graphic_query_df_area_group['count'])

            graphic_one_area_df = graphic_query_df['shape_area'].describe()
            max_graphic_area = graphic_one_area_df['max']
            avg_graphic_area = graphic_one_area_df['mean']




        else:
            graphic_len = 0
            max_graphic_group = 0

        shape_one_area_df = shape_query_df['shape_area'].describe()
        max_shape_area = shape_one_area_df['max']
        avg_shape_area = shape_one_area_df['mean']

    else:
        shape_len = 0
        max_shape_group = 0
        chart_len = 0
        graphic_len = 0
        max_graphic_group = 0
        estimate_title_len = 0

    one_ppt['max_text_group'] = max_text_group
    one_ppt['max_shape_group'] = max_shape_group
    one_ppt['max_graphic_group'] = max_graphic_group

    one_ppt['text_num'] = text_len
    one_ppt['shape_num'] = shape_len
    one_ppt['table_num'] = table_len
    one_ppt['graphic_num'] = graphic_len
    one_ppt['chart_num'] = chart_len
    one_ppt['outline_num'] = outline_len
    one_ppt['title_num'] = title_len
    one_ppt['estimate_title_num'] = estimate_title_len
    one_ppt['new_title_num'] = new_title_len
    one_ppt['max_font_group'] = max_font_group

    one_ppt['max_text_area'] = max_text_area
    one_ppt['avg_text_area'] = avg_text_area
    one_ppt['max_text_content'] = max_text_content
    one_ppt['avg_text_content'] = avg_text_content
    one_ppt['max_shape_area'] = max_shape_area
    one_ppt['avg_shape_area'] = avg_shape_area
    one_ppt['max_graphic_area'] = max_graphic_area
    one_ppt['avg_graphic_area'] = avg_graphic_area

    one_ppt['max_text_area_group'] = max_text_area_group
    one_ppt['max_text_area_group_avg_content_size'] = max_text_area_group_avg_content_size
    one_ppt['max_text_font_group_avg_content_size'] = max_text_font_group_avg_content_size


    one_stat = pd.DataFrame(one_ppt, index=[cur_index])

    return one_stat

def get_stat_db_3(one_df, cur_index):
    max_text_area = 0
    avg_text_area = 0
    max_shape_area = 0
    avg_shape_area = 0
    max_graphic_area = 0
    avg_graphic_area = 0
    max_text_content = 0
    avg_text_content = 0
    max_text_area_group = 0
    max_text_area_group_avg_content_size = 0
    max_text_font_group_avg_content_size = 0
    max_text_group_num = 0
    max_font_group_num = 0
    max_graphic_group_num = 0
    font_size_estimate_title_len = 0

    one_ppt = {}
    one_ppt['file_name'] = one_df.iloc[0]['file_name']
    one_ppt['width'] = one_df.iloc[0]['width']
    one_ppt['height'] = one_df.iloc[0]['height']
    subject_class = list(one_df['subject'].unique())

    if 'texts' in subject_class:

        text_one_df = one_df[one_df['subject'] == 'texts']
        text_one_df['font-name'].fillna('none', inplace=True)
        text_one_df['font-name-asian'].fillna('none', inplace=True)
        text_one_df.loc[:,'new_class'] = 'none'

        text_len = len(text_one_df)
        text_class = list(text_one_df['class'].unique())

        if 'TitleTextShape' in text_class:
            title_len = len(text_one_df[text_one_df['class'] == 'TitleTextShape'])
        else:
            title_len = 0

        if 'OutlinerShape' in text_class:
            outline_len = len(text_one_df[text_one_df['class'] == 'OutlinerShape'])
        else:
            outline_len = 0

        estimate_title_len = len(text_one_df[text_one_df['estimate_title'] == 1])

        # 这个根据编码的情况
        '''
        这个根据编码的情况
        '''
        font_size_estimate_title_len = 0

        #font_size_estimate_title_len = len(text_one_df[text_one_df['font_size_estimate_title'] == 1])

        new_title_len = 0  # new_title_len = 1,表示只有唯一的一个estimate_title,也就是estimate_title_num = 1
        new_font_title_len = 0
        if title_len == 0 and outline_len == 0:
            # 制造新的title
            new_title = []
            # 根据字体大小判断title
            font_size_new_title = []
            font_size_seq = []

            # if text_len >= 2:
            #     text_one_font_df = text_one_df.copy()
            #     text_one_font_df = text_one_font_df.sort_values(['font-size'],ascending=[False])
            #     text_one_font_df = text_one_font_df[~text_one_font_df.content.str.match('\d+')]
            #     if len(text_one_font_df) >= 2:
            #         first_text_one_font_size = int(text_one_font_df.iloc[0]['font-size'].replace('pt',''))
            #         first_text_one_content_size = int(text_one_font_df.iloc[0]['font-size'])
            #         second_text_one_font_size = int(text_one_font_df.iloc[1]['font-size'].replace('pt',''))
            #         if first_text_one_font_size > (3/2)*second_text_one_font_size and first_text_one_content_size <= 15:
            #             new_font_title_len = 1


            for i in range(text_len):
                one_text = text_one_df[i:i + 1]
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
                text_one_df.loc[new_title[0], 'new_class'] = 'title'

            else:
                new_title_len = 0

        if title_len > 1:
            title_text_query_df = text_one_df[text_one_df['class'] == 'TitleTextShape']

            title_text_query_df = title_text_query_df.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
            top_key = title_text_query_df.iloc[0]['key']
            all_key = list(title_text_query_df['key'].unique())
            all_key.remove(top_key)
            for key in all_key:
                text_one_df['class'][text_one_df['key'] == key] = 'TextShape'

        text_one_df_area_group = \
        text_one_df[text_one_df['class'] != 'TitleTextShape'].groupby(['shape_area'], as_index=False)['class'].count()
        text_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)

        if len(text_one_df_area_group) == 0:
            max_text_group = 1
        else:
            max_text_group = max(text_one_df_area_group['count'])

        if max_text_group >= 2:
            text_one_df_area_group = text_one_df_area_group.sort_values(['count', 'shape_area'],
                                                                        ascending=[False, False])
            max_text_area_group = text_one_df_area_group.iloc[0]['shape_area']
            max_text_area_df = text_one_df[
                (text_one_df['class'] != 'TitleTextShape') & (text_one_df['shape_area'] == max_text_area_group)]
            max_text_area_group_avg_content_size = max_text_area_df['content_size'].mean()

            max_text_group_num = len(text_one_df_area_group[text_one_df_area_group['count'] == max_text_group])





        # 字体
        text_df_font_group = text_one_df[text_one_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                            'font-name',
                                                                                            'font-weight',
                                                                                            'font-size-asian',
                                                                                            'font-name-asian',
                                                                                            'font-style'],
                                                                                           as_index=False)[
            'class'].count()
        text_df_font_group.rename(columns={'class': 'count'}, inplace=True)
        if len(text_df_font_group) != 0:
            max_font_group = max(text_df_font_group['count'])
        else:
            max_font_group = 1

        if max_font_group >= 2:
            text_df_font_group = text_df_font_group.sort_values(['count', 'font-size'],
                                                                ascending=[False, False])
            query_font_size = text_df_font_group.iloc[0]['font-size']
            query_font_name = text_df_font_group.iloc[0]['font-name']
            query_font_weight = text_df_font_group.iloc[0]['font-weight']
            query_font_size_asian = text_df_font_group.iloc[0]['font-size-asian']
            query_font_name_asian = text_df_font_group.iloc[0]['font-name-asian']
            query_font_style = text_df_font_group.iloc[0]['font-style']
            max_text_font_df = text_one_df[(text_one_df['font-size'] == query_font_size) &
                                                  (text_one_df['font-name'] == query_font_name) &
                                                  (text_one_df['font-weight'] == query_font_weight) &
                                                  (text_one_df['font-size-asian'] == query_font_size_asian) &
                                                  (text_one_df['font-name-asian'] == query_font_name_asian) &
                                                  (text_one_df['font-style'] == query_font_style)]
            max_text_font_group_avg_content_size = max_text_font_df['content_size'].mean()

            max_font_group_num = len(text_df_font_group[text_df_font_group['count'] == max_font_group])

        if 'Table' in text_class:
            table_len = len(text_one_df[text_one_df['class'] == 'Table'])
        else:
            table_len = 0
        # 针对area
        text_one_area_df = text_one_df['shape_area'].describe()
        max_text_area = text_one_area_df['max']
        avg_text_area = text_one_area_df['mean']
        text_one_df.loc[:,'content_size'] = text_one_df['content_size'].values.astype(float)
        text_one_content_df = text_one_df['content_size'].describe()
        max_text_content = text_one_content_df['max']
        avg_text_content = text_one_content_df['mean']

    else:
        text_len = 0
        max_text_group = 0
        table_len = 0
        title_len = 0
        outline_len = 0
        new_title_len = 0
        max_font_group = 0
        estimate_title_len = 0

    if 'shape' in subject_class:
        shape_one_df = one_df[one_df['subject'] == 'shape']
        shape_len = len(shape_one_df)

        shape_class = list(shape_one_df['class'].unique())

        shape_one_df_area_group = shape_one_df.groupby(['shape_area'], as_index=False)['class'].count()
        shape_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        max_shape_group = max(shape_one_df_area_group['count'])
        if 'Chart' in shape_class:
            chart_len = len(shape_one_df[shape_one_df['class'] == 'Chart'])
        else:
            chart_len = 0

        if 'GraphicObjectShape' in shape_class:
            graphic_len = len(shape_one_df[shape_one_df['class'] == 'GraphicObjectShape'])
            graphic_one_df = shape_one_df[shape_one_df['class'] == 'GraphicObjectShape']
            graphic_one_df_area_group = graphic_one_df.groupby(['shape_area'], as_index=False)['class'].count()
            graphic_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
            max_graphic_group = max(graphic_one_df_area_group['count'])


            if max_graphic_group >= 2:
                max_graphic_group_num = len(graphic_one_df_area_group[graphic_one_df_area_group['count'] == max_graphic_group])




            graphic_one_area_df = graphic_one_df['shape_area'].describe()
            max_graphic_area = graphic_one_area_df['max']
            avg_graphic_area = graphic_one_area_df['mean']
        else:
            graphic_len = 0
            max_graphic_group = 0

        shape_one_area_df = shape_one_df['shape_area'].describe()
        max_shape_area = shape_one_area_df['max']
        avg_shape_area = shape_one_area_df['mean']
    else:
        shape_len = 0
        max_shape_group = 0
        chart_len = 0
        graphic_len = 0
        max_graphic_group = 0
        estimate_title_len = 0

    one_ppt['max_text_group'] = max_text_group
    one_ppt['max_shape_group'] = max_shape_group
    one_ppt['max_graphic_group'] = max_graphic_group
    one_ppt['max_font_group'] = max_font_group

    one_ppt['max_text_group_num'] = max_text_group_num
    one_ppt['max_font_group_num'] = max_font_group_num
    one_ppt['max_graphic_group_num'] = max_graphic_group_num

    one_ppt['text_num'] = text_len
    one_ppt['shape_num'] = shape_len
    one_ppt['table_num'] = table_len
    one_ppt['graphic_num'] = graphic_len
    one_ppt['chart_num'] = chart_len
    one_ppt['outline_num'] = outline_len
    one_ppt['title_num'] = title_len
    one_ppt['estimate_title_num'] = estimate_title_len
    one_ppt['font_size_estimate_title_num'] = font_size_estimate_title_len
    one_ppt['new_title_num'] = new_title_len

    one_ppt['max_text_area'] = max_text_area
    one_ppt['avg_text_area'] = avg_text_area
    one_ppt['max_text_content'] = max_text_content
    one_ppt['avg_text_content'] = avg_text_content
    one_ppt['max_shape_area'] = max_shape_area
    one_ppt['avg_shape_area'] = avg_shape_area
    one_ppt['max_graphic_area'] = max_graphic_area
    one_ppt['avg_graphic_area'] = avg_graphic_area
    one_ppt['max_text_area_group'] = max_text_area_group
    one_ppt['max_text_area_group_avg_content_size'] = max_text_area_group_avg_content_size
    one_ppt['max_text_font_group_avg_content_size'] = max_text_font_group_avg_content_size
    one_stat = pd.DataFrame(one_ppt, index=[cur_index])

    return one_stat

def get_stat_db_4(one_df, cur_index):
    max_text_area = 0
    avg_text_area = 0
    max_shape_area = 0
    avg_shape_area = 0
    max_graphic_area = 0
    avg_graphic_area = 0
    max_text_content = 0
    avg_text_content = 0
    max_text_area_group = 0
    max_text_area_group_avg_content_size = 0
    max_text_font_group_avg_content_size = 0
    max_text_group_num = 0
    max_font_group_num = 0
    max_graphic_group_num = 0
    font_size_estimate_title_len = 0

    one_ppt = {}
    one_ppt['file_name'] = one_df.iloc[0]['file_name']
    one_ppt['width'] = one_df.iloc[0]['width']
    one_ppt['height'] = one_df.iloc[0]['height']
    subject_class = list(one_df['subject'].unique())

    if 'texts' in subject_class:

        text_one_df = one_df[one_df['subject'] == 'texts']
        text_one_df['font-name'].fillna('none', inplace=True)
        text_one_df['font-name-asian'].fillna('none', inplace=True)
        text_one_df['new_class'] = 'none'

        text_len = len(text_one_df)
        text_class = list(text_one_df['class'].unique())

        if 'TitleTextShape' in text_class:
            title_len = len(text_one_df[text_one_df['class'] == 'TitleTextShape'])
        else:
            title_len = 0

        if 'OutlinerShape' in text_class:
            outline_len = len(text_one_df[text_one_df['class'] == 'OutlinerShape'])
        else:
            outline_len = 0

        estimate_title_len = len(text_one_df[text_one_df['estimate_title'] == 1])

        # 这个根据编码的情况
        '''
        这个根据编码的情况
        '''

        font_size_estimate_title_len = len(text_one_df[text_one_df['font_size_estimate_title'] == 1])

        new_title_len = 0  # new_title_len = 1,表示只有唯一的一个estimate_title,也就是estimate_title_num = 1
        new_font_title_len = 0
        if title_len == 0 and outline_len == 0:
            # 制造新的title
            new_title = []
            # 根据字体大小判断title
            font_size_new_title = []
            font_size_seq = []

            # if text_len >= 2:
            #     text_one_font_df = text_one_df.copy()
            #     text_one_font_df = text_one_font_df.sort_values(['font-size'],ascending=[False])
            #     text_one_font_df = text_one_font_df[~text_one_font_df.content.str.match('\d+')]
            #     if len(text_one_font_df) >= 2:
            #         first_text_one_font_size = int(text_one_font_df.iloc[0]['font-size'].replace('pt',''))
            #         first_text_one_content_size = int(text_one_font_df.iloc[0]['font-size'])
            #         second_text_one_font_size = int(text_one_font_df.iloc[1]['font-size'].replace('pt',''))
            #         if first_text_one_font_size > (3/2)*second_text_one_font_size and first_text_one_content_size <= 15:
            #             new_font_title_len = 1


            for i in range(text_len):
                one_text = text_one_df[i:i + 1]
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
                text_one_df.loc[new_title[0], 'new_class'] = 'title'

            else:
                new_title_len = 0

        if title_len > 1:
            title_text_query_df = text_one_df[text_one_df['class'] == 'TitleTextShape']

            title_text_query_df = title_text_query_df.sort_values(['shape_y', 'shape_x'], ascending=[True, True])
            top_key = title_text_query_df.iloc[0]['key']
            all_key = list(title_text_query_df['key'].unique())
            all_key.remove(top_key)
            for key in all_key:
                text_one_df['class'][text_one_df['key'] == key] = 'TextShape'

        text_one_df_area_group = \
        text_one_df[text_one_df['class'] != 'TitleTextShape'].groupby(['shape_area'], as_index=False)['class'].count()
        text_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)

        if len(text_one_df_area_group) == 0:
            max_text_group = 1
        else:
            max_text_group = max(text_one_df_area_group['count'])

        if max_text_group >= 2:
            text_one_df_area_group = text_one_df_area_group.sort_values(['count', 'shape_area'],
                                                                        ascending=[False, False])
            max_text_area_group = text_one_df_area_group.iloc[0]['shape_area']
            max_text_area_df = text_one_df[
                (text_one_df['class'] != 'TitleTextShape') & (text_one_df['shape_area'] == max_text_area_group)]
            max_text_area_group_avg_content_size = max_text_area_df['content_size'].mean()

            max_text_group_num = len(text_one_df_area_group[text_one_df_area_group['count'] == max_text_group])





        # 字体
        text_df_font_group = text_one_df[text_one_df['class'] != 'TitleTextShape'].groupby(['font-size',
                                                                                            'font-name',
                                                                                            'font-weight',
                                                                                            'font-size-asian',
                                                                                            'font-name-asian',
                                                                                            'font-style'],
                                                                                           as_index=False)[
            'class'].count()
        text_df_font_group.rename(columns={'class': 'count'}, inplace=True)
        if len(text_df_font_group) != 0:
            max_font_group = max(text_df_font_group['count'])
        else:
            max_font_group = 1

        if max_font_group >= 2:
            text_df_font_group = text_df_font_group.sort_values(['count', 'font-size'],
                                                                ascending=[False, False])
            query_font_size = text_df_font_group.iloc[0]['font-size']
            query_font_name = text_df_font_group.iloc[0]['font-name']
            query_font_weight = text_df_font_group.iloc[0]['font-weight']
            query_font_size_asian = text_df_font_group.iloc[0]['font-size-asian']
            query_font_name_asian = text_df_font_group.iloc[0]['font-name-asian']
            query_font_style = text_df_font_group.iloc[0]['font-style']
            max_text_font_df = text_one_df[(text_one_df['font-size'] == query_font_size) &
                                                  (text_one_df['font-name'] == query_font_name) &
                                                  (text_one_df['font-weight'] == query_font_weight) &
                                                  (text_one_df['font-size-asian'] == query_font_size_asian) &
                                                  (text_one_df['font-name-asian'] == query_font_name_asian) &
                                                  (text_one_df['font-style'] == query_font_style)]
            max_text_font_group_avg_content_size = max_text_font_df['content_size'].mean()

            max_font_group_num = len(text_df_font_group[text_df_font_group['count'] == max_font_group])

        if 'Table' in text_class:
            table_len = len(text_one_df[text_one_df['class'] == 'Table'])
        else:
            table_len = 0
        # 针对area
        text_one_area_df = text_one_df['shape_area'].describe()
        max_text_area = text_one_area_df['max']
        avg_text_area = text_one_area_df['mean']
        text_one_df['content_size'] = text_one_df['content_size'].values.astype(float)
        text_one_content_df = text_one_df['content_size'].describe()
        max_text_content = text_one_content_df['max']
        avg_text_content = text_one_content_df['mean']

    else:
        text_len = 0
        max_text_group = 0
        table_len = 0
        title_len = 0
        outline_len = 0
        new_title_len = 0
        max_font_group = 0
        estimate_title_len = 0

    if 'shape' in subject_class:
        shape_one_df = one_df[one_df['subject'] == 'shape']
        shape_len = len(shape_one_df)

        shape_class = list(shape_one_df['class'].unique())

        shape_one_df_area_group = shape_one_df.groupby(['shape_area'], as_index=False)['class'].count()
        shape_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
        max_shape_group = max(shape_one_df_area_group['count'])
        if 'Chart' in shape_class:
            chart_len = len(shape_one_df[shape_one_df['class'] == 'Chart'])
        else:
            chart_len = 0

        if 'GraphicObjectShape' in shape_class:
            graphic_len = len(shape_one_df[shape_one_df['class'] == 'GraphicObjectShape'])
            graphic_one_df = shape_one_df[shape_one_df['class'] == 'GraphicObjectShape']
            graphic_one_df_area_group = graphic_one_df.groupby(['shape_area'], as_index=False)['class'].count()
            graphic_one_df_area_group.rename(columns={'class': 'count'}, inplace=True)
            max_graphic_group = max(graphic_one_df_area_group['count'])


            if max_graphic_group >= 2:
                max_graphic_group_num = len(graphic_one_df_area_group[graphic_one_df_area_group['count'] == max_graphic_group])




            graphic_one_area_df = graphic_one_df['shape_area'].describe()
            max_graphic_area = graphic_one_area_df['max']
            avg_graphic_area = graphic_one_area_df['mean']
        else:
            graphic_len = 0
            max_graphic_group = 0

        shape_one_area_df = shape_one_df['shape_area'].describe()
        max_shape_area = shape_one_area_df['max']
        avg_shape_area = shape_one_area_df['mean']
    else:
        shape_len = 0
        max_shape_group = 0
        chart_len = 0
        graphic_len = 0
        max_graphic_group = 0
        estimate_title_len = 0

    one_ppt['max_text_group'] = max_text_group
    one_ppt['max_shape_group'] = max_shape_group
    one_ppt['max_graphic_group'] = max_graphic_group
    one_ppt['max_font_group'] = max_font_group

    one_ppt['max_text_group_num'] = max_text_group_num
    one_ppt['max_font_group_num'] = max_font_group_num
    one_ppt['max_graphic_group_num'] = max_graphic_group_num

    one_ppt['text_num'] = text_len
    one_ppt['shape_num'] = shape_len
    one_ppt['table_num'] = table_len
    one_ppt['graphic_num'] = graphic_len
    one_ppt['chart_num'] = chart_len
    one_ppt['outline_num'] = outline_len
    one_ppt['title_num'] = title_len
    one_ppt['estimate_title_num'] = estimate_title_len
    one_ppt['font_size_estimate_title_num'] = font_size_estimate_title_len
    one_ppt['new_title_num'] = new_title_len

    one_ppt['max_text_area'] = max_text_area
    one_ppt['avg_text_area'] = avg_text_area
    one_ppt['max_text_content'] = max_text_content
    one_ppt['avg_text_content'] = avg_text_content
    one_ppt['max_shape_area'] = max_shape_area
    one_ppt['avg_shape_area'] = avg_shape_area
    one_ppt['max_graphic_area'] = max_graphic_area
    one_ppt['avg_graphic_area'] = avg_graphic_area
    one_ppt['max_text_area_group'] = max_text_area_group
    one_ppt['max_text_area_group_avg_content_size'] = max_text_area_group_avg_content_size
    one_ppt['max_text_font_group_avg_content_size'] = max_text_font_group_avg_content_size
    one_stat = pd.DataFrame(one_ppt, index=[cur_index])

    return one_stat

def post_deal_with_total_structure_csv(stat_df):
    text_num = stat_df.iloc[0]['text_num']
    max_text_group = stat_df.iloc[0]['max_text_group']
    max_font_group = stat_df.iloc[0]['max_font_group']
    title_num = stat_df.iloc[0]['title_num']
    if title_num == 0:
        if max_text_group == text_num:
            stat_df['max_text_group'] = max_text_group - 1
        if max_font_group == text_num:
            stat_df['max_font_group'] = max_font_group - 1

    return stat_df


