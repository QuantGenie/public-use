import time
from prometheus_client import start_http_server, Summary, Counter
import json

# Create Prometheus metrics
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
REQUEST_COUNT = Counter('request_count', 'Total count of requests')

# Load JSON data from a file
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Parse JSON data and update Prometheus metrics
def process_json(json_data):
    # Process your JSON data here and update metrics
    # For example, assuming the JSON contains a list of items
    item_count = len(json_data)
    REQUEST_COUNT.inc(item_count)

# Start an HTTP server to expose the metrics
def start_metrics_server(port):
    start_http_server(port)
    print(f'Prometheus exporter is listening on port {port}...')

if __name__ == '__main__':
    # Provide the path to your JSON file
    json_file_path = 'C:/Practice/airflow/Airflow-Dag_manager/sample_json.json'

    # Load JSON data
    json_data = load_json(json_file_path)

    # Start the metrics server on port 8000
    start_metrics_server(8000)

    while True:
        # Load JSON data
        json_data = load_json(json_file_path)

        # Process the JSON data and update metrics
        process_json(json_data)

        # Wait for 10 seconds before reloading the JSON file
        time.sleep(3)
