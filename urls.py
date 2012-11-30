# -*- coding: utf-8 -*-

from django.conf.urls import patterns,url
urlpatterns=patterns('jfupload.views',
    url(r'^$','index'),
    #url(r'^upload/$','upload',name="upload"),
    url(r'^upload/$','upload'),
    #url(r'^check_existing/$','check_existing',name="check_existing"),
)

