from django.db import models
from django.core.files.base import ContentFile
from datetime import datetime, timedelta
from positional import PositionalSortMixIn
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import signals
import shlex
import subprocess
import os

from photologue.models import Gallery, Photo


from positional import PositionalSortMixIn
 
   
class QueuedItem(PositionalSortMixIn, models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    content_object = generic.GenericForeignKey()
    
    def title(self):
        return self.content_object.title
    
    def admin_thumbnail(self):
        return self.content_object.admin_thumbnail()
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True    
   
class Video(Photo):
    video_file = models.FileField(upload_to='videos', null=True, blank=True)
    poster_frame = models.OneToOneField(Photo, parent_link=True)
    
    def history_item(self):
        ctype = ContentType.objects.get_for_model(self)
        return HistoricalItem.objects.get(content_type__pk = ctype.id, object_id = self.id )
    def orderedphoto(self):
        return self.history_item()
    
last_upload_process = []     
class VideoUpload(models.Model):
    video_file = models.FileField(upload_to='videos_temp')
    title = models.CharField(max_length=256)
    description = models.TextField()
    
    def save(self, *args, **kwargs):
        super(VideoUpload, self).save(*args, **kwargs)
        self.run_converter()
    
    def run_converter(self):
        global last_upload_process
        list = last_upload_process[:]
        for p in list:
            if p.poll:
                p.wait()
                last_upload_process.remove(p)
        base_dir =  os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(base_dir, 'convert_movie.py')
        c = '\'python '+ script + ' ' + str(self.id) + '\''        
        args = shlex.split(c)
        s = subprocess.Popen(args, close_fds=True, shell=True)
        last_upload_process.append(s)  
    
   
class HistoricalItem(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
   
    content_object = generic.GenericForeignKey()
    shown_date = models.DateTimeField()
   
    class Meta:
        ordering = ['shown_date']
        get_latest_by = 'shown_date'
        
class PhotoProxy(Photo):
    
    def history_item(self):
        ctype = ContentType.objects.get_for_model(self)
        return HistoricalItem.objects.get(content_type__pk = ctype.id, object_id = self.id )
    
    def orderedphoto(self):
        return self.history_item()

    class Meta:
        proxy = True        
       
def add_queued_item(sender, instance, **kwargs):
    try: 
        ctype = ContentType.objects.get_for_model(instance)
        QueuedItem.objects.get(content_type__pk = ctype.id, object_id = instance.id)
    except:
        h = QueuedItem(content_object = instance)
        h.save()
       
signals.post_save.connect(add_queued_item, sender=Photo)
signals.post_save.connect(add_queued_item, sender=Video)
   
class Catalog(models.Model):
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add = True)
    #timer = models.DateTimeField(auto_now_add=True)
    increment_setting = models.PositiveIntegerField(default=86400)    
   
    def increment_image(self):
        try:
            item = QueuedItem.objects.get(position=0)
            h = HistoricalItem(content_object = item.content_object, shown_date = datetime.now())
            h.save()
            item.delete()
            return True
        except:
            #No Image in the Queue
            pass

        #if (OrderedPhoto.objects.count() > self.counter+1):
        #    self.counter += 1
        #    self.save()
        #    return True
        return False
        
    def curr_item(self):
        if HistoricalItem.objects.count()==0:
            #No Items Have Ever Been Shown
            if not self.increment_image():
                return None
        #if (OrderedPhoto.objects.count() == 0):
        #    return None
       
        totalSeconds = self.total_seconds()
        if (totalSeconds > self.increment_setting):
            #Increment Image If Possible
            self.increment_image()
            #if (self.increment_image()):
            #    self.timer = self.timer + timedelta(seconds=self.increment_setting)
            #    self.save()
        return HistoricalItem.objects.latest()            
        #ordered_photo = OrderedPhoto.objects.all()[self.counter]
        #if (ordered_photo.shown_date == None):
        #    ordered_photo.shown_date = datetime.now()
        #    ordered_photo.save()                    
       
        return ordered_photo.photo
   
    def total_seconds(self):
        now = datetime.now()
        h = HistoricalItem.objects.latest()
        
        #ordered_photo = OrderedPhoto.objects.all()[self.counter]
        td = now - h.shown_date
        seconds = td.days * 24 * 60 * 60 + td.seconds
        return seconds

class Comment(models.Model):
    photo = models.ForeignKey(Photo)
    text = models.TextField()
    name = models.CharField(max_length=2048)
    created = models.DateTimeField(auto_now_add = True)
   

    class Meta:
        get_latest_by = 'created'
        #unique_together = ("photo", "text", "name")
