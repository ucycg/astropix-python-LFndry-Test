# astropix-python

Python based lightweight cross-platform tool for controlling the GECCO System.

To interact with the FTDI-Chip the ftd2xx package is used, which provides a wrapper around the proprietary D2XX driver.
For Bitmanipulation the bitstring package is used.

Features:
* Write asicSR
* Configure Voltageboards (+calibration)
* Configure Injectionboard
* Read/Write to single registers

TODO:
* SPI

## Installation

Requirements:
* Python >= 3.6
* packages: ftd2xx, bitstring
* D2XX Driver

Create venv:
    
    python3 -m venv astropix-python
    source astropix-python/bin/activate 

Install requirements:

    pip install -r requirements.txt

### Windows

D2XX Driver should be pre-installed.

### Linux

Install D2XX driver: [Installation Guide](https://ftdichip.com/wp-content/uploads/2020/08/AN_220_FTDI_Drivers_Installation_Guide_for_Linux-1.pdf)

Check if VCP driver gets loaded:
    
    sudo lsmod | grep -a "ftdi_sio"

If yes, create a file in /etc/udev/rules.d/ with the following content to unbid the VCP driver and make the device accessible for non-root users:

    ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010",\
    PROGRAM="/bin/sh -c '\
        echo -n $id:1.0 > /sys/bus/usb/drivers/ftdi_sio/unbind;\
        echo -n $id:1.1 > /sys/bus/usb/drivers/ftdi_sio/unbind\
    '"

    ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010",\
    MODE="0666"

Reload rules with:

    sudo udevadm trigger

Create links to shared lib:

    sudo ldconfig
