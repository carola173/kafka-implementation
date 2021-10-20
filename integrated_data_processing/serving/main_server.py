import pickle

import numpy as np

# Server
from fastapi import FastAPI
from pydantic import BaseModel

# Modeling

app = FastAPI()

# Initialize files
clf = pickle.load(open("../data_raw/model.pickle", "rb"))
features = pickle.load(open("../data_raw/features.pickle", "rb"))


class Record(BaseModel):
    id: str
    passenger_count: int
    pickup_longitude: float
    pickup_latitude: float
    dropoff_longitude: float
    dropoff_latitude: float
    distance: float
    direction: float
    store_and_fwd_flag_Y: int
    store_and_fwd_flag_N: int
    vendor_id_1: int
    vendor_id_2: int
    month: int
    week: int
    weekday: int
    hour: int
    minute_oftheday: int


@app.post("/predict")
def predict(data: Record):

    # Extract data in correct order
    data_dict = data.dict()
    to_predict = np.asarray([data_dict[feature] for feature in features])

    # Create and return prediction
    prediction = clf.predict(to_predict.reshape(1, -1))

    return {"prediction": np.exp(prediction[0])}
