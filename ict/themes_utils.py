#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @Author : jliangqiu
# @Time : 2020/6/18
# @File : themes_utils.py
import time

import cv2
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from ict.MMCQ import MMCQ
from ict.KMeans import KMeans


def choice_themes_method(max_color, option="MMCQ"):
    if option == "MMCQ":
        t_method = lambda d: MMCQ(d, max_color).quantize()
    elif option == "KMeans":
        t_method = lambda d: KMeans(d, max_color).quantize()
    else:
        t_method = None
    return t_method


def cv_imread(filePath, flags=-1):
    import numpy as np
    try:
        cv_img = cv2.imdecode(np.fromfile(filePath, dtype=np.uint8), flags)
        ## imdecode读取的是rgb，如果后续需要opencv处理的话，需要转换成bgr，转换后图片颜色会变化
        ##cv_img=cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
    except Exception as e:
        return None
    return cv_img


def image_bgra_to_bgr(img_path, img_bgr=None):
    img_bgr = cv_imread(img_path, -1) if img_bgr is None else img_bgr
    if img_bgr is None:
        print(img_path)
        return None
    try:
        if len(img_bgr.shape)<=2:
            b = img_bgr
            g = img_bgr
            r = img_bgr
        else:
            if img_bgr.shape[2] > 3:
                b, g, r, a = cv2.split(img_bgr)
                a_v = 255 - a
                # a_v = 0
                a = a / 255
                b = b * a + a_v
                g = g * a + a_v
                r = r * a + a_v
            else:
                b, g, r = cv2.split(img_bgr)
    except:
        print('hello')
    img_pro = cv2.merge([b, g, r]).astype(np.uint8)
    return img_pro


def img_palette(imgs, themes, titles, imgs_hsv):
    N = len(imgs)
    fig = plt.figure()
    gs = gridspec.GridSpec(len(imgs), len(themes) + 2)
    print(N)
    for i in range(N):
        im = fig.add_subplot(gs[i, 0])
        im.imshow(imgs[i])
        im.set_title("Image %s" % str(i + 1))
        im.xaxis.set_ticks([])
        im.yaxis.set_ticks([])
        im_hsv = fig.add_subplot(gs[i, 1])
        im_hsv.imshow(imgs_hsv[i])
        im_hsv.set_title("Imagehsv %s" % str(i + 1))
        im_hsv.xaxis.set_ticks([])
        im_hsv.yaxis.set_ticks([])
        t = 2
        for themeLst in themes:
            theme = themeLst[i]
            pale = np.zeros(imgs[i].shape, dtype=np.uint8)
            h, w, _ = pale.shape
            ph = h / len(theme)
            for y in range(h):
                pale[y, :, :] = np.array(theme[int(y / ph)], dtype=np.uint8)

            pl = fig.add_subplot(gs[i, t])
            pl.imshow(pale)
            pl.set_title(titles[t - 2])
            pl.xaxis.set_ticks([])
            pl.yaxis.set_ticks([])

            t += 1

    plt.show()


def rgb2hsv(rgb_value):
    r, g, b = rgb_value[:]
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    m = mx - mn
    h = 0
    if mx == mn:
        h = 0
    elif mx == r:
        if g >= b:
            h = ((g - b) / m) * 60
        else:
            h = ((g - b) / m) * 60 + 360
    elif mx == g:
        h = ((b - r) / m) * 60 + 120
    elif mx == b:
        h = ((r - g) / m) * 60 + 240
    if mx == 0:
        s = 0
    else:
        s = m / mx
    v = mx
    H = h / 2
    S = s * 255.0
    V = v * 255.0
    return H, S, V


def get_image_themes_color(f_call, img_path, resize=256, is_hsv=True, is_show=False):
    if not callable(f_call):
        f_call = choice_themes_method(10)
    img_bgr = image_bgra_to_bgr(img_path)
    if img_bgr is None:
        print('error')
        print(img_path)
        return [], None, None
    img_h, img_w = img_bgr.shape[:2]
    hw = [img_h, img_w]
    # print(img_bgr.shape)
    max_s = max(img_h, img_w)
    f = resize / (max_s + 1e-5)
    img_bgr = cv2.resize(img_bgr, None, fx=f, fy=f)
    # print(img_bgr.shape)
    pix_data = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    themes, nratio = f_call(pix_data)
    hsv_theme = []
    if is_show:
        pix_hsvs = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        for t in themes:
            h, s, v = rgb2hsv(t)
            hsv_theme.append([int(h), int(s), int(v)])
        img_palette([pix_data], [[themes], [hsv_theme]], ["MMCQ", "HSV"], [pix_hsvs])
    if is_hsv:
        for t in themes:
            h, s, v = rgb2hsv(t)
            hsv_theme.append([int(h), int(s), int(v)])
        return hsv_theme, nratio, hw
    else:
        return themes, nratio, hw


def get_images_themes_color(f_call, img_paths, resize=256, is_hsv=True, is_show=False):
    if not callable(f_call):
        f_call = choice_themes_method(7)
    pix_rgbs, pix_hsvs, hw_list = [], [], []
    start = time.process_time()
    for img_path in img_paths:
        img_bgr = image_bgra_to_bgr(img_path)
        if img_bgr is None:
            print(img_path)
            continue
        print("db image path", img_path)
        # print(img_bgr.shape)
        img_h, img_w = img_bgr.shape[:2]
        hw_list.append([img_h, img_w])
        if resize is not None:
            max_s = max(img_h, img_w)
            f = resize / (max_s + 1e-5)
            img_bgr = cv2.resize(img_bgr, None, fx=f, fy=f)
            # print(img_bgr.shape)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pix_rgbs.append(img_rgb)
        pix_hsvs.append(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV))

    themes = list(map(f_call, pix_rgbs))
    print("MMCQ Time cost: {0}".format(time.process_time() - start))
    hsv_list, hsv_str, rgb_str = [], [], []
    for idt, theme in enumerate(themes):
        t_hsv, t_hstr, t_rstr, = [], [], []
        for t in theme[0]:
            h, s, v = rgb2hsv(t)
            t_hstr.append("%d,%d,%d" % (h, s, v))
            t_rstr.append(",".join(map(lambda x: str(x), t)))
            t_hsv.append([int(h), int(s), int(v)])
        r_str = map(lambda x: str(x), theme[1])
        t_str = ",".join(r_str)
        wh_str = "%s,%s" % (hw_list[idt][0], hw_list[idt][1])
        hsv_str.append(";".join([":".join(t_hstr), t_str, wh_str]))
        rgb_str.append(";".join([":".join(t_rstr), t_str, wh_str]))
        hsv_list.append([t_hsv, theme[1]])
    if is_show:
        them_ = [i[0] for i in themes]
        hsv_l = [i[0] for i in hsv_list]
        img_palette(pix_rgbs, [them_, hsv_l], ["MMCQ", "HSV"], pix_hsvs)
    if is_hsv:
        return hsv_list, hsv_str
    else:
        return themes, rgb_str


def resize_image(img_bgr, resize=256):
    if resize is not None:
        img_h, img_w = img_bgr.shape[:2]
        max_s = max(img_h, img_w)
        f = resize / (max_s + 1e-5)
        img_bgr = cv2.resize(img_bgr, (resize, resize))
    return img_bgr