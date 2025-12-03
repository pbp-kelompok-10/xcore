from django.contrib import admin
from .models import Highlight

@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('match', 'video_preview')
    search_fields = ('match__home_team__name', 'match__away_team__name')
    list_select_related = ('match',)
    readonly_fields = ('video_embed',)

    fieldsets = (
        (None, {
            'fields': ('match', 'video', 'video_embed'),
        }),
    )

    def video_preview(self, obj):
        return obj.video if obj.video else '-'
    video_preview.short_description = "Video URL"

    def video_embed(self, obj):
        if obj.video:
            from django.utils.safestring import mark_safe
            return mark_safe(f'<iframe width="320" height="180" src="{obj.video.url}" frameborder="0" allowfullscreen></iframe>')
        return "No video available"
    video_embed.short_description = "Video Preview"
