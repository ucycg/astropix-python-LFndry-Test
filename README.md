# astropix-python

Python based lightweight cross-platform tool for controlling the GECCO System.

To interact with the FTDI-Chip the ftd2xx package is used, which provides a wrapper around the proprietary D2XX driver.
The free pyftdi driver currently does not support the synchronous 245 FIFO mode.  
For bit manipulation the bitstring package is used.

Features:
* Write ASIC (SR)
* Configure Voltageboards (+calibration)
* Configure Injectionboard
* Read/Write to single registers

TODO:
* Write ASIC (SPI)
* SPI Readout

## Installation

Requirements:
* Python 3.9
* packages: ftd2xx, bitstring
* D2XX Driver


    git clone git@github.com:nic-str/astropix-python.git
    cd astropix-python

    # Create venv
    python3 -m venv astropix-venv
    source astropix-venv/bin/activate

    # Install Requirements
    pip install -r requirements.txt

### Windows

D2XX Driver should be pre-installed.

### Linux

Install D2XX driver: [Installation Guide](https://ftdichip.com/wp-content/uploads/2020/08/AN_220_FTDI_Drivers_Installation_Guide_for_Linux-1.pdf)

Check if VCP driver gets loaded:
    
    sudo lsmod | grep -a "ftdi_sio"

If yes, create a rule e.g., 99-ftdi-nexys.rules in /etc/udev/rules.d/ with the following content to unbid the VCP driver and make the device accessible for non-root users:

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
