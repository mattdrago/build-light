#!/usr/bin/env python
import atexit
from buildlight import HudsonBuildLight

def exit_hook(light):
    light.set_usbled_color('off')

if __name__ == '__main__':
    build_light = HudsonBuildLight(host='127.0.0.1', port=8080, jobs=['job-1-here','job-2-here'])
    build_light.set_usbled_color('off')
    atexit.register(exit_hook,build_light)
    build_light.loop()

