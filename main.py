from fastapi import FastAPI
import uvicorn

from enum import Enum
from datetime import datetime

class Species(Enum):
    DOG = 0
    CAT = 1
    EXOTIC = 2

class Sex(Enum):
    MALE = 0
    FEMALE = 1

class AppointmentStatus(Enum):
    SCHEDULED = 0
    CHECKED_IN = 1
    COMPLETED = 2
    CANCELLED = 3
    NO_SHOW = 4

class PetProfile:
    def __init__(self, pet_id: str, name: str, species: Species, weight: float, sex: Sex, birthdate: str):
        self.__id = pet_id
        self.__name = name
        self.__species = species
        self.__weight = weight
        self.__sex = sex
        self.__birthdate = birthdate
        self.__medical_records = []
    
    @property
    def id(self):
        return self.__id
    
    @property
    def species(self):
        return self.__species

class User:
    def __init__(self, user_id: str, name: str):
        self.__user_id = user_id
        self.__name = name
        self.__no_show_left = 3
        self.__pet_list = []

    @property
    def user_id(self):
        return self.__user_id
    
    @property
    def no_show_left(self):
        return self.__no_show_left

    def add_petprofile(self, pet_id: str, name: str, species: Species, weight: float, sex: Sex, birthdate: str):
        self.__pet_list.append(PetProfile(pet_id, name, species, weight, sex, birthdate))

    def get_pet_by_id(self, pet_id: str):
        for pet in self.__pet_list:
            if pet.id == pet_id:
                return pet
        return None

class Employee(User):
    def __init__(self, employee_id: str, user_id: str, name: str, salary: float):
        super().__init__(user_id, name)
        self.__employee_id = employee_id
        self.__salary = salary
    
    @property
    def employee_id(self):
        return self.__employee_id

class PetHospital:
    def __init__(self, name):
        self.__name = name
        self.__user_list = []
        self.__employee_list = []
        self.__appointment_list = []

    def add_user(self, user: User):
        self.__user_list.append(user)
    
    def add_employee(self, employee: Employee):
        self.__employee_list.append(employee)

    def search_user_by_id(self, user_id: str):
        for user in self.__user_list:
            if user_id == user.user_id:
                return user
        return None
    
    def search_employee_by_id(self, employee_id: str):
        for employee in self.__employee_list:
            if employee_id == employee.employee_id:
                return employee
        return None
    
    def check_user_eligibility(self, user: User):
        if user.no_show_left == 0:
            return False
        else:
            # มี appointment ที่ยังไม่เสร็จ
            for appt in self.__appointment_list:
                if appt.user_id == user.user_id and appt.appointment_status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CHECKED_IN]:
                    return False
        return True
    
    def book_appointment(self, user_id: str, vet_id: str, pet_id: str, chosen_date: datetime):
        
        user = self.search_user_by_id(user_id)
        vet = self.search_employee_by_id(vet_id)
        petprofile = user.get_pet_by_id(pet_id)

        if not vet.is_compatible_with(petprofile.species):
            return "แพทย์คนนี้ไม่สามารถรักษาสัตว์ประเภทนี้ได้"
        
        if not self.check_user_eligibility(user):
            return "ไม่สามารถจองได้ ติดเงื่อนไข"
        
        if not vet.is_available_at(chosen_date):
            return "เวลานี้ถูกจองแล้ว"
        
        import uuid
        appointment_id = uuid.uuid4()

        new_appointment = Appointment(appointment_id, user_id, vet_id, petprofile, chosen_date, status=AppointmentStatus.SCHEDULED)
        self.__appointment_list.append(new_appointment)

        return new_appointment

class Appointment:
    def __init__(self, appointment_id: str, user_id: str, vet_id: str, petprofile: PetProfile, chosen_date: datetime, status):
        self.appointment_id = appointment_id
        self.appointment_status = status
        self.date = chosen_date
        self.vet_id = vet_id
        self.user_id = user_id
        self.petprofile = petprofile

class TimeSlot:
    def __init__(self, date : datetime):
        self.date = date
        self.available = True
        self.__duration = 1 # hours

class Vet(Employee):
    def __init__(self, employee_id: str, user_id: str, name: str, salary: float, expertise: Species):
        super().__init__(employee_id, user_id, name, salary)
        self.__expertise = expertise
        self.__current_appointment = None
        self.__timeslot_list = []
    
    def add_timeslot(self, datetime : datetime):
        self.__timeslot_list.append(TimeSlot(datetime))

    def is_compatible_with(self, species: Species):
        return species == self.__expertise

    def is_available_at(self, chosen_time : datetime):
        for slot in self.__timeslot_list:
            if slot.date == chosen_time and slot.available:
                return True
        return False

def create_instances():
    system = PetHospital("Smart Pet Clinic")

    user = User("0", "Tam")
    user.add_petprofile("0", "aidum", Species.DOG, 12.00, Sex.MALE, datetime(2017, 4, 13))

    vet1 = Vet("111", "1", "Dr. Somchai", 35000.00, Species.DOG)
    vet2 = Vet("112", "2", "Dr. Jaibun", 35000.00, Species.CAT)

    vet1.add_timeslot((datetime(2026, 2, 23, 11, 0)))
    vet1.add_timeslot((datetime(2026, 2, 23, 12, 0)))

    system.add_user(user)
    system.add_employee(vet1)
    system.add_employee(vet2)

    return system

system = create_instances()
    
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Pet Hospital"}

@app.post("/book_appointment")
def book_appointment(user_id: str, vet_id: str, pet_id: str, chosen_date: str):

    fmt = "%Y-%m-%d %H:%M"
    try:
        formated_desired_date = datetime.strptime(chosen_date, fmt)
        result = system.book_appointment(user_id, vet_id, pet_id, formated_desired_date)
        if isinstance(result, str):
            return {"success": False, "message": result}
        
        return {
            "success" : True,
            "data" : {
                "appointment_id": result.appointment_id,
                "appointment_status": result.appointment_status,
                "date": result.date,
                "vet_id": result.vet_id,
                "user_id": result.user_id,
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Sum ting wong: {str(e)}"}
    
if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)