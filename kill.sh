#!/bin/bash
 ps aux | grep hydropower.py | awk '{ print $2}' |xargs -I{} kill -10 {}
