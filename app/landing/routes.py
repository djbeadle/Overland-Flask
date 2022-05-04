from http.client import HTTPResponse
from flask import jsonify, request, render_template, Response
from app.landing import landing_bp
from db_operations import create_thing, list_all_things, record_point, get_points, count_points

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
        count=count_points(device_id='mbp2021'),
        loads=json.loads,
        gpx=False
    )

@landing_bp.route('/info4', methods=['GET'])
def info_iphone2():
    return render_template(
        'info2.html',
        points=get_points(device_id='iPhone13', mod=50, time='all'),
        count=count_points(device_id='iPhone13'),
        loads=json.loads,
        gpx=False
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
