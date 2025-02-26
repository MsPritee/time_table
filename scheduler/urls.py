from django.urls import path
from .views import generate_schedule, bulk_upload, generate_timetable_view

urlpatterns = [
    path('generate/', generate_schedule, name='generate_schedule'),
    path('bulk-upload/', bulk_upload, name='bulk_upload'),
    # path("generate-timetable/", generate_timetable_view, name="generate_timetable"),
    path("generate-timetable/", generate_timetable_view, name="generate_timetable"),

]
