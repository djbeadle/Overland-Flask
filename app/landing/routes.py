from http.client import HTTPResponse
from flask import jsonify, request, render_template, Response
from app.landing import landing_bp
from db_operations import create_thing, list_all_things, record_point, get_points, count_points, get_devices
import operator

import json

@landing_bp.route('/', methods=['GET'])
def home():
    text = 'This is the landing route!'
    return render_template(
        'landing.html',
        things=list_all_things(),
        content=text
    )


@landing_bp.route('/api', methods=['POST'])
def overland_api():
    d = request.json
    try:
        for loc in d['locations']:
            record_point(loc, d.get('trip'))
        return jsonify({'result': 'ok'}) 
    except Exception as e:
        print("An error occurred while parsing the locations")
        print(e)
        return jsonify({'result': 'failed'})


@landing_bp.route('/info2', methods=['GET'])
def info_iPhone():
    return render_template(
        'info2.html',
        points=get_points(device_id='iPhone13'),
        count=count_points(device_id='iPhone13'),
        loads=json.loads,
        gpx=True
    )
@landing_bp.route('/info3', methods=['GET'])
def info_mbp():
    return render_template(
        'info2.html',
        points=get_points(device_id='mbp2021'),
        info=f'{count_points(device_id="mbp2021")} points recorded for MacBook. Color coding is based on time.',
        loads=json.loads,
        gpx=False
    )

@landing_bp.route('/info4', methods=['GET'])
def info_iphone2():
    mod=20
    return render_template( 'info2.html', points=get_points(device_id='iPhone13', mod=mod, time='all'), info=f'{count_points(device_id="iPhone13")} points recorded for iPhone. Showing 1 out of every {mod} points. Large green datapoints are new, small red datapoints are old. The entire time range is shown',
        gpx=False
    )
@landing_bp.route('/info5', methods=['GET'])
def info_iphone_last_day():
    return render_template(
        'info2.html',
        info=f'{count_points(device_id="iPhone13")} points recorded for iPhone. Showing 1 in 5 points for the last two days. Color coding is based on time.',
        points=get_points(device_id='iPhone13', mod=5, time='2', filter_func=lambda x: x),
        count=count_points(device_id='iPhone13'),
        loads=json.loads,
        gpx=False
    )

def filter_property(x, prop_name, op, value):
    """
    Given an array of rows 'x' and a property name 'prop_name' contained in 'x'.
    Run 'op(x[n][prop_name], value)' return a list of values that return true
    """
    out = []
    for point in x:
        # try:
        pj = point

        if op(pj[prop_name] or 0, value):
            out += [point]
        """
        except Exception as e:
            print("Error while filtering by property")
            print(e)
            print(point)
        """
    return out
            
@landing_bp.route('/info_bat', methods=['GET'])
def info_iphone_bat():
    mod = 20
    time = 'all'
    max_battery = 50
    return render_template(
        'info2.html',
        info=f'Showing {count_points(device_id="iPhone13")} points recorded for iPhone where battery is < {max_battery}%. Showing 1 in {mod} points for the last two days. Color coding is based on time.',
        points=get_points(device_id='iPhone13', mod=mod, filter_func=lambda x: filter_property(x, 'battery_level', operator.lt, max_battery/100), time=time),
        count=count_points(device_id='iPhone13'),
        loads=json.loads,
        gpx=False
    )

@landing_bp.route('/info_speed', methods=['GET'])
def info_iphone_speed():
    op = lambda point, value: point>value #and 'driving' not in point['properties']['motion']
    mod = 10
    time = 'all'
    prop_val= 10 # mph
    prop_name = 'speed'
    # op = operator.gt
    return render_template(
        'info2.html',
        info=f'Showing {count_points(device_id="iPhone13")} points recorded for iPhone where speed is > {prop_val} mph. Showing 1 in {mod} points for the last two days. Color coding is based on time.',
        points=get_points(device_id='iPhone13', mod=mod, filter_func=lambda x: filter_property(x, prop_name, op, prop_val /  2.237), time=time),
        count=count_points(device_id='iPhone13'),
        gpx=False
    )


@landing_bp.route('/info_query', methods=['GET'])
def info_query_no_data():
    return render_template(
        "info_query.html",
        device_ids = get_devices(),
        points = [],
        count = 0
    )


@landing_bp.route('/info_query', methods=['POST'])
def info_query_with_data():
    mod = request.form.get('mod', 20)
    time = request.form.get('time', "all")
    device_id = request.form.get('device_id', "")

    filter_property_name = request.form.get('filter_by', "")
    filter_value = request.form.get('filter_value', 0)

    filter_funcs = {
        'battery_level': lambda x: filter_property(x, 'battery_level', operator.lt, int(filter_value)/100),
        # Convert Meters/second to MPH
        'speed': lambda x: filter_property(x, 'speed', operator.gt, int(filter_value)/ 2.237) 
    }
    if filter_property_name != "":
        filter_lambda = filter_funcs[filter_property_name]
    else:
        filter_lambda = lambda x: x


    # op = lambda point, value: point > value

    return render_template(
        "info_query.html",
        device_ids = get_devices(),
        points = get_points(
            device_id=device_id,
            mod=mod,time=time,
            filter_func=filter_lambda 
        )
    )


@landing_bp.route('/info', methods=['GET'])
def info():
    return render_template(
        'info.html',
        points=get_points(),
        loads=json.loads
    )


@landing_bp.route('/info', methods=['PUT'])
def update_info():
    return 'You have made a put request!'


@landing_bp.route('/create_thing', methods=['GET'])
def create_thing_route():
    create_thing("Thing!", "This is another thing", 2)
    return Response("New thing inserted in to the database.", 200)
