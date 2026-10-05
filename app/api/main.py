from fastapi import FastAPI, HTTPException
from starlette import status
from src.predict import predict_mutagenicity
from src.predict_bcf import predict_bcf
from pydantic import BaseModel

app = FastAPI()

class BCFPrediction(BaseModel):
    smiles: str
    prediction_log: float
    prediction_display: str

class SMILESInput(BaseModel):
    smiles: str


@app.get("/")
def root():
    return {
        "message": "QSPR Prediction API",
        "endpoints": {
            "mutagenicity": "/predict/mutagenicity (POST)",
            "bcf": "/predict/bcf (POST)",
        },
        "docs": "/docs",
    }    

@app.post("/predict/mutagenicity")
def mutagenicity_endpoint(input: SMILESInput):
    try:
        return predict_mutagenicity(input.smiles)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/predict/bcf", response_model=BCFPrediction)
def bcf_endpoint(input: SMILESInput):
    try:
        result = predict_bcf(input.smiles)
        return BCFPrediction(
            smiles=input.smiles,
            prediction_log=result["prediction_log"],
            prediction_display=result["display"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



