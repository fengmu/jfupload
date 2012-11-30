#coding:utf-8
from django.template.loader import get_template
from django.template import Context
#from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import os
import logging
import sqlalchemy
import Image
from string import Template
from yuquan.dataInterface import fmsql
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.contrib import auth
#importing json parser to generate jQuery plugin friendly json response
from django.utils import simplejson

def log(request):
    logging.basicConfig(filename='uploadify.log',level=logging.INFO)
    logging.info(request)

def index(request):
    t=get_template("jfupload/jfupload.html")
    html=t.render(Context())
    return HttpResponse(html)

#@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.user.is_authenticated() and request.user.has_perm("auth.can_manage_data"):
        file = request.FILES[u'files[]']
        wrapped_file = UploadedFile(file)
        filename = wrapped_file.name
        file_size = wrapped_file.file.size
        #log(filename)
        #log(file_size)
        errormsg=""

        if len(filename)<>12 and filename[0:-4].isdigit()==False:
            errormsg="上传失败！图片名称必须为8位商品代码。"
        else:

            #保存图片
            file_upload = open(os.path.join(settings.IMG_TEMP_FOLDER,filename), 'w+b')
            file_upload.write(request.FILES[u'files[]'].read())
            file_upload.close()
    
            #缩小图片
            sqlstr = Template("select spcode, height, width from kdsp where spcode in ('${spcodestr}')")
            mysql = fmsql.Fmsql()
            docname = filename.split(".")[0]
            doctype = filename.split(".")[1]
            sqldata = mysql.getresults(sqlstr.substitute(spcodestr = str(docname)))
            if len(sqldata)>0:
                height = sqldata[0][1]
                width = sqldata[0][2]
                picheight = int(height * 0.5)
                picwidth = int(width * 0.5)
                imgdir=os.path.join(settings.IMG_TEMP_FOLDER,filename)
                #log(imgdir)
                fmimg=Image.open(imgdir)
                fmimg=fmimg.resize((picwidth,picheight))
                imgdir2=os.path.join(settings.IMG_THUMB_FOLDER,filename)
                #log(imgdir2)
                fmimg.save(imgdir2,"JPEG")
                
                rotatePicfilename = docname + "r." + doctype            
                imgdir3=os.path.join(settings.IMG_THUMB_FOLDER,rotatePicfilename)
                fmimg.save(imgdir2,"JPEG")
                rotatePic(imgdir2, imgdir3)
                
            else:
                 height = 0
                 width = 0
                 errormsg="上传失败！图片无尺寸信息！"
    
           
    
            #转存到store
            img = request.FILES[u'files[]']        
            destination = open(os.path.join(settings.IMG_STORE_FOLDER,filename), 'wb+')
            for chunk in img.chunks():
                destination.write(chunk)
            destination.close()
    
            #清空temp
            os.remove(os.path.join(settings.IMG_TEMP_FOLDER,filename))

        #generating json response array
        result = []
        result.append({"name":filename, 
                       "size":file_size,
                       "error":errormsg,
                       #"url":file_url, 
                       #"thumbnail_url":thumb_url,
                       #"delete_url":file_delete_url+str(image.pk)+'/', 
                       #"delete_type":"POST",
                       })
        response_data = simplejson.dumps(result)
        #checking for json data type
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, mimetype=mimetype)
    else:
        return HttpResponse('Only POST accepted')

#旋转图片
def rotatePic(picpath, picpath2,angle=90):   
    try:
        im = Image.open(picpath)
        im = im.rotate(angle)
        im.save(picpath2,"JPEG")
    except:
        pass

