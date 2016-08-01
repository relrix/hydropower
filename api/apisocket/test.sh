#1/usr/bin/bash

args=("$@")
path="/usr/local/gst/webcam/hydropower/api/apisocket"
`${path}/servertest.py ${args[0]} &`
exit 0
