#!/usr/bin/env python2

from flask import Flask
from flask import render_template, Response, request, url_for, make_response, abort

import caldav
import requests as requests_native
import urllib
import os

import config
#TODO change references
from helper import *

try:
    import ConfigParser as configparser
except:
    import configparser

#TODO let SchedulerCalendar create the the client connection
#TODO permissions and user retrieval in principal class
from scheduler import SchedulerCalendar, SchedulerEvent


def requests_raise(response, *args, **kwargs):
    response.raise_for_status()


app = Flask(__name__)


@app.route('/calendar/<cal>')
def calendar(cal):
    resp = make_response(render_template('index.html', cal=cal))
    return resp


"""
cals: Comma seperated list of calendars to display
"""
@app.route('/calendars/<cals>')
def calendars(cals):
        cal_list = cals.split(',')
        cal_urls = [url_for('events', cal=cal) for cal in cal_list]
        return render_template('multisource.html', cal_urls=cal_urls)


@app.template_filter('quote')
def quote(text, quote_mark='"'):
    return quote_mark + text + quote_mark


@app.route('/events/<cal>')
def events(cal):
    dav_cal = get_system_cal(cal)
    if check_user_permission(cal, request, 'r'):
        # TODO have SchedulerCalendar handle name resolution
        sched_cal = SchedulerCalendar.fromCalendar(dav_cal)
        return Response(sched_cal.toXMLString(), mimetype='application/xml')
    else:
        abort(403)


# modify single events
@app.route('/event/<cal>', methods=['POST'])
def event(cal):
    if not check_user_permission(cal, request, 'w'):
        abort(403)

    start = request.form['start_date']
    end = request.form['end_date']
    text = request.form['text']
    id = request.form['id']
    tid = id

# TODO check if id/ref belongs to calendars, otherwise security hole!
    #url_cal = url.path.split('/')[1].rstrip('.ics')
    #url = urlparse.urlparse(id)
    dav_cal = get_system_cal(cal)

    mode = request.form['!nativeeditor_status']

    # TODO views for update and delete, with different status codes
    if mode == 'updated':
        ev = SchedulerEvent.fromRequest(id, start, end, text)
        ev.update(dav_cal)
        return Response(
            SchedulerEvent.XmlResponse(mode, id, tid),
            status=200,
            mimetype='application/xml')
    elif mode == 'inserted':
        ev = SchedulerEvent.fromRequest(id, start, end, text)
        ev.create(dav_cal)
        # use original id only in reponse
        tid = ev.id
        return Response(
            SchedulerEvent.XmlResponse(mode, id, tid),
            status=201,
            mimetype='application/xml')
    elif mode == 'deleted':
        ev = SchedulerEvent.fromRequest(id, start, end, text)
        ev.delete(dav_cal)
        return Response(
            SchedulerEvent.XmlResponse(mode, id, tid),
            status=200,
            mimetype='application/xml')


if __name__ == '__main__':
    app.debug = True
    requests = requests_native.Session()
    requests.hooks = {"response": requests_raise}
    conf = config.get_config()
    app.run()
