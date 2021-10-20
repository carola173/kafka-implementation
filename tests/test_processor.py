import unittest

import numpy as np

from integrated_data_processing.shared_functions.agents import Processor


class TestProcessor:
    def test_generate_direction_features(self):
        params = {
            "pickup_longitude": -73.988129,
            "pickup_latitude": 40.732029,
            "dropoff_longitude": -73.990173,
            "dropoff_latitude": 40.756680,
        }
        response = Processor.generate_direction_features(params)
        assert np.round(response["direction"], 2) == -3.59

    def test_generate_distance_featires(self):
        params = {
            "pickup_longitude": -73.988129,
            "pickup_latitude": 40.732029,
            "dropoff_longitude": -73.990173,
            "dropoff_latitude": 40.756680,
        }
        response = Processor.generate_distance_features(params)
        assert np.round(response["distance"], 2) == 2.75

    def test_generate_date_features(self):
        params = {"pickup_datetime": "2016-03-14 17:24:55"}
        response = Processor.generate_date_features(params)
        assert response["month"] == 3
        assert response["week"] == 11
        assert response["weekday"] == 0
        assert response["hour"] == 17
        assert response["minute_oftheday"] == 1044

    def test_generate_one_hot_encoding(self):
        params = {"store_and_fwd_flag": "N", "vendor_id": 1}
        response = Processor.generate_one_hot_encoding(params)
        assert response["store_and_fwd_flag_N"] == 1
        assert response["store_and_fwd_flag_Y"] == 0
        assert response["vendor_id_1"] == 1
        assert response["vendor_id_2"] == 0

    def test_generate_features(self):
        params = {
            "pickup_longitude": -73.988129,
            "pickup_latitude": 40.732029,
            "dropoff_longitude": -73.990173,
            "dropoff_latitude": 40.756680,
            "store_and_fwd_flag": "N",
            "vendor_id": 1,
            "pickup_datetime": "2016-03-14 17:24:55",
        }
        response = Processor.generate_features(params)
        # Checking for not null response
        assert response != None
