from django.db import models

# Create your models here.
from django.utils import timezone


class Site(models.Model):
    name = models.CharField('名字', max_length=100, default='阳光政务')
    create = models.DateTimeField('创建时间', default=timezone.now)
    use = models.IntegerField('使用次数', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '网站运营数据'
        verbose_name = '网站运营数据'


class Board(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('留言用户', max_length=50)
    email = models.CharField('邮箱地址', max_length=50)
    content = models.CharField('留言内容', max_length=500)
    created = models.DateTimeField('创建时间', default=timezone.now)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = '留言'
        verbose_name = '留言'

