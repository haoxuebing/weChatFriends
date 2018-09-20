import pandas as pd
import itchat
from pyecharts import Pie, Map, Style, Page, Bar
import jieba
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy
import PIL.Image as Image
import os


def get_attr(friends, key):
    return list(map(lambda user: user.get(key), friends))


def get_friends():
    itchat.auto_login(hotReload=True)
    friends = itchat.get_friends()
    users = dict(province=get_attr(friends, "Province"),
                 city=get_attr(friends, "City"),
                 nickname=get_attr(friends, "NickName"),
                 sex=get_attr(friends, "Sex"),
                 signature=get_attr(friends, "Signature"),
                 remarkname=get_attr(friends, "RemarkName"),
                 pyquanpin=get_attr(friends, "PYQuanPin"),
                 displayname=get_attr(friends, "DisplayName"),
                 isowner=get_attr(friends, "IsOwner"))
    return users


def sex_stats(users):
    df = pd.DataFrame(users)
    sex_arr = df.groupby(['sex'], as_index=True)['sex'].count()
    data = dict(zip(list(sex_arr.index), list(sex_arr)))
    # data['不告诉你'] = data.pop(0)
    data['帅哥'] = data.pop(1)
    data['美女'] = data.pop(2)
    return data.keys(), data.values()


def prov_stats(users):
    prv = pd.DataFrame(users)
    prv_cnt = prv.groupby('province', as_index=True)[
        'province'].count().sort_values()
    attr = list(map(lambda x: x if x != '' else '未知', list(prv_cnt.index)))
    return attr, list(prv_cnt)


def gd_stats(users):
    df = pd.DataFrame(users)
    data = df.query('province == "北京"')
    res = data.groupby('city', as_index=True)['city'].count().sort_values()
    attr = list(map(lambda x: '%s区' % x if x != '' else '未知', list(res.index)))
    return attr, list(res)


def create_charts():
    users = get_friends()
    page = Page()
    style = Style(width=1300, height=800)
    style_middle = Style(width=900, height=500)
    data = sex_stats(users)
    attr, value = data
    chart = Pie('微信性别')  # title_pos='center'
    chart.add('', attr, value, center=[50, 50],
              radius=[30, 70], is_label_show=True, legend_orient='horizontal', legend_pos='center',
              legend_top='bottom', is_area_show=True)
    page.add(chart)

    data = prov_stats(users)
    attr, value = data
    chart = Map('全国分布', **style.init_style)
    chart.add('', attr, value, is_label_show=True,
              is_visualmap=True, visual_text_color='#000')
    page.add(chart)

    chart = Bar('全国柱状图', **style_middle.init_style)
    chart.add('', attr, value, is_stack=True, label_pos='inside', is_legend_show=True,
              is_label_show=True, xaxis_interval=0, xaxis_rotate=30)
    page.add(chart)

    data = gd_stats(users)
    attr, value = data
    chart = Map('北京分布', **style.init_style)
    chart.add('', attr, value, maptype='北京', is_label_show=True,
              is_visualmap=True, visual_text_color='#000')
    page.add(chart)

    chart = Bar('北京柱状图', **style_middle.init_style)
    chart.add('', attr, value, is_stack=True,
              label_pos='inside', is_label_show=True)
    page.add(chart)
    page.render()


def jieba_cut(users):
    signature = users['signature']
    words = ''.join(signature)
    res_list = jieba.cut(words, cut_all=True)
    return res_list


def create_wc(words_list):
    # res_path = os.path.abspath('./resource')
    words = ' '.join(words_list)
    # back_pic = numpy.array(Image.open("%s/china1.png" % res_path))
    stopwords = set(STOPWORDS)
    stopwords = stopwords.union(set(
        ['class', 'span', 'emoji', 'emoji', 'emoji1f388', 'emoji1f604', 'emoji1f436', 'emoji1f4aa']))
    wc = WordCloud(background_color="white", margin=0,
                   font_path='./resource/qihei55.ttf',
                   width=1300,
                   height=900,
                   #    mask=back_pic,
                   max_font_size=150,
                   stopwords=stopwords
                   ).generate(words).to_file('./resource/weixin.png')
    # image_colors = ImageColorGenerator(back_pic)
    plt.imshow(wc)
    # plt.imshow(wc.recolor(color_func=image_colors))
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    create_charts()
    users = get_friends()
    word_list = jieba_cut(users)
    create_wc(word_list)
