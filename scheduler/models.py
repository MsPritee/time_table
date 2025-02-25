# from django.db import models

# Create your models here.


from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=50)
    max_lectures_per_week = models.IntegerField(default=18)

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, unique=True)
    teachers = models.ManyToManyField(Teacher)
    classes = models.ManyToManyField(Class)
    is_practical = models.BooleanField(default=False)  # True if it's a lab session

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"

class Room(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_lab = models.BooleanField(default=False)  # True if it's a lab

    def __str__(self):
        return self.name
