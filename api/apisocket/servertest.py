#!/usr/bin/python

import on24server as socklisten

import sys

socklisten.socket_start_listener(str(sys.argv[1]))


