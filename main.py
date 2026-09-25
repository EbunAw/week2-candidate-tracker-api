from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import joblib
import pandas as pd

# Create FastAPI application
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Load the trained model
model = joblib.load("models/model.pkl")


# Define the prediction input
class CustomerData(BaseModel):
    tenure: int
    monthly_charges: int
    contract_type: int
    payment_method: int


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )


@app.post("/predict")
def predict(data: CustomerData):

    # Arrange the input in the same order used during training
    features = pd.DataFrame([{
        "tenure": data.tenure,
        "monthly_charges": data.monthly_charges,
        "contract_type": data.contract_type,
        "payment_method": data.payment_method
    }])

    # Make prediction
    prediction = model.predict(features)[0]

    # Get probability of churn
    probability = model.predict_proba(features)[0][1]

    return {
        "prediction": int(prediction),
        "churn_probability": round(float(probability), 2)
    }