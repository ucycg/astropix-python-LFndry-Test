# astropix-python

Python based lightweight cross platform tool for controlling the GECCO System.

To interact with the FTDI-Chip the ftd2xx package is used, which provides a wrapper around the D2XX driver.
For Bitmanipulation the Bitstring package is used.

Features:
* Write asicSR
* Configure Voltageboards
* Read/Write to single registers

TODO:
* Injectionboard
* SPI

### Linux
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
