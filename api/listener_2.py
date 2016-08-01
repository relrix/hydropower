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

from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__, static_url_path="")
api = Api(app)

events = [
    {
        'event_id': 1,
        'presenter_id': 101,
        'stream_url': u'some FMS server Url1',
        'mainwindow': False
    },
    {
        'event_id': 2,
        'presenter_id': 102,
        'stream_url': u'some FMS server Url2',
        'mainwindow': True
    }
]

event_fields = {
    'event_id': fields.Integer,
    'presenter_id': fields.Integer,
    'stream_url': fields.String,
    'mainwindow': fields.Boolean,
    # 'uri': fields.Url('events')
}


class EventListAPI(Resource):
    """Events api."""

    def __init__(self):
        """init."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('event_id', type=int, required=True, help='No event event id provided', location='json')
        self.reqparse.add_argument('presenter_id', type=int, required=True, help='No event presenter id provided', location='json')
        self.reqparse.add_argument('stream_url', type=str, required=True, help='No stream url provided', location='json')

        super(EventListAPI, self).__init__()

    def get(self):
        """get."""
        return {'events': [marshal(event, event_fields) for event in events]}

    def post(self):
        args = self.reqparse.parse_args()

        event = {
            'event_id': args['event_id'],
            'presenter_id': args['presenter_id'],
            'stream_url': args['stream_url'],
            'mainwindow': False
        }
        events.append(event)
        return {'event': marshal(event, event_fields)}, 201


class EventAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('event_id', type=int, location='json')
        self.reqparse.add_argument('presenter_id', type=int, location='json')
        self.reqparse.add_argument('stream_url', type=str, location='json')
        self.reqparse.add_argument('mainwindow', type=bool, location='json')
        super(EventAPI, self).__init__()

    def get(self, id):
        event = [event for event in events if event['event_id'] == id]
        if len(event) == 0:
            abort(404)
        return {'event': marshal(event[0], event_fields)}

    def put(self, id):
        event = [event for event in events if event['event_id'] == id]
        if len(event) == 0:
            abort(404)
        event = event[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                event[k] = v
        return {'event': marshal(event, event_fields)}

    def delete(self, id):
        event = [event for event in events if event['event_id'] == id]
        if len(event) == 0:
            abort(404)
        events.remove(event[0])
        return {'result': True}


api.add_resource(EventListAPI, '/webcam/api/v1.0/events', endpoint='events')
api.add_resource(EventAPI, '/webcam/api/v1.0/event/<int:id>', endpoint='event')

if __name__ == '__main__':
    app.run(debug=True, host='10.4.0.80', port=80)
