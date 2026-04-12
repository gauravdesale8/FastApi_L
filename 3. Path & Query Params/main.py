from fastapi import FastAPI, Path, HTTPException, Query
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
    raise HTTPException(status_code=404, detail='Patient not found.')


@app.get('/sort')
def sort_patients(sort_by: str = Query(...,description='Sort on the basis of height, weight, BMI'), order: str = Query('asc',description='sort in asc or desc order')):
    valid_fields = ['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid selection from {valid_fields}')
    
    if order not in ['desc','asc']:
        raise HTTPException(status_code=400, detail='Invalid order seletion.')
    
    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(data.values(),key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data