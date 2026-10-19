import json

# json me hm data ko store krte h, agr hm python ek variable me data store krte h to wo data sirf ussi variable me store hota h, but json me hm data ko file me store krte h, jisse hm us data ko kahi bhi access kr skte h aur restart krne pr bhi data save rhega, but python variable me data restart krne pr delete ho jata h

from abc import ABC, abstractmethod
from pathlib import Path

database = "school_data.json"

data = {"students": [], "teachers": []}

if Path(database).exists():
    with open(database, "r") as file:
        content = file.read()
        if content:
            data = json.loads(content)


def save():
    with open(database, "w") as file:
        json.dump(data, file, indent=4)


class Persons(ABC):
    @abstractmethod
    def get_roles(self):
        pass

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    def show_details(self):
        pass



    def add_grade(self):
        roll_no = input("tell the roll number:- ")
        subject = input("Subject:- ")
        marks = float(input("Marks:- "))

        for i in data["students"]:
            if i["roll_no"] == roll_no:
                i["grade"][subject] = marks
                save()
                print("Grades added succesfully")
                return
            else:
                print("Student not found")

    @staticmethod
    def validate_email(email):
        if "@" in email and "." in email:
            return True
        else:
            return False


class Students(Persons):
    def get_roles(self):
        return "student"

    def register(self):
        name = input("tell your name :- ")
        age = int(input("tell your age:- "))
        email = input("tell your mail:- ")
        roll_no = input("tell your roll number:- ")

        if not Persons.validate_email(email):
            print("invalid email")
            return

        for i in data["students"]:
            if i["roll_no"] == roll_no:  # <= Current Roll No
                print("student already exist")
                return

        data["students"].append(
            {"name": name, "age": age, "email": email, "roll_no": roll_no, "grade": {}}
        )
        save()
        print(f"Student {name} registered")

    def show_details(self):
        roll_no=input("Roll no- ")
        for s in data ["students"]:
            if s["roll_no"]==roll_no:
                grade = s['grade']
                avg = sum(grade.values()) / len(grade) if grade else 0

                print(f"\n  Name    : {s['name']}")
                print(f"  Roll no : {s['roll_no']}")
                print(f"  Grade  : {grade}")
                print(f"  Average : {avg:.1f}")
                return


class Teacher(Persons):
    def get_roles(self):
        return "teachers"

    def register(self):
        name = input("tell your name :- ")
        age = int(input("tell your age:- "))
        email = input("tell your mail:- ")
        subject = input("subject:- ")
        emp_id = input("tell your emp id number:- ")

        if not Persons.validate_email(email):
            print("invalid email")
            return

        for i in data["teachers"]:
            if i["emp_id"] == emp_id:  # <= Current Roll No
                print("teacher already exist")
                return

        data["teachers"].append(
            {
                "name": name,
                "age": age,
                "email": email,
                "subject": subject,
                "emp_id": emp_id,
            }
        )
        save()
        print(f"Teacher {name} registered")

    def show_details(self):
        emp_id = input("Employee ID: ")

        for t in data["teachers"]:
            if t["emp_id"] == emp_id:
                print(f"\n  Name    : {t['name']}")
                print(f"  Subject : {t['subject']}")
                print(f"  Emp ID  : {t['emp_id']}")
                return
        print("Teacher not found.")


stud = Students()
Teach = Teacher()


print("Press 1 to register a student")
print("Press 2 to register a teacher")
print("Press 3 to add grades")
print("Press 4 to show a student detail")
print("Press 5 to show a teacher detail")


choice = int(input("Please tell your choice:- "))


if choice == 1:
    stud.register()

elif choice == 2:
    Teach.register()

elif choice == 3:
    stud.add_grade()

elif choice == 4:
    stud.show_details()

elif choice == 5:
    Teach.show_details()

else:
    print("Invalid choice")
