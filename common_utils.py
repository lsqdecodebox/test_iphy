import numpy as np
from PIL import Image, ImageDraw,ImageFont
import cv2
def standardization(data):
    mu = np.mean(data, axis=0)
    sigma = np.std(data, axis=0)
    return (data - mu) / sigma

def paint_chinese_opencv(im, chinese, pos, color):
    img_PIL = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype('resource/simsun/simsun.ttc', 100)
    fillColor = color # 颜色
    position = pos # 位置
    if not isinstance(chinese, str):
        chinese = chinese.decode('utf-8')
    draw = ImageDraw.Draw(img_PIL)
    draw.text(position, chinese, font=font, fill=fillColor)
    img = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
    return img

def deal_no_word(x):
    if x == '':
        return float(0)
    else:
        return float(x)


def deal_no_word(x):
    '''
    处理无文字
    :param x:
    :return:
    '''
    if x == '':
        return float(0)
    else:
        return float(x)
