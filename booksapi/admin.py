from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name','id','created_by')
    prepopulated_fields = {'slug':('name',),}
