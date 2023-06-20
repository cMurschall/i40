from influxdb_client import InfluxDBClient
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np


def read_environment_variables():
    env_vars = {}
    with open("./environment.env") as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue

            key, value = line.strip().split('=', 1)
            env_vars[key] = value
    return env_vars



def read_shellies():
    environment_variables = read_environment_variables()

    organization = environment_variables["DOCKER_INFLUXDB_INIT_ORG"]
    token = environment_variables["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"]

    client = InfluxDBClient(url="http://localhost:8086", token=token, org=organization)

    query = client.query_api()

    q = """data = from(bucket: "AdlerTasks")
          |> range(start: 0, stop: now())
          |> filter(fn: (r) => r["_measurement"] == "shellies" and r["Sensor"] == "power")
          |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
          |> group(columns: ["_measurement"])
          |> pivot(columnKey: ["_field"], rowKey:["_time"], valueColumn: "_value")
          |> yield()
    """

    df = query.query_data_frame(q)

    df["_time"] = pd.to_datetime(df['_time'])
    return df


def find_step():
    df = read_shellies()
    data = df["value"].to_numpy()

    data -= np.average(data)
    step = np.hstack((np.ones(len(data)), -1 * np.ones(len(data))))

    data_step = np.convolve(data, step, mode='valid')
    step_index= np.argmax(data_step)

    step_time = df["_time"].loc[step_index]

    # plots
    fig, ax1 = plt.subplots()
    ax1.plot(df["_time"], data_step[:-1] / 10,color='salmon')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(df["_time"], df["value"], color='yellowgreen')

    ax1.plot((step_time, step_time), (data_step[step_index] / 10, 0), 'r')
    ax1.xaxis.set_major_formatter(DateFormatter('%d.%m.'))

    ax1.text(step_time, data_step[step_index] / 10, step_time.strftime("%m.%d. %H:%M Uhr"), color='r')
    plt.show()

if __name__ == '__main__':
    find_step()


    #fig, ax = plt.subplots()
    #plt.plot(df["_time"], df["value"])

    #ax.xaxis.set_major_formatter(DateFormatter('%d.%m.'))
    #_ = plt.xticks(rotation=90)

    #plt.show()
