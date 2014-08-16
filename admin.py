from oneaday.models import *
from django.contrib import admin

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'created')
    list_per_page = 10
    
class CatalogAdmin(admin.ModelAdmin):
    list_display = ('name', 'increment_setting', 'total_seconds')
    list_per_page = 10

class HistoricalAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'shown_date')
    list_per_page = 50

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title','date_added', 'admin_thumbnail', 'video_file')

class VideoUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_file')
    
class QueuedItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'admin_thumbnail')

admin.site.register(Catalog, CatalogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(VideoUpload, VideoUploadAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(QueuedItem, QueuedItemAdmin)
admin.site.register(HistoricalItem, HistoricalAdmin)

