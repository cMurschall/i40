# i40

To be able to mount the serial port into the docker container we need to add a udev rule:

```
KERNEL=="ttyUSB[0-9]*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001",  MODE="0666"
KERNEL=="ttyACM[0-9]*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001",  MODE="0666"
```