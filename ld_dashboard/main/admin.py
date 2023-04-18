from django.contrib import admin

from .models import Project, TestList, TestCase, TestCase_Detail, WeeklyTable
from simple_history import register

# Register your models here.
admin.site.register(Project)
admin.site.register(TestList)
admin.site.register(TestCase)
admin.site.register(TestCase_Detail)
admin.site.register(WeeklyTable)


