from ortools.sat.python import cp_model
from scheduler.models import Teacher, Subject, Class, Room, TimeSlot

def generate_timetable():
    """Generate an optimized timetable using Google OR-Tools."""
    
    model = cp_model.CpModel()
    
    # Fetch data from the database
    teachers = list(Teacher.objects.all())
    subjects = list(Subject.objects.all())
    classes = list(Class.objects.all())
    timeslots = list(TimeSlot.objects.all())
    rooms = list(Room.objects.all())

    # Create variables for each (class, subject, teacher, timeslot, room)
    schedule = {}
    for cls in classes:
        for subject in subjects:
            if cls in subject.classes.all():
                for teacher in subject.teachers.all():
                    for timeslot in timeslots:
                        for room in rooms:
                            schedule[(cls, subject, teacher, timeslot, room)] = model.NewBoolVar(
                                f"{cls}_{subject}_{teacher}_{timeslot}_{room}"
                            )

    # Constraints
    # 1️⃣ Each class should have only one subject at a time
    for cls in classes:
        for timeslot in timeslots:
            model.Add(sum(schedule[(cls, s, t, timeslot, r)] 
                          for s in subjects 
                          for t in s.teachers.all() 
                          for r in rooms if (cls, s, t, timeslot, r) in schedule) <= 1)

    # 2️⃣ A teacher should not be assigned to multiple subjects at the same time
    for teacher in teachers:
        for timeslot in timeslots:
            model.Add(sum(schedule[(c, s, teacher, timeslot, r)] 
                          for c in classes 
                          for s in subjects 
                          for r in rooms if (c, s, teacher, timeslot, r) in schedule) <= 1)

    # 3️⃣ Room allocation: One subject per room at a time
    for room in rooms:
        for timeslot in timeslots:
            model.Add(sum(schedule[(c, s, t, timeslot, room)] 
                          for c in classes 
                          for s in subjects 
                          for t in s.teachers.all() if (c, s, t, timeslot, room) in schedule) <= 1)

    # Objective: Distribute lectures evenly
    model.Maximize(sum(schedule.values()))

    # Solve the problem
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        timetable = []
        for key, var in schedule.items():
            if solver.Value(var) == 1:
                timetable.append({
                    "class": key[0].name,
                    "subject": key[1].name,
                    "teacher": key[2].name,
                    "timeslot": f"{key[3].start_time} - {key[3].end_time}",
                    "room": key[4].name,
                })
        return timetable
    else:
        return "No feasible schedule found!"

