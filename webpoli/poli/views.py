import json
from collections import Counter

import jieba
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Q
from django.shortcuts import render

# Create your views here.
from poli.models import Poli


# 详情页面
def details(request, id):
    f = open('Data.json', 'r', encoding="utf-8")
    Data = json.load(f)

    poli = Poli.objects.filter(id=id).first()
    # 添加阅读量
    if not request.session.get('reading' + str(id), ''):
        reading = Poli.objects.filter(id=id)
        reading.update(reading=F('reading') + 1)
        request.session['reading' + str(id)] = True
    return render(request, 'details.html', locals())

# 政务信息页面
def poli(request, page):
    f = open('Data.json', 'r', encoding="utf-8")
    Data = json.load(f)

    polis = Poli.objects.all().order_by('-Time')[(page-1)*10:page*10]
    per_page = 10
    polis_num = Poli.objects.all().count()
    pages_num = int(polis_num/per_page) if polis_num%per_page==0 else int(polis_num/per_page)+1
    pages = list(range(1, pages_num+1))

    return render(request, 'poli.html', locals())

# 搜索特定城市城市
def city_poli(request, City, page):
    f = open('Data.json', 'r', encoding="utf-8")
    Data = json.load(f)

    polis = Poli.objects.filter(City=City).order_by('-Time')[(page - 1) * 10:page * 10]
    per_page = 10
    polis_num = Poli.objects.filter(City=City).count()
    pages_num = int(polis_num / per_page) if polis_num % per_page == 0 else int(polis_num / per_page) + 1
    pages = list(range(1, pages_num + 1))

    # polis = Poli.objects.filter(City=City).order_by('-Time')
    # paginator = Paginator(polis, 10)
    # try:
    #     pageInfo = paginator.page(page)
    # except PageNotAnInteger:
    #     # 如果参数page 的数据类型不是整型，就返回第一页数据
    #     pageInfo = paginator.page(1)
    # except EmptyPage:
    #     # 若用户访问的页数大于实际页数，则返回最后一页的数据
    #     pageInfo = paginator.page(paginator.num_pages)
    return render(request, 'poli.html', locals())

# 搜索特定类别
def class_poli(request, _Class, page):
    f = open('Data.json', 'r', encoding="utf-8")
    Data = json.load(f)

    polis = Poli.objects.filter(Class=_Class).order_by('-Time')[(page - 1) * 10:page * 10]
    per_page = 10
    polis_num = Poli.objects.filter(Class=_Class).count()
    pages_num = int(polis_num / per_page) if polis_num % per_page == 0 else int(polis_num / per_page) + 1
    pages = list(range(1, pages_num + 1))

    # polis = Poli.objects.filter(Class=_Class).order_by('-Time')
    # paginator = Paginator(polis, 10)
    # try:
    #     pageInfo = paginator.page(page)
    # except PageNotAnInteger:
    #     # 如果参数page 的数据类型不是整型，就返回第一页数据
    #     pageInfo = paginator.page(1)
    # except EmptyPage:
    #     # 若用户访问的页数大于实际页数，则返回最后一页的数据
    #     pageInfo = paginator.page(paginator.num_pages)
    return render(request, 'poli.html', locals())

# 搜索关键词
def key_poli(request, key, page):
    f = open('Data.json', 'r', encoding="utf-8")
    Data = json.load(f)

    polis = Poli.objects.filter(Q(Content__contains=key)|Q(RepCon__contains=key)).order_by('-Time')[(page - 1) * 10:page * 10]
    per_page = 10
    polis_num = Poli.objects.filter(Q(Content__contains=key)|Q(RepCon__contains=key)).count()
    pages_num = int(polis_num / per_page) if polis_num % per_page == 0 else int(polis_num / per_page) + 1
    pages = list(range(1, pages_num + 1))

    # polis = Poli.objects.filter(Q(Content__contains=key)|Q(RepCon__contains=key)).order_by('-Time')
    # paginator = Paginator(polis, 10)
    # try:
    #     pageInfo = paginator.page(page)
    # except PageNotAnInteger:
    #     # 如果参数page 的数据类型不是整型，就返回第一页数据
    #     pageInfo = paginator.page(1)
    # except EmptyPage:
    #     # 若用户访问的页数大于实际页数，则返回最后一页的数据
    #     pageInfo = paginator.page(paginator.num_pages)
    return render(request, 'poli.html', locals())