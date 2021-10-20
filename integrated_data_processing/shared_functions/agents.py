import logging
from datetime import timedelta
from typing import Dict

import numpy as np
import pandas as pd
import requests
from app import app

"""
 :
 1. Create a variable record_topic that listen to the topic nyc_taxi
 2. Create a variable processed_topic that listen to the topic nyc_taxi_processed
 3. Set the variable server_url to  "http://127.0.0.1:8000/predict"

Hint:
You are need to use the topic function present in the app class that is imported above.

"""

"""
------------------------------YOUR CODE ----------------------------------------
"""



"""
------------------------------ END CODE ----------------------------------------
"""

logger = logging.getLogger(__name__)


@app.agent(record_topic, sink=[processed_topic])
async def process_record(stream):
    """
    Function to generate the features for each record, and push them into another kafka topic.
    """
    async for records in stream.take(max_=100, within=timedelta(seconds=5)):
        for record in records:
            columns = record["columns"]
            values = record["values"]
            mapping = dict(zip(columns, values))
            record_id = int(mapping["id"].split("id")[1])
            new_record = Processor.generate_features(mapping)
            logger.debug(f"Feature generation successful for record: {record_id}")
            yield new_record


@app.agent(processed_topic)
async def predict(stream):
    """
    Function to predict the trip duration for the given record.
    """
    async for records in stream.take(max_=100, within=timedelta(seconds=5)):
        for record in records:
            response = requests.post(server_url, json=record)
            if response.status_code == 200:
                val = response.json()["prediction"]
                logger.info(f"Trip duration for ID: {record['id']} : {val}")
            else:
                error = response.json()
                logger.error(f"Prediction failed for record: {record['id']} with errors: {error}")


class Processor:
    """
    Class containing functions to perform feature engineering.

    NOTE: Initially, this was in a seperate file, but importing the class from another file caused faust to not detect
    the agents defined above. I was unable to fix the cause for it, so I've moved it here.
    """

    AVG_EARTH_RADIUS = 6371

    @classmethod
    def generate_direction_features(cls, record: Dict[str, str]) -> Dict[str, str]:
        """
        Function to generate the direction feature. Here, we will use the haversine distance
        """
        (lat1, lng1, lat2, lng2) = (
            float(record["pickup_latitude"]),
            float(record["pickup_longitude"]),
            float(record["dropoff_latitude"]),
            float(record["dropoff_longitude"]),
        )
        lng_delta_rad = np.radians(lng2 - lng1)
        [lat1, lng1, lat2, lng2] = list(map(np.radians, (lat1, lng1, lat2, lng2)))
        y = np.sin(lng_delta_rad) * np.cos(lat2)
        x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(lng_delta_rad)
        record["direction"] = np.degrees(np.arctan2(y, x))
        return record

    @classmethod
    def generate_distance_features(cls, record: Dict[str, str]) -> Dict[str, str]:
        """
        Function to generate the distance feature. Here, we will use the haversine distance
        """
        (lat1, lng1, lat2, lng2) = (
            float(record["pickup_latitude"]),
            float(record["pickup_longitude"]),
            float(record["dropoff_latitude"]),
            float(record["dropoff_longitude"]),
        )
        [lat1, lng1, lat2, lng2] = list(map(np.radians, (lat1, lng1, lat2, lng2)))
        lat_diff = lat2 - lat1
        lng_diff = lng2 - lng1
        distance = np.sin(lat_diff * 0.5) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(lng_diff * 0.5) ** 2
        haversine = 2 * cls.AVG_EARTH_RADIUS * np.arcsin(np.sqrt(distance))
        record["distance"] = haversine
        return record

    @classmethod
    def generate_date_features(cls, record: Dict[str, str]) -> Dict[str, str]:
        """
        Function to generate the datetime related features for the given record.

        :param record: Record containing data

        :return: Dictionary containing the date features as independent columns
        """
        pickup_datetime = pd.to_datetime(record.get("pickup_datetime"))
        record["month"] = pickup_datetime.month
        record["week"] = pickup_datetime.week
        record["weekday"] = pickup_datetime.weekday()
        record["hour"] = pickup_datetime.hour
        record["minute"] = pickup_datetime.minute
        record["minute_oftheday"] = record["hour"] * 60 + record["minute"]
        record.pop("minute")
        record.pop("pickup_datetime")
        return record

    @classmethod
    def generate_one_hot_encoding(cls, record: Dict[str, str]) -> Dict[str, str]:
        """
        Function to perform one hot encoding on the given record. Here, we will perform the operation
        only on two columns: `store_and_fwd_flag` and `vendor_id`.
        We can represent the values with just a single column, since there are only two values.
        For now, we will keep each value in a different column.

        :param record: Record containing data

        :return: Dictionary containing the one hot encoded columns along with the remaining data.
        """
        # We will generate the OHE for the `store_and_fwd_flag` column
        flag_val = record.get("store_and_fwd_flag")
        if flag_val == "Y":
            record["store_and_fwd_flag_Y"] = 1
            record["store_and_fwd_flag_N"] = 0
        else:
            record["store_and_fwd_flag_Y"] = 0
            record["store_and_fwd_flag_N"] = 1
        vendor_val = record.get("vendor_id")
        if vendor_val == 1:
            record["vendor_id_1"] = 1
            record["vendor_id_2"] = 0
        else:
            record["vendor_id_1"] = 0
            record["vendor_id_2"] = 1
        # Delete the keys
        record.pop("store_and_fwd_flag")
        record.pop("vendor_id")
        return record

    @classmethod
    def generate_features(cls, record: Dict[str, str]) -> Dict[str, str]:
        """
        Function to generate all the required features for the dataset.
        These features are explained in the research notebooks.
        """
        one_hot_record = cls.generate_one_hot_encoding(record)
        date_record = cls.generate_date_features(one_hot_record)
        distance_record = cls.generate_distance_features(date_record)
        final_record = cls.generate_direction_features(distance_record)
        return final_record
