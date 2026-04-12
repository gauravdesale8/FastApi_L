from fastapi import FastAPI, Path
import json

app = FastAPI()

def load_data():
    with open('patients.json','r') as file:
        data = json.load(file)

    return data

@app.get("/")
def message():
    return {'message':'Patient Records'}

@app.get("/about")
def about():
    return {'message':'Here you will find patient records.'}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    # load all the patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    return {'error':'patient not found'}