from flask import Flask, jsonify

app = Flask(__name__)

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate an API token from the "API Tokens Tab" in the UI
token = "<api_token>"
org = "samela.io"
bucket = "weatherstation"

def getLastValue(field):
    with InfluxDBClient(url="http://192.168.1.5:8086", token=token, org=org) as client:
        query = f''' from(bucket: "weatherstation")
            |> range(start: -10m, stop: now())
            |> filter(fn: (r) => r["_measurement"] == "Acurite-5n1")
            |> filter(fn: (r) => r["_field"] == "{field}")
            |> filter(fn: (r) => r["channel"] == "A")
            |> filter(fn: (r) => r["id"] == "1663")
            |> last()
        '''
        tables = client.query_api().query(query, org=org)

        return tables[0].records[0]['_value']

@app.route('/')
def index():
    return 'Homebridge influx-db weather station relay. Visit <a href="/data">/data</a> for current weather data as json.'

@app.route('/data')
def data():
    return jsonify(
        {
            'temperature': getLastValue('temperature_F'),
            'humidity': getLastValue('humidity'),
            'wind_speed': getLastValue('wind_avg_km_h'),
            'wind_dir_deg': getLastValue('wind_dir_deg'),
            'rain_in': getLastValue('rain_in')
        }
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
