import argparse
import csv
import json
import uuid

from confluent_kafka import Producer

bootstrap_servers = "localhost:29092"


class DataPublisher:

    COLUMN_NAMES = [
        "id",
        "vendor_id",
        "pickup_datetime",
        "passenger_count",
        "pickup_longitude",
        "pickup_latitude",
        "dropoff_longitude",
        "dropoff_latitude",
        "store_and_fwd_flag",
    ]
    TOPIC = "nyc_taxi"

    @classmethod
    def confluent_kafka_producer(cls, num_records: int) -> None:
        """
        Function to produce messages to kafka. For now, we will only publish messages from the test dataset
        """
        with open("integrated_data_processing/data_raw/test.csv", "r") as infile:
            producer = Producer({"bootstrap.servers": bootstrap_servers})
            reader = csv.DictReader(infile, fieldnames=cls.COLUMN_NAMES)
            count = 0
            for record in reader:
                if count == 0:
                    # Skipping the header row
                    count += 1
                    continue
                record_key = str(uuid.uuid4())
                record_value = json.dumps({"columns": cls.COLUMN_NAMES, "values": list(record.values())})

                """
                    1. Use the producer object to call the produce function with the parameters : cls.TOPIC, key=record_key, value=record_value
                    2. Use the produce object to call the poll function
                """
                """
                    -------------------------------YOUR CODE ------------------------------------------
                """
               

                """
                    -------------------------------END YOUR CODE ------------------------------------------
                """

                count += 1
                if count == num_records:
                    break

            producer.flush()
            print("Sent {count} messages to {brokers}".format(count=count, brokers=bootstrap_servers))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publish messages to Kafka")
    parser.add_argument(
        "-n",
        "--num-records",
        type=int,
        help="number of records to publish",
        default=10,
    )
    args = parser.parse_args()
    DataPublisher.confluent_kafka_producer(args.num_records)
