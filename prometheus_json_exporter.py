import json
from jsonpath_ng import parse
from flask import Flask, Response
import requests
import argparse
import yaml

def load_configuration(file_url):
    with open(file_url) as f:
        config = yaml.safe_load(f)
    return config

def find_metric_values(json_data, json_path):
    metric_expr = parse(json_path)
    metric_values = [match.value for match in metric_expr.find(json_data)]
    return metric_values

def build_metric_strings(group_name, metric_name, metric_labels, metric_values):
    metric_data = []
    for value in metric_values:
        labels = ','.join([f'{label}="{metric_labels[label]}"' for label in metric_labels.keys()])
        metric_str = f'{group_name}_{metric_name}{{{labels}}} {value}\n'
        metric_data.append(metric_str)
    return metric_data

def create_app(config):
    app = Flask(__name__)

    @app.route('/metrics', methods=['GET'])
    def metrics():
        metric_data = []
        for group in config['groups']:
            group_name = group['name']
            json_source = group['json_source']

            # Load the JSON data from either a local file or remote URL
            if json_source.startswith('http://') or json_source.startswith('https://'):
                response = requests.get(json_source)
                if response.status_code == 200:
                    json_data = response.json()
                else:
                    raise Exception(f"Failed to load JSON data from: {json_source}")
            else:
                with open(json_source) as f:
                    json_data = json.load(f)

            for metric in group['metrics']:
                metric_name = metric['name']
                metric_labels = metric.get('labels', {})
                metric_values = find_metric_values(json_data, metric['json_path'])
                metric_strings = build_metric_strings(group_name, metric_name, metric_labels, metric_values)
                metric_data.extend(metric_strings)

        response = Response(''.join(metric_data), content_type='text/plain')
        return response

    return app

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-url', help='URL of the remote YAML configuration file')
    parser.add_argument('--target-host', help='Target host for the Flask server')
    parser.add_argument('--target-port', type=int, help='Target port for the Flask server')
    args = parser.parse_args()

    # Load the remote YAML configuration
    config = load_configuration(args.config_url)

    # Create the Flask app
    app = create_app(config)

    # Start the Flask server
    app.run(host=args.target_host, port=args.target_port)
