# Aufgabe node-red, telegraf und influx db

[Lösungen der Aufgaben](report.md)


Da mir die VM zu und zu unflexibel ist habe ich den Stack mit Docker aufgesetzt. Die Meßdaten aus dem TCLab sollten in die influxdb geschriben werden und folgenden Weg gehen:


TCLab => node-red => MQTT => telegraf => influxdb


Das TCLab stellt einen seriellen Port zur Verfügung um die Daten auszulesen. Unter linux müssen erstmal die Rechte freigegeben werden. Damit das gelingt, müssen wir eine udev rule anlegen:

```
KERNEL=="ttyUSB[0-9]*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001",  MODE="0666"
KERNEL=="ttyACM[0-9]*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001",  MODE="0666"
```

Damit haben wir den seriellen Port für alle freigegeben. Da unter Linux jedes Gerät eine Datei ist, sollte es eigentlich möglich sein, diese in den container zu mounten. Dies ist leider nicht gelungen. Als abhilfe können wir den port aber als device übergeben. In der [docker-compose datei](docker-compose.yml#L68) ist das diese Zeile:
```
devices:
    - "/dev/ttyACM0:/dev/ttyACM0"
```


Mit diesem Eintrag können wir einen node red flow aufsetzen, der periodisch die Temperatursensoren und die Solltemperatur des Reglers abfragt

![](images/node_red_flow.png)


Der Code im `Set Query` node sieht so aus:
```js
const messages = [
    "T1",
    "T2",
    "R1",
    "R2",
]

let index = flow.get("count") % messages.length

msg.payload = messages[index]
return msg;
``` 

Der komplette Flow ist [hier](node-red_flow.json)  abgelegt.



