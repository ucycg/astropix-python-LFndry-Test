# astropix-python-LFndry-Test

Python based lightweight cross-platform tool to control the GECCO System, based on [ATLASPix3_SoftAndFirmware](https://git.scc.kit.edu/jl1038/atlaspix3)

To interact with the FTDI-Chip the ftd2xx package is used, which provides a wrapper around the proprietary D2XX driver.
The free pyftdi driver currently does not support the synchronous 245 FIFO mode.  
For bit manipulation the bitstring package is used.

Features:
* Write ASIC config (SR and SPI)
* Configure Voltageboards (+offset cal)
* Configure Injectionboard
* Read/Write single registers
* SPI/QSPI Readout
* Import/export chip config from/to yaml

Work in progress:
* GUI
* Scans

## Installation

Requirements:
* Python >= 3.9
* packages: ftd2xx, async-timeout, bitstring 
* D2XX Driver

```shell
$ git clone git@github.com:nic-str/astropix-python.git
$ cd astropix-python

# Create venv
$ python3 -m venv astropix-venv
$ source astropix-venv/bin/activate

# Install Requirements
$ pip install -r requirements.txt
```

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

### Mac
See [FTDI Mac OS X Installation Guide](https://www.ftdichip.com/Support/Documents/InstallGuides/Mac_OS_X_Installation_Guide.pdf) D2XX Driver section from page 10.

## Example Usage

### Upload the Firmware to FPGA Board
