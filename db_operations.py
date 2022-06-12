import sqlite3, json
from flask import g, current_app

def get_db():
    """
    Singleton for database connection
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DB_NAME'])
        db.row_factory = sqlite3.Row
    return db


# SELECT JSON_EXTRACT(data, '$.properties.altitude') FROM datapoints ORDER BY rowid DESC LIMIT 1;
def record_point(point, trip):
    db = get_db()
    cur = db.cursor()
    # print(json.dumps(point))
    try:
        cur.execute(
            "INSERT INTO datapoints (device_id, timestamp, data, trip) VALUES (?, ?, ?, ?);",
            [point['properties']['device_id'], point['properties']['timestamp'], json.dumps(point), trip ]
        )
        db.commit()
    except Exception as e:
        print("Unable to store this data point:")
        print(e)
        raise e

def get_points(device_id='iPhone13', filter_func=None, limit=2000, mod=20, time='all'):
    db = get_db()
    cur = db.cursor()

    query = "SELECT data FROM datapoints WHERE device_id = ? AND rowid % ? = 0 "
    if time.lower() == 'all':
        pass
    else:
        query += f' AND date(timestamp) >= date(\'now\', \'-{time} day\');'

    cur.execute(
        # "SELECT data FROM datapoints WHERE device_id = ? AND rowid % 20 = 0 ORDER BY timestamp DESC LIMIT ?;",
        query,
        [ device_id, mod ]
    ) 
    
    if filter_func:
        return filter_func(cur.fetchall())

    return cur.fetchall()

def count_points(device_id='iPhone13'):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT count(data) FROM datapoints WHERE device_id = ?;",
       [device_id]
    )
    return cur.fetchone()[0]

def create_thing(thing, description, status):
    db = get_db()
    cur = db.cursor()
  
    try:
        cur.execute(
            "INSERT INTO things(title, description, status) VALUES (?, ?, ?);",
            [thing, description, status]
        )
        rows = cur.fetchall()
        db.commit()
        return rows

    except Exception as e:
        print("An error occurred fetching all of the things.")
        print(e)


def list_all_things():
    db = get_db()
    cur = db.cursor()
  
    try:
        cur.execute("""
            SELECT id, title, description, status
            FROM things;
        """)
        rows = cur.fetchall()
        db.commit()
        db.close()
        return rows

    except Exception as e:
        print("An error occurred fetching all of the things.")
        print(e)
