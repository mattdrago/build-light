
## Linux/MacOS Hudson build light script for USB Led devices (eg. Delcom USB Visual Signal Indicator)

This script polls a hudson instance and drives an USB led device to act as a "build light".

It works out of the box for Linux. For MacOS libusb 1.x must be installed:

    sudo brew install libusb

To configure the script for your hudson instance, change the following line in run.py:

    build_light = HudsonBuildLight(host='127.0.0.1', port=8080, job='your-job-here')

This script has been tested only on a generation 1 Delcom USB Visual Signal Indicator (804005)

To be able to run this script as a non-root user, setup a udev rule for Delcom devices.  Make sure to re-attach the devices after copying the rules file.

    sudo cp 70-delcom.rules /etc/udev/rules.d/ 

Bundled PyUSB is 1.0.0-a0

References for libusb code: 

 * http://www.linuxjournal.com/article/7466?page=0,1
 * http://pyusb.sourceforge.net/docs/1.0/tutorial.html
