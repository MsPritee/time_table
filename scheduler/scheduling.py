import random
from ortools.sat.python import cp_model
from .models import Subject, Teacher, Room, TimeSlot, Class

def assign_rooms(subject):
    """Dynamically assign labs for practical subjects and classrooms for theory subjects"""
    labs = list(Room.objects.filter(is_lab=True))
    classrooms = list(Room.objects.filter(is_lab=False))

    if subject.is_practical:
        return random.choice(labs) if labs else None  # Assign a lab if available
    else:
        return random.choice(classrooms) if classrooms else None  # Assign a classroom if available

def generate_timetable():
    model = cp_model.CpModel()

    # Fetch subjects, teachers, rooms, time slots, and classes from DB
    subjects = list(Subject.objects.all())
    teachers = list(Teacher.objects.all())
    rooms = list(Room.objects.all())
    timeslots = list(TimeSlot.objects.all())
    classes = list(Class.objects.all())

    # Shuffle rooms & timeslots to randomize the output
    random.shuffle(rooms)
    random.shuffle(timeslots)

    num_slots = len(timeslots)

    # Mapping: Subject → Teachers
    subject_teacher_map = {sub.name: list(sub.teachers.all()) for sub in subjects}

    # Mapping: Subject → Assigned Class
    subject_class_map = {sub.name: random.choice(classes).name for sub in subjects}

    # Variables: Lecture Schedule
    lecture_schedule = {}
    for subject in subjects:
        for slot in range(num_slots):
            lecture_schedule[(subject.name, slot)] = model.NewBoolVar(f"{subject.name}_slot_{slot}")

    # ✅ Constraint 1: Each subject must be scheduled **exactly once**
    for subject in subjects:
        model.Add(sum(lecture_schedule[(subject.name, slot)] for slot in range(num_slots)) == 1)

    # ✅ Constraint 2: No **room clash** (one subject per room per time slot)
    room_schedule = {room.name: [model.NewBoolVar(f"{room.name}_slot_{slot}") for slot in range(num_slots)] for room in rooms}
    for slot in range(num_slots):
        for room in rooms:
            model.Add(sum(room_schedule[room.name][slot] for room in rooms) <= 1)

    # ✅ Constraint 3: No **teacher teaches two subjects at the same time**
    teacher_schedule = {teacher.name: [model.NewBoolVar(f"{teacher.name}_slot_{slot}") for slot in range(num_slots)] for teacher in teachers}
    for slot in range(num_slots):
        for teacher in teachers:
            model.Add(sum(teacher_schedule[teacher.name][slot] for teacher in teachers) <= 1)

    # ✅ Constraint 4: Add **breaks** (Prevent consecutive lectures for teachers)
    for teacher in teachers:
        for slot in range(num_slots - 1):
            model.Add(teacher_schedule[teacher.name][slot] + teacher_schedule[teacher.name][slot + 1] <= 1)

    # ✅ Solve the problem
    solver = cp_model.CpSolver()
    solver.parameters.random_seed = random.randint(1, 1000)  # Ensures different results
    status = solver.Solve(model)

    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        timetable = []
        for subject in subjects:
            for slot in range(num_slots):
                if solver.Value(lecture_schedule[(subject.name, slot)]):
                    assigned_room = assign_rooms(subject).name  # Assign correct room type
                    assigned_teachers = ", ".join([teacher.name for teacher in subject_teacher_map[subject.name]])  
                    assigned_timeslot = f"{timeslots[slot % len(timeslots)].start_time} - {timeslots[slot % len(timeslots)].end_time}"  
                    assigned_class = subject_class_map[subject.name]  # Assign class
                    
                    timetable.append((subject.name, assigned_room, assigned_teachers, assigned_timeslot, assigned_class))
        
        return timetable
    else:
        return "No valid timetable found!"
