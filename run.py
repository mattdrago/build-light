#!/usr/bin/env python
from buildlight import HudsonBuildLight

if __name__ == '__main__':
    build_light = HudsonBuildLight(host='127.0.0.1', port=8080, jobs=['job-1-here','job-2-here'])
    build_light.loop()

