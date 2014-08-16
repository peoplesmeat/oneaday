import os
import sys
import shlex
import subprocess
from django.core.management import setup_environ
from django.core.files import File
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..'))

from djangoapps import settings 
setup_environ(settings)

from oneaday.models import *

os.nice(15)

id = sys.argv[1]

v = VideoUpload.objects.get(pk=id)

class Converter():
    def __init__(self, video):
        self.video = video
        
        
        
    def do_convert(self):
        input_file = self.video.video_file.path
        output_file = ext = os.path.splitext(self.video.video_file.path)[0] + '.flv'
        
        c = '\'/usr/local/bin/ffmpeg -i '+ str(input_file)
        c+=' -y  -acodec libfaac -ab 128k -ac 2 -ar 22050 -vcodec libx264 -vpre default -crf 22 -threads 0 '
        c+= output_file + '\''
        print c
        #r = os.system(c)
        args = shlex.split(c)
        
        subprocess.call(args, shell=True)
        return open(output_file) 
    
    def do_poster_frame(self):
        input_file = self.video.video_file.path
        poster_frame = os.path.splitext(self.video.video_file.path)[0] + '.jpg'
        
        c = 'ffmpeg -i '+str(input_file)+' -ss 00:00:01 -vcodec mjpeg -vframes 1 -f image2 '
        c +=  str(poster_frame)
        args = shlex.split(c)
        subprocess.call(args)
        return open(poster_frame)

c = Converter(v)
video = c.do_convert()
poster_frame = c.do_poster_frame()

new_video = Video(title=v.title, caption=v.description, 
                  title_slug = slugify(v.title),
                  video_file=File(video))
new_video.image.save('test.jpg', ContentFile(poster_frame.read()))
new_video.save()
print 'DONE!'