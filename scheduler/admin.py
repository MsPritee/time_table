# Register your models here.

from django.contrib import admin
from .models import Teacher, Class, Subject, TimeSlot, Room

admin.site.register(Teacher)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(TimeSlot)
admin.site.register(Room)
