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


def read_signal(signal):
    environment_variables = read_environment_variables()

    organization = environment_variables["DOCKER_INFLUXDB_INIT_ORG"]
    token = environment_variables["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"]

    client = InfluxDBClient(url="http://localhost:8086", token=token, org=organization)

    query = client.query_api()

    q = f"""from(bucket: "AdlerTasksNewData")
      |> range(start: 0, stop: now())
      |> filter(fn: (r) => r["_measurement"] == "DS_SS23_TrayStates_B")
      |> filter(fn: (r) => r["Sensor"] == "{signal}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> yield() """

    df = query.query_data_frame(q)

    df["_time"] = pd.to_datetime(df['_time'])
    df = df.drop(columns=["_start", "_stop"])  # they are useless
    return df


def find_step():
    df = read_shellies()
    data = df["value"].to_numpy()

    data -= np.average(data)
    step = np.hstack((np.ones(len(data)), -1 * np.ones(len(data))))

    data_step = np.convolve(data, step, mode='valid')
    step_index = np.argmax(data_step)

    step_time = df["_time"].loc[step_index]

    # plots
    fig, ax1 = plt.subplots()
    ax1.plot(df["_time"], df["value"], color='yellowgreen', label="Measurements")
    ax1.set_ylabel("Power")

    ax1.xaxis.set_major_formatter(DateFormatter('%d.%m.'))

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(df["_time"], data_step[:-1] / 10, color='salmon', label="Convolved with step")
    ax2.plot((step_time, step_time), (data_step[step_index] / 10, 0), 'r')

    ax2.text(df["_time"].loc[step_index - 620], 10, step_time.strftime("%m.%d. %H:%M Uhr"), color='r')
    ax2.set_yticklabels([])




    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='lower right')

    plt.show()


def analyze_waggons():
    signal_10B3 = read_signal("10B3")
    signal_cam = read_signal("KameraP")

    print(f"Total time {(signal_cam['_time'].max() - signal_cam['_time'].min()).total_seconds():.2f} s")
    print(f"Total time {(signal_10B3['_time'].max() - signal_10B3['_time'].min()).total_seconds():.2f} s")

    # we cast to int
    signal_cam["value"].astype("int32")
    # ignore waggon 0
    signals_cam = signal_cam[signal_cam["value"] != 0]

    df_times = pd.DataFrame(columns=['delta_time', 'waggon'])
    for index, row in signals_cam[:-1].iterrows():
        # for each waggon let's find the next occurrence
        for index_n, row_n in signals_cam[index:].iterrows():
            if row_n["value"] == row["value"]:
                new_item = {
                    'delta_time': (row_n["_time"] - row["_time"]).total_seconds(),
                    'waggon': row["value"]
                }
                df_times = pd.concat([df_times, pd.DataFrame([new_item])])
                break

    print(f"Roundtrip times: ")
    print(df_times.groupby(["waggon"]).agg(['count', 'mean', 'std']))


def analyze_waggons_loads():
    signal_10B3 = read_signal("10B3")[10:]
    signal_cam = read_signal("KameraP")[10:]
    signal_cam = signal_cam[signal_cam["value"] != 0]

    print(f"Total time {(signal_cam['_time'].max() - signal_cam['_time'].min()).total_seconds():.2f} s")
    print(f"Total time {(signal_10B3['_time'].max() - signal_10B3['_time'].min()).total_seconds():.2f} s")

    signal_10B3["state"] = np.where(signal_10B3["value"] > 0.1, "On", "Off")

    fig, ax1 = plt.subplots()
    colors = {'On': 'tab:green', 'Off': 'tab:red'}
    ax1.scatter(signal_10B3["_time"], signal_10B3["state"], c=signal_10B3["state"].map(colors))
    ax1.set_ylabel("Signal 10B3 state")

    signal_cam["value"].astype(np.int32).astype("str")
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    colors = {'12': 'tab:brown', '19': 'tab:orange', '23': 'tab:purple', '24': 'tab:brown'}
    wagons = signal_cam["value"].astype(np.int32).astype("str")
    ax2.scatter(signal_cam["_time"], wagons, c=wagons.map(colors))
    ax2.margins(y=0.4)
    ax2.set_ylabel("Waggon")

    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    plt.title("Waggon loads")
    plt.show()


if __name__ == '__main__':
    find_step()
    analyze_waggons_loads()
