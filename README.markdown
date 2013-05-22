
## Linux/MacOS Hudson build light script for USB Led devices (eg. Delcom USB Visual Signal Indicator)

This script polls a hudson instance and drives an USB led device to act as a "build light".

It works out of the box for Linux. For MacOS libusb 1.x must be installed:

    sudo brew install libusb

To configure the script for your hudson instance, change the following line in run.py:

    build_light = HudsonBuildLight(host='127.0.0.1', port=8080, job='your-job-here')

Or, if you have multiple lights attached and you know the address of the one to control.  Not specifying an address will result in teh first one found being used.

    build_light = HudsonBuildLight(host='127.0.0.1', port=8080, job='your-job-here', ledAddress=21)

This script has been tested on generation 1 and 2 Delcom USB Visual Signal Indicator (in particular 804028 and 904005-SB)

To be able to run this script as a non-root user, setup a udev rule for Delcom devices.  Make sure to re-attach the devices after copying the rules file.

    sudo cp 70-delcom.rules /etc/udev/rules.d/ 

Bundled PyUSB is 1.0.0a3

References for libusb code: 

 * http://www.linuxjournal.com/article/7466?page=0,1
 * http://pyusb.sourceforge.net/docs/1.0/tutorial.html
