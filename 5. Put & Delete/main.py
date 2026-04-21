from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):

    id: Annotated[str, Field(..., description='Id of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='Where the patient is living.')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male','female','others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in meters')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in Kgs')]


class PatientUpdate(BaseModel):
    
    name: Annotated[Optional[str], Field(default = None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male','female']], Field(default=None)]
    height: float
    weight: float


    @computed_field
    @property
    def bmi(self) -> float:
        if self.height is None or self.weight is None:
            raise ValueError("Height and Weight must not be None")

        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        
        if self.age < 18.5:
            return "Underweight"
        elif self.age < 25:
            return "Normal"
        elif self.age < 30:
            return "Extra"
        else:
            return "Obese"


def load_file():
    with open('patients.json', 'r') as file:
        data = json.load(file)

    return data

def save_data(data):
    with open('patients.json','w') as file:
        json.dump(data, file)


@app.get("/")
def message():
    return {'message':'Patient Records'}

@app.get("/about")
def about():
    return {'message':'Here you will find patient records.'}

@app.get("/view")
def view():
    data = load_file()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    # load all the patients
    data = load_file()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found.')


@app.get('/sort')
def sort_patients(sort_by: str = Query(...,description='Sort on the basis of height, weight, BMI'), order: str = Query('asc',description='sort in asc or desc order')):
    valid_fields = ['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid selection from {valid_fields}')
    
    if order not in ['desc','asc']:
        raise HTTPException(status_code=400, detail='Invalid order seletion.')
    
    data = load_file()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(data.values(),key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):

    # load existing data
    data = load_file()

    # check if the patient data already exist
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save into json
    save_data(data)

    return JSONResponse(status_code=201, content={'message':'Patient created successfully'})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update:PatientUpdate):

    data = load_file()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient id not found.')
    
    existing_patient_info = data[patient_id]

    update_existing_info = patient_update.model_dump(exclude_unset=True)

    for key, value in update_existing_info.items():
        existing_patient_info[key] = value

    # existing_patient_info -> pydantic object -> update bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)

    # -> pydantic object -> dict

    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'patient updated'})

