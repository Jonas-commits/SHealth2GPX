import argparse
import json
import pandas
import os
from datetime import datetime
from gooey import Gooey, GooeyParser

import pandas as pd

EXERCISE_TYPES = {  # https://developer.samsung.com/health/android/data/api-reference/EXERCISE_TYPE.html
    0: 'Custom type',
    1001: 'Walking',
    1002: 'Running',
    2001: 'Baseball, general',
    2002: 'Softball, general',
    2003: 'Cricket',
    3001: 'Golf, general',
    3002: 'Billiards',
    3003: 'Bowling, alley',
    4001: 'Hockey',
    4002: 'Rugby, touch, non-competitive',
    4003: 'Basketball, general',
    4004: 'Football, general (Soccer)',
    4005: 'Handball, general',
    4006: 'American football, general, touch',
    5001: 'Volleyball, general',
    5002: 'Beach volleyball',
    6001: 'Squash, general',
    6002: 'Tennis, general',
    6003: 'Badminton, competitive',
    6004: 'Table tennis',
    6005: 'Racquetball, general',
    7001: 'Thai chi, general',
    7002: 'Boxing, in ring',
    7003: 'Martial arts, moderate pace (Judo, Jujitsu, Karate, Taekwondo)',
    8001: 'Ballet, general, rehearsal or class',
    8002: 'Dancing, general (Fork, Irish step, Polka)',
    8003: 'Ballroom dancing, fast',
    9001: 'Pilates',
    9002: 'Yoga',
    10001: 'Stretching',
    10002: 'Jump rope, moderate pace, 2 foot skip',
    10003: 'Hula-hooping',
    10004: 'Push-ups (Press-ups)',
    10005: 'Pull-ups (Chin-up)',
    10006: 'Sit-ups',
    10007: 'Circuit training, moderate effort',
    10008: 'Mountain climbers',
    10009: 'Jumping Jacks',
    10010: 'Burpee',
    10011: 'Bench press',
    10012: 'Squats',
    10013: 'Lunges',
    10014: 'Leg presses',
    10015: 'Leg extensions',
    10016: 'Leg curls',
    10017: 'Back extensions',
    10018: 'Lat pull-downs',
    10019: 'Deadlifts',
    10020: 'Shoulder presses',
    10021: 'Front raises',
    10022: 'Lateral raises',
    10023: 'Crunches',
    10024: 'Leg raises',
    10025: 'Plank',
    10026: 'Arm curls',
    10027: 'Arm extensions',
    11001: 'Inline skating, moderate pace',
    11002: 'Hang gliding',
    11003: 'Pistol shooting',
    11004: 'Archery, non-hunting',
    11005: 'Horseback riding, general',
    11007: 'Cycling',
    11008: 'Flying disc, general, playing',
    11009: 'Roller skating',
    12001: 'Aerobics, general',
    13001: 'Hiking',
    13002: 'Rock climbing, low to moderate difficulty',
    13003: 'Backpacking',
    13004: 'Mountain biking, general',
    13005: 'Orienteering',
    14001: 'Swimming, general, leisurely, not lap swimming',
    14002: 'Aquarobics',
    14003: 'Canoeing, general, for pleasure',
    14004: 'Sailing, leisure, ocean sailing',
    14005: 'Scuba diving, general',
    14006: 'Snorkeling',
    14007: 'Kayaking, moderate effort',
    14008: 'Kitesurfing',
    14009: 'Rafting',
    14010: 'Rowing machine, general, for pleasure',
    14011: 'Windsurfing, general',
    14012: 'Yachting, leisure',
    14013: 'Water skiing',
    15001: 'Step machine',
    15002: 'Weight machine',
    15003: 'Exercise bike, Moderate to vigorous effort (90-100 watts)',
    15004: 'Rowing machine',
    15005: 'Treadmill, combination of jogging and walking',
    15006: 'Elliptical trainer, moderate effort',
    16001: 'Cross-country skiing, general, moderate speed',
    16002: 'Skiing, general, downhill, moderate effort',
    16003: 'Ice dancing',
    16004: 'Ice skating, general',
    16006: 'Ice hockey, general',
    16007: 'Snowboarding, general, moderate effort',
    16008: 'Alpine skiing, general, moderate effort',
    16009: 'Snowshoeing, moderate effort'
}


def create_gpx_file(filename, gpx_name):
    with open(filename, 'w') as f:
        f.write("""<?xml version='1.0' encoding='UTF-8'?>
<gpx version="1.1" creator="SHealth2GPX" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>{}</name>
  </metadata>
  <trk>
    <name>{}</name>
    <trkseg>
""".format(gpx_name, gpx_name))


def finish_gpx_file(filename):
    with open(filename, 'a') as f:
        f.write("""    </trkseg>
  </trk>
</gpx>""")


def insert_trackpoints(filename, lst):
    with open(filename, 'a') as f:
        for l in lst:
            lat = l[0]
            lon = l[1]
            timestamp = l[2]
            iso_time = datetime.fromtimestamp(timestamp / 1000).isoformat()
            f.write("<trkpt lat=\"{}\" lon=\"{}\"><time>{}</time></trkpt>\n".format(lat, lon, iso_time))


def parse_shealth_json(filename):
    trkpts = []

    with open(filename, 'r') as f:
        json_data = json.load(f)

        for list_item in json_data:
            trkpts.append((list_item['latitude'], list_item['longitude'], list_item['start_time']))

    return trkpts


def convert_file(in_filename, out_filename):
    create_gpx_file(out_filename, os.path.basename(in_filename))
    trkpts = parse_shealth_json(in_filename)
    if len(trkpts) != 0:
        insert_trackpoints(out_filename, trkpts)
        finish_gpx_file(out_filename)
    else:
        os.remove(out_filename)


def create_file_index(folder):
    index = {}
    for root, dirs, files in os.walk(folder):
        for filename in files:
            index[filename] = os.path.join(root, filename)
    return index


def create_gpx_files(export_dir):
    files = os.listdir(export_dir)
    if 'jsons' not in files:
        raise Exception('Could not find a json folder in directory => assure you set the right directory')

    exercise_csv = ""
    for file in files:
        if file.startswith('com.samsung.shealth.exercise.2'):
            exercise_csv = file
            break
    else:
        raise Exception('Could not find exercise csv in root folder => assure you set the right directory')

    exercise_path = os.path.join(export_dir, 'jsons', 'com.samsung.shealth.exercise')
    if not os.path.exists(exercise_path):
        raise Exception('Could not find ' + exercise_path)

    exercise_files = create_file_index(exercise_path)
    df = pandas.read_csv(os.path.join(export_dir, exercise_csv), sep=',', header=1, index_col=False)
    for index, row in df.iterrows():
        if not pd.isna(row['com.samsung.health.exercise.location_data']):
            try:
                print(exercise_files[row['com.samsung.health.exercise.location_data']])
                timestamp = row['com.samsung.health.exercise.start_time'].replace(':', '_')
                target_dir = os.path.join(export_dir, 'SHealth2GPX',
                                          str(EXERCISE_TYPES[row['com.samsung.health.exercise.exercise_type']]))
                target_file = os.path.join(target_dir, timestamp + '.gpx')
                os.makedirs(target_dir, exist_ok=True)
                convert_file(exercise_files[row['com.samsung.health.exercise.location_data']], target_file)
            except KeyError:
                pass


if __name__ == '__main__':
    @Gooey
    def main():
        parser = GooeyParser(
            prog="SHealth2GPX Converter",
            description="Converts Samsung Health extract to GPX Files\n"
                        "This Program is a private script and not related in any kind to Samsung or SHealth")
        parser.add_argument('export_dir', help='export path from Samsung files', widget="DirChooser")
        args = parser.parse_args()

        create_gpx_files(args.export_dir)
    main()
