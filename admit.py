from fastapi import FastAPI, HTTPException
from enum import Enum
from datetime import datetime
import uvicorn
from typing import Union
"////////////////////////////////////////////////"

class Sex(Enum):
    Male = "Male"
    Female = "Female"

"////////////////////////////////////////////////"

class CageSize(Enum):
    S = 5.0
    M = 15.0
    L = 30.0
    XL = 30.0

"////////////////////////////////////////////////"

class Expertise(Enum):
    CAT = "CAT"
    DOG = "DOG"
    EXOTIC = "EXOTIC"

"////////////////////////////////////////////////"

class CageStatus(Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"

"////////////////////////////////////////////////"

class WardType(Enum):
    Standard = "Standard"
    Isotaion = "Isotation"

"////////////////////////////////////////////////"
class PetHospital :
    def __init__(self, name):
        self.__name = name
        self.__user_list = []
        self.__employee_list = []
        self.__admitted_list = []
        self.__ward_list = []
        self.__medical_record_list = []
        self.__examination_room_list = []
        self.__appointment_list = []
        self.__cage_booking_list = []

    def admit(self,MedicalRecordID,date_admit):
        Pet = None
        weight = None
        medical = None
        date_admit = self.valid_date(date_admit)
        for medical_record in self.__medical_record_list:
            if(MedicalRecordID == medical_record.get_medical_id()):
                Pet, weight = medical_record.get_approval()
                medical = medical_record
                break
        if(isinstance(Pet,PetProfile)):
            for ward in self.__ward_list:
                cage_no, ward_no =  ward.try_admit(Pet, weight)
                if(cage_no != None and ward_no != None):
                    
                    admit_record = AdmitRecord(Pet.get_id(), ward_no, cage_no, date_admit)
                    medical_record.write_admit_record(admit_record)
                    return f"admit success at cage {cage_no} ward {ward_no}"
    
            else:
                return f"no cage match available"
            
        elif(Pet == None): ## ไม่ได้มีการรีเทิร์น PetProfile = ไม่อนุมัติ 
            return "Not approved"

    def valid_date(self, date_time):
        try:
            date_time = datetime.strptime(date_time, "%d/%m/%Y %H:%M")
            return date_time
        except :
            raise HTTPException(status_code= 400, detail= "validate datetime format. dd/mm/yy hr:min")

    def make_medical_record(self, medical_id: str, date: str, pet: object, user: object, vet: object, symtomps: str, diagnosis: str,prescription: object, admit: bool):
        medical_rec = medical_record(medical_id,date,pet,user,vet,symtomps,diagnosis,prescription,admit)
        self.__medical_record_list.append(medical_rec)
        pet.add_medical_record(medical_rec)

    def add_ward(self,ward: object):
        self.__ward_list.append(ward)
    
    def get_med_list(self):
        return self.__medical_record_list

"////////////////////////////////////////////////"

class AdmitRecord():
    def __init__(self, pet_id: str, ward: object, cage: object, date_of_admit: str):
        self.__pet = pet_id
        self.__ward = ward
        self.__cage = cage
        self.__date_of_admit = date_of_admit
        self.__date_of_leave = None

    def get_pet(self):
        return self.__pet
    def get_cage(self):
        return self.__cage

    def check_out(self, date_leave: str):
        self.__date_of_leave = date_leave
"////////////////////////////////////////////////"

class Prescription:
    pass
"////////////////////////////////////////////////"

class Employee():
    def __init__(self, employee_id: str, hospital: str, salary: float):
        self.__employee_id = employee_id
        self.__hospital = hospital
        self.__salary = salary


class Vet(Employee):
    def __init__(self,employee_id: str, hospital: str, salary: float,vet_id: str, expertise: Expertise):
        self.__vet_id = vet_id
        self.__expertise = expertise
        super.__init__(employee_id, hospital, salary)

"////////////////////////////////////////////////"

class medical_record :
    def __init__(self,medical_id:str, date: str, pet: object, user :object, vet: object, symtomps: str, diagnosis: str, prescription: Prescription, admit: bool)  :
        self.__id = medical_id
        self.__datetime = date
        self.__pet = pet
        self.__user = user
        self.__vet = vet
        self.__symtomps = symtomps
        self.__diagnosis = diagnosis
        self.__perscription = prescription
        self.__admited_record = admit

    def get_medical_id(self) -> str:
        return self.__id

    def get_approval(self) -> Union[None,object]:
        "return Pet and weight if approved return None if not aprroved"
        if(self.__admited_record): 
            return self.__pet, self.__pet.get_information()
        
        return None, None

    def write_admit_record(self,admit_record: object):
        self.__admited_record = admit_record
        

    def get_admit_record(self):
        return self.__admited_record

"////////////////////////////////////////////////"

class PetProfile :
    def __init__(self, pet_id: str, name: str, species: str, weight: float, sex: Sex, birthdate: str):
        self.__pet_id = pet_id
        self.__name = name
        self.__species = species
        self.__weight = weight
        self.__sex = sex
        self.__birthdate = birthdate
        self.__medical_record_list = []

    def add_medical_record(self,medical_record: object):
        self.__medical_record_list.append(medical_record)

    def get_information(self) -> float:
        return self.__weight
    def get_id(self):
        return self.__pet_id

"////////////////////////////////////////////////"

class Ward :
    def __init__(self, ward_no: str, type: WardType, max_number_of_cage: int = 10):
        self.__ward_no = ward_no
        self.__type = type
        self.__cage_list = []
        self.__max_number_of_cage = max_number_of_cage


    def try_admit(self, Pet:object, weight: float):
        for cage in self.__cage_list:
            admit_cage = cage.can_admit(Pet, weight)
            if(admit_cage != None):
                return admit_cage, self.__ward_no

        return None, None
    
    def add_cage(self, cage: object):
        self.__cage_list.append(cage)

    def get_cage(self) -> list:
        "return cage_list in ward"
        return self.__cage_list
    
    def __str__(self):
        return self.__ward_no

"////////////////////////////////////////////////"

class Cage :
    def __init__(self, cage_no: str, cage_size: CageSize, pet: object ,cage_status: CageStatus):
        self.__cage_no = cage_no
        self.__cage_size = cage_size
        self.__pet = pet
        self.__cage_status = cage_status

    def can_admit(self, Pet: object, weight: float) -> Union[str, None]:
        "ถ้ากรงว่างและน้ำหนักสัตว์ไม่เกิน return True"
        if(self.__cage_status == CageStatus.AVAILABLE and weight < self.__cage_size.value):
            self.update_status(Pet)
            return self.__cage_no 
        
        return None
    
    def update_status(self, Pet: object):
        "รับ pet มาและupdate pet และ status ของกรงเป็น occupied"
        self.__pet = Pet
        self.__cage_status = CageStatus.OCCUPIED


    @property
    def cage_status(self): return self.__cage_status
    @property
    def no(self):
        return self.__cage_no
    def __str__(self):
     return self.__cage_no
"////////////////////////////////////////////////"

class User :
    def __init__(self ,user_id: str,  name: str, phone_num: str):
        self.__user_id = user_id
        self.__name = name
        self.__phone_no= phone_num
        self.__pet = []  
        self.__no_show_left = 3

"////////////////////////////////////////////////"

def create_test():
    hospital = PetHospital("Happy Pet Hospital")

    user1 = User("U001", "John", "0999999999")

    pet1 = PetProfile(
        "P001", "Lucky", "Dog", 4.0,
        Sex.Male, "2020-01-01"
    )

    prescription = Prescription()

    # =============================
    # CASE 1 : ADMIT SUCCESS
    # =============================

    hospital.make_medical_record("M001", "2026-02-18",
        pet1, user1, None,
        "Fever", "Infection",
        prescription,
        True  # approved
    )

    ward1 = Ward("W01", WardType.Standard)
    cage1 = Cage("C01", CageSize.S, None, CageStatus.AVAILABLE)

    ward1.add_cage(cage1)
    hospital.add_ward(ward1)




    # =============================
    # CASE 2 : NO CAGE AVAILABLE
    # =============================
    pet2 = PetProfile(
        "P002", "GeGee", "Dog", 4.0,
        Sex.Male, "2020-01-01"
    )

    hospital.make_medical_record( "M002", "2026-02-18",
        pet2, user1, None,
        "Fever", "Infection",
        prescription,
        True
    )

    ward2 = Ward("W02", WardType.Standard)
    cage2 = Cage("C02", CageSize.S, None, CageStatus.OCCUPIED)  # กรงไม่ว่าง

    ward2.add_cage(cage2)
    hospital.add_ward(ward2)



    # =============================
    # CASE 3 : NOT APPROVED
    # =============================

    hospital.make_medical_record("M003", "2026-02-18",
        pet1, user1, None,
        "Fever", "Infection",
        prescription,
        False   # ไม่อนุมัติ
        )
    return hospital

hospital =  create_test()
app = FastAPI()

@app.get("/")
def read_root():
    return {"welcome to" : "Pethospital"}

@app.post("/admit", tags=["admit"])
def admit(MedID: str, date_in: str)-> dict:
    
    status = hospital.admit(MedID, date_in)
    return {"status" : status}

@app.get("/admit",tags=["admit"])
def get_admit_record(MedID):
    for med in hospital.get_med_list():
        if(med.get_medical_id() == MedID):
            if(isinstance(med.get_admit_record(),AdmitRecord)):
                cage = med.get_admit_record().get_cage()
                pet_id = med.get_admit_record().get_pet()
                return {med.get_admit_record().get_pet() : cage}
            return {MedID : med.get_admit_record()}
    return {MedID : "can't find this ID"}

if __name__ == "__main__":
    uvicorn.run("admit:app",host="127.0.0.1",port=8000,reload=True)