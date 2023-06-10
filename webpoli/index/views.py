import json
import os
import re
import time
from collections import Counter

import jieba
import numpy as np
import pandas as pd
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from wordcloud import WordCloud  # 词云，颜色生成器，停止词

# Create your views here.
from index.form import DownloadForm
from index.models import Board
from poli.models import Poli

# 数据初始化，为了提高访问速度，提前进行计算并存储结果
def data_init():
    print('数据初始化中')
    # 城市导航栏
    City = [i['City'] for i in Poli.objects.values('City').distinct()]
    Class = [i['Class'] for i in Poli.objects.values('Class').distinct()]
    city_num = {i: Poli.objects.filter(City=i).count() for i in City}
    class_num = {i: Poli.objects.filter(Class=i).count() for i in Class}
    city_num_sort = sorted(list(city_num.items()), key=lambda i: -i[1])
    class_num_sort = sorted(list(class_num.items()), key=lambda i: -i[1])
    # 分词、词频
    count = Poli.objects.count()
    if count < 200:
        raw_data = [i['Content'] for i in Poli.objects.values('Content')] + \
                   [i['RepCon'] for i in Poli.objects.values('RepCon')]
    else:
        raw_data = [i['Content'] for i in Poli.objects.order_by('?')[:200].values('Content')] + \
                   [i['RepCon'] for i in Poli.objects.order_by('?')[:200].values('RepCon')]

    raw_data = ''.join(raw_data)
    # 过滤无用词
    for x in 'xXD_感谢你您我们好的现已零一二三四五六七八九十':
        raw_data = raw_data.replace(x, "")
    for x in ['问题', '反映', '目前', '已经', '可以', '收到', '根据', '内容', '回复', '来信', '关于', '尊敬', '网友', '如下', '相关', '情况', '进行', '使用', '工作', '领导', '联系'
        , '电话', '先生', '收悉', '没有', '按照', '经查', '经了解', '据了解', '答复', '祝生活愉快', '承办单位', '将意见']:
        raw_data = raw_data.replace(x, "")

    data = raw_data
    # 过滤标点
    for x in ' ，。“‘’”：！、《》；？　」「…":.,/\\; X0D_':
        data = data.replace(x, "")
        data = data.replace("\n", "")
    words = [i for i in jieba.lcut(data) if len(i) > 1]
    data = ''.join(words)
    ct = Counter(words).most_common(8)

    # 绘图sub1
    Time = sorted([int(i['Time'].strftime('%Y%m')) for i in Poli.objects.values('Time')])
    c = sorted({int(i): Time.count(i) for i in set(Time)}.items())
    x1 = [i[0] for i in c]
    y1 = [c[0][1]]
    for i in c[1:]:
        y1.append(y1[-1] + i[1])
    # y1 = [i[1] for i in c]

    # 绘图sub2
    c = sorted(city_num.items(), key=lambda x: x[1], reverse=True)[0:10]
    x2 = [i[0] for i in c]
    y2 = [i[1] for i in c]

    # 绘图sub3
    # 配置词云的背景，图片，字体大小等参数
    wc = WordCloud(
        background_color=(256, 256, 256, 0),  # 设置显示内容在什么颜色内
        width=600,  # 设置图片宽,默认为400
        height=400,  # 设置图片高,默认为200
        # mask=img_array,  # 设置词云背景模板
        font_path='STKAITI.TTF',  # 设置字体路径
        # stopwords=stopwords,  # 设置需要屏蔽的词，如果为空，则使用内置的STOPWORDS
        scale=1.0,  # 图照比例进行放大画布，如设置为1.5，则长和宽都是原来画布的1.5倍
        max_words=1000,  # max_words图片上显示的最大词语的个数
        max_font_size=65,  # max_font_size为最大字体的大小
        min_font_size=4,  # min_font_size为最小字体大小,默认为4
        mode='RGBA',  # ,默认值RGB,当参数为“RGBA”并且background_color不为空时，背景为透明
        relative_scaling=1,  # 词频和字体大小的关联性,默认值
        collocations=True  # 是否包括两个词的搭配
    )
    wc.generate_from_text(raw_data)  # 根据文本生成词云
    # image = wc.to_image()
    # image.show()
    wc.to_file('media/images/wordcloud.png')  # 保存图片

    Data = {'Class': Class, 'city_num': city_num, 'city_num_sort':city_num_sort,'class_num_sort':class_num_sort ,'class_num': class_num, 'ct': ct, 'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2}
    f = open('Data.json', 'w+', encoding='utf-8')
    json.dump(Data, f)
    f.flush()

    print('数据初始化完成')

# 主页
def index(request):
    # 添加访问量
    if not request.session.get('use', ''):
        site = Site.objects.all()
        site.update(use=F('use') + 1)
        request.session['use'] = True
    # 加载数据
    f = open('Data.json', 'r', encoding="utf-8")
    Data = json.load(f)

    return render(request, 'index.html', locals())

# 管理页面
def manage(request):
    site = Site.objects.first()
    tm = timezone.now() - site.create # 网站运行时间
    ct = Poli.objects.all().count()  # 意见条数

    df = DownloadForm() # 城市选择表单
    if request.method == 'POST':
        # 选择城市导出表单
        if 'City' in request.POST.keys():
            City = df.choices[int(request.POST['City'])][1]
            dh = [i.name for i in Poli._meta.get_fields()]
            if City == '全部':
                dt = Poli.objects.values_list()
            else:
                dt = Poli.objects.filter(City=City).values_list()
            excel = pd.DataFrame({i: j for i, j in zip(dh, zip(*dt))})
            excel['Time'] = excel['Time'].dt.tz_localize(None)
            excel['RepTime'] = excel['RepTime'].dt.tz_localize(None)
            excel.to_excel('data.xlsx')
            # 返回excel文件
            try:
                response = StreamingHttpResponse(open('data.xlsx', 'rb'))
                response['content_type'] = "application/octet-stream"
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename('data.xlsx')
                return response
            except Exception:
                # raise Http404
                pass
        # 通过excel文件导入信息
        elif 'f' in request.FILES.keys():
            file = request.FILES.get('f')
            success, fail = 0, 0
            try:
                print('文件接收成功，开始导入')
                f = pd.read_excel(file)
                obj = []
                for value in f.values:
                    poli = {}
                    for i, j in zip(f.columns, value):
                        poli[i] = j
                    if list(poli.values()).count(np.nan)==0 :
                        if re.search(r'^\d{4}-\d+-\d+', poli['Time']) and re.search(r'^\d{4}-\d+-\d+', poli['RepTime']) :
                            obj.append(Poli(**poli))
                            success = success + 1
                        else:
                            fail = fail + 1
                        # Poli.objects.create(**poli)
                    else:
                        fail = fail + 1
                Poli.objects.bulk_create(obj)

                messages.info(request, '数据导入成功！'+'导入'+str(success)+'条记录。'+str(fail)+'条记录导入失败')
                data_init() # 导入完成后需要重新进行数据初始化
            except ValueError:
                messages.info(request, '文件出错')
    return render(request, 'manage.html', locals())

# 意见反馈页面
def board(request, page):
    f = open('Data.json', 'r', encoding="utf-8")
    Data = json.load(f)

    # 管理员展示留言内容
    if request.user.is_superuser:
        boardList = Board.objects.all().order_by('-created')
        paginator = Paginator(boardList, 10)
        try:
            pageInfo = paginator.page(page)
        except PageNotAnInteger:
            # 如果参数page 的数据类型不是整型，就返回第一页数据
            pageInfo = paginator.page(1)
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页的数据
            pageInfo = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')
        value = {'name': name, 'email': email,
                 'content': content}
        Board.objects.create(**value)
        kwargs = {'page': 1}
        return redirect(reverse('board', kwargs=kwargs))
    return render(request, 'board.html', locals())

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

def page_error(request):
    return render(request, '500.html', status=500)


# 初始搭建时初始化数据库内网站信息
from index.models import Site
def site_init():
    try:
        if Site.objects.all().count() == 0:
            Site.objects.create()
    except Exception:
        pass
site_init()
# data_init()