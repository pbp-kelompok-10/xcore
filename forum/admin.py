from django.contrib import admin
from .models import Forum, Post

# Admin untuk Forum
class ForumAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'match')  
    list_filter = ('match',) 
    search_fields = ('nama',)  
    readonly_fields = ('id',)  

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('match')  

# Admin untuk Post
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'forum', 'author', 'message', 'created_at', 'is_edited') 
    list_filter = ('forum', 'author', 'is_edited', 'created_at') 
    search_fields = ('message', 'author__username') 
    readonly_fields = ('id', 'created_at')  
    date_hierarchy = 'created_at' 

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('forum', 'author')  

# Daftarkan model ke admin
admin.site.register(Forum, ForumAdmin)
admin.site.register(Post, PostAdmin)