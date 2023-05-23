import collections.abc

# hyper needs the four following aliases to be done manually.
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping

import tclab
import time
import os

import serial.tools.list_ports



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print(os.getlogin())
    ports = serial.tools.list_ports.comports()
    for p in ports:
        print(p.device)
    print(len(ports), 'ports found')


    with tclab.TCLab() as lab:
        print("\nStarting Temperature 1: {0:0.2f} °C".format(lab.T1), flush=True)
        print("Starting Temperature 2: {0:0.2f} °C".format(lab.T2), flush=True)

        lab.Q1(100)
        lab.Q2(100)
        print("\nSet Heater 1:", lab.Q1(), "%", flush=True)
        print("Set Heater 2:", lab.Q2(), "%", flush=True)

        t_heat = 20
        print("\nHeat for", t_heat, "seconds")
        time.sleep(t_heat)

        print("\nTurn Heaters Off")
        lab.Q1(0)
        lab.Q2(0)
        print("\nSet Heater 1:", lab.Q1(), "%", flush=True)
        print("Set Heater 2:", lab.Q2(), "%", flush=True)

        print("\nFinal Temperature 1: {0:0.2f} °C".format(lab.T1))
        print("Final Temperature 2: {0:0.2f} °C".format(lab.T2))