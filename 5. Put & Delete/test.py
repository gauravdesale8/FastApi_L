from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()


# =========================
# 🧍 Patient Model (Full Data)
# =========================
class Patient(BaseModel):
    id: Annotated[str, Field(..., description='Id of the patient', examples=['P001'])]
    name: Annotated[str, Field(...)]
    city: Annotated[str, Field(...)]
    age: Annotated[int, Field(..., gt=0, lt=120)]
    gender: Annotated[Literal['male', 'female', 'others'], Field(...)]
    height: Annotated[float, Field(..., gt=0)]
    weight: Annotated[float, Field(..., gt=0)]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"


# =========================
# ✏️ Update Model (Partial)
# =========================
class PatientUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0)
    gender: Optional[Literal['male', 'female', 'others']] = None
    height: Optional[float] = Field(default=None, gt=0)
    weight: Optional[float] = Field(default=None, gt=0)


# =========================
# 📂 File Handling
# =========================
def load_file():
    try:
        with open('patients.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_data(data):
    with open('patients.json', 'w') as file:
        json.dump(data, file, indent=4)


# =========================
# 🏠 Routes
# =========================
@app.get("/")
def home():
    return {'message': 'Patient Records API'}


@app.get("/view")
def view_all():
    return load_file()


@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(...)):
    data = load_file()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    return data[patient_id]


# =========================
# ➕ Create Patient
# =========================
@app.post('/create')
def create_patient(patient: Patient):
    data = load_file()

    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)

    return JSONResponse(status_code=201, content={'message': 'Patient created'})


# =========================
# ✏️ Update Patient
# =========================
@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_file()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    existing = data[patient_id]

    updates = patient_update.model_dump(exclude_unset=True)

    # apply updates
    for key, value in updates.items():
        existing[key] = value

    # rebuild full object (this recalculates BMI safely)
    existing['id'] = patient_id
    updated_patient = Patient(**existing)

    data[patient_id] = updated_patient.model_dump(exclude=['id'])
    save_data(data)

    return {'message': 'Patient updated successfully'}


# =========================
# 🔃 Sort Patients
# =========================
@app.get('/sort')
def sort_patients(
    sort_by: str = Query(..., description='height, weight, bmi'),
    order: str = Query('asc')
):
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Choose from {valid_fields}')

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Order must be asc or desc')

    data = load_file()

    reverse = True if order == 'desc' else False

    def get_sort_value(patient_dict):
        if sort_by == 'bmi':
            temp = Patient(**patient_dict, id="temp")
            return temp.bmi
        return patient_dict.get(sort_by, 0)

    sorted_data = sorted(data.values(), key=get_sort_value, reverse=reverse)

    return sorted_data

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    #load data
    data = load_file()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient Not Found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'Patient Deleted'})