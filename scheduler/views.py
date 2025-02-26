# from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from .optimizer import generate_timetable
import csv
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Teacher, Subject, Class, Room, TimeSlot
from .forms import CSVUploadForm
from django.db import IntegrityError
from .scheduling import generate_timetable  # Import the function



def generate_schedule(request):
    """API to trigger the timetable generation"""
    timetable = generate_timetable()
    return JsonResponse({"timetable": timetable})


def bulk_upload(request):
    """Handle bulk upload of data via CSV with duplicate handling"""
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["file"]

            # Ensure it's a CSV file
            if not csv_file.name.endswith(".csv"):
                messages.error(request, "Only CSV files are allowed.")
                return redirect("bulk_upload")

            try:
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file)

                header = next(reader)  # Read the first row as header
                
                for row in reader:
                    if len(row) < 2:
                        continue  # Skip incomplete rows

                    model_name = row[0].strip().lower()
                    data = [col.strip() for col in row[1:]]

                    if model_name == "teacher":
                        try:
                            teacher, created = Teacher.objects.get_or_create(
                                email=data[1],  # Check by email
                                defaults={"name": data[0], "department": data[2], "max_lectures_per_week": int(data[3])}
                            )
                            if not created:
                                messages.warning(request, f"Skipped duplicate teacher: {data[0]}")
                        except IntegrityError:
                            messages.error(request, f"Duplicate email found: {data[1]}")

                    elif model_name == "class":
                        Class.objects.get_or_create(name=data[0])

                    elif model_name == "subject":
                        subject, created = Subject.objects.get_or_create(name=data[0], subject_code=data[1])
                        
                        teachers = Teacher.objects.filter(name__in=data[2].split(";"))
                        subject.teachers.set(teachers)

                        classes = Class.objects.filter(name__in=data[3].split(";"))
                        subject.classes.set(classes)

                        subject.is_practical = data[4].lower() == "true"
                        subject.save()

                    elif model_name == "room":
                        Room.objects.get_or_create(name=data[0], defaults={"is_lab": data[1].lower() == "true"})

                    elif model_name == "timeslot":
                        TimeSlot.objects.get_or_create(start_time=data[0], end_time=data[1])

                messages.success(request, "Bulk data uploaded successfully with duplicate handling!")
                return redirect("bulk_upload")

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
                return redirect("bulk_upload")

    else:
        form = CSVUploadForm()

    return render(request, "bulk_upload.html", {"form": form})


def generate_timetable_view(request):
    """View to regenerate and display the timetable"""
    if request.method == "POST":  # When the button is clicked
        timetable = generate_timetable()  # Call the scheduler again to regenerate
    else:
        timetable = generate_timetable()  # First-time load

    return render(request, "scheduler/timetable.html", {"timetable": timetable})

# def generate_timetable_view(request):
#     """View to generate and display the timetable"""
#     result = generate_timetable()  # Call OR-Tools function

#     if isinstance(result, str):  # If no solution was found
#         return render(request, "generate_timetable.html", {"error": result})
    
#     return render(request, "generate_timetable.html", {"timetable": result})



# def bulk_upload(request):
#     """Handle bulk upload of data via CSV"""
#     if request.method == "POST":
#         form = CSVUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = request.FILES["file"]
            
#             # Ensure it's a CSV file
#             if not csv_file.name.endswith(".csv"):
#                 messages.error(request, "Only CSV files are allowed.")
#                 return redirect("bulk_upload")
            
#             try:
#                 decoded_file = csv_file.read().decode("utf-8").splitlines()
#                 reader = csv.reader(decoded_file)

#                 header = next(reader)  # Read the first row as header
                
#                 for row in reader:
#                     if len(row) < 2:
#                         continue  # Skip incomplete rows

#                     model_name = row[0].strip().lower()
#                     data = [col.strip() for col in row[1:]]

#                     if model_name == "teacher":
#                         Teacher.objects.create(name=data[0], email=data[1], department=data[2], max_lectures_per_week=int(data[3]))

#                     elif model_name == "class":
#                         Class.objects.create(name=data[0])

#                     elif model_name == "subject":
#                         subject, created = Subject.objects.get_or_create(name=data[0], subject_code=data[1])
                        
#                         teachers = Teacher.objects.filter(name__in=data[2].split(";"))
#                         subject.teachers.set(teachers)

#                         classes = Class.objects.filter(name__in=data[3].split(";"))
#                         subject.classes.set(classes)

#                         subject.is_practical = data[4].lower() == "true"
#                         subject.save()

#                     elif model_name == "room":
#                         Room.objects.create(name=data[0], is_lab=data[1].lower() == "true")

#                     elif model_name == "timeslot":
#                         TimeSlot.objects.create(start_time=data[0], end_time=data[1])

#                 messages.success(request, "Bulk data uploaded successfully!")
#                 return redirect("bulk_upload")

#             except Exception as e:
#                 messages.error(request, f"Error processing file: {e}")
#                 return redirect("bulk_upload")

#     else:
#         form = CSVUploadForm()

#     return render(request, "bulk_upload.html", {"form": form})
