#!/usr/bin/python
"""API listener.

Copyright (C) 2016 - Shishir Pokharel
shishir.pokharel@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from flask import Flask, jsonify
from flask import abort, make_response
from flask import request
import urlparse

import db.apidb as dbconnector
import apisocket.on24client as On24appsocket
import apisocket.on24socketclient as On24procsocket
import json
import time

app = Flask(__name__)
server = '127.0.0.1'


@app.route('/webcam/api/v1.0/events', methods=['GET'])
def get_events():
    """list processing events."""
    return On24Response('success', 'you will have list of on going events here')


@app.route('/webcam/api/v1.0/event/<int:eventid>', methods=['POST'])
def get_event(eventid):
    """list detail about single event."""
    response = "None"
    params = "None"
    port = dbconnector.access_db(eventid)
    if port is None or port is 0:
        #params = dict(urlparse.parse_qsl(request.data))
        params = request.form
        if "rtmpurldst" not in params:
            status = dbconnector.del_record(eventid)
            return On24Response('failed', "publish RTMP url missing.")

        elif "action" not in params:
            status = dbconnector.del_record(eventid)
            return On24Response('failed', "action not found.")

        elif "presenter_id" not in params:
            status = dbconnector.del_record(eventid)
            return On24Response('failed', "presenter_id is missing.")

        elif "rtmpurl" not in params:
            status = dbconnector.del_record(eventid)
            return On24Response('failed', "presenter RTMP url missing.")

        response = On24Socketstart(eventid, params['rtmpurldst'], port)

       # return jsonify (response)

    else:
        params = request.form

        if "action" not in params:
            return On24Response('failed', "action not found.")

        elif "presenter_id" not in params:
            return On24Response('failed', "presenter_id is missing.")

        elif "rtmpurl" not in params:
            return On24Response('failed', "persenter RTMP url is missing.")

        else:

            return On24Socketadd(params['presenter_id'], params['rtmpurl'], False, port)


    if response['status'] == "success":
        time.sleep(2)
        port = dbconnector.access_db(eventid)
        print " I have port ", port
        print params['presenter_id'], params['rtmpurl']
        if port is not None or port is not 0:
            return On24Socketadd(params['presenter_id'], params['rtmpurl'], True, port)


@app.route('/webcam/api/v1.0/event/<int:eventid>/switch', methods=['POST'])
def switch_user(eventid):
    """list detail about single event."""
    port = dbconnector.access_db(eventid)
    if port is None or port is 0:
        return On24Response('failed', str(eventid) + " event not found.")
    else:
        params = request.form

        if "action" not in params:
            return On24Response('failed', "action not found.")

        elif "presenter_id" not in params:
            return On24Response( 'failed', "On24Response")

        else:
            return On24Socketswitch(params['presenter_id'], port)


@app.errorhandler(404)
def notfound_error(error):
    """create custome 404 error."""
    return make_response(jsonify({'error': 'stop messing with invalid data'}), 400)


def On24Socketstart(eventid, rtmpurldst, port):
    message = json.dumps({'eventid': str(eventid), 'action': 'startProcess', 'rtmpurldst': rtmpurldst, 'on24data': 'ON24EOS'}, separators=(',', ':'))
    return On24procsocket.client_start_process(server, message)

def On24Socketadd(presenter_id, rtmpurl, ismain, port):

    message = json.dumps({'action': 'add_presenter', 'presenter_id': presenter_id, 'ismain': ismain, 'rtmpurl': rtmpurl, 'on24data': 'ON24EOS'}, separators=(',', ':'))
    return jsonify(On24appsocket.socket_get_dict_response(port, message))

def On24Socketswitch(presenter_id, port):
    message = json.dumps({'action': 'switch_presenter', 'presenter_id': presenter_id, 'on24data': 'ON24EOS'}, separators=(',', ':'))
    return jsonify(On24appsocket.socket_get_dict_response(port, message))

def On24Response(status, message):
    return jsonify({'status': status, 'message': message})

if __name__ == '__main__':
    app.run(debug=True, host='10.4.0.80', port=80)
