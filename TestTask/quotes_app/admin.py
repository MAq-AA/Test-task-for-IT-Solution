from django.contrib import admin
from .models import Source, Quote, LikeDislike

# Регистрируем каждую модель
@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    pass

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text', 'source', 'weight', 'views_count')
    search_fields = ('text', 'source__name')

@admin.register(LikeDislike)
class LikeDislikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'quote', 'value')
    list_filter = ('value', )