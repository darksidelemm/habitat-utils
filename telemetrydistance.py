#!/usr/bin/env python
#
#   Calculate telemetry distance records for a HAB flight.
#
import argparse
import json
import logging
import sys
from earthmaths import position_info




def read_receivers(filename="receivers.json"):
    """ Read in a Receivers JSON file, and convert to a callsign-indexed dictionary """

    _f = open(filename, 'r')
    _data = _f.read()
    _f.close()

    _json = json.loads(_data)

    output = {}
    for _rxer in _json:
        output[_rxer['name']] = _rxer

    return output


def read_telemetry(filename):
    """ Read in a telemetry file """
    _f = open(filename, 'r')
    _data = _f.read()
    _f.close()

    return json.loads(_data)


def calculate_distances(rxers, telem):
    """ Calculate the maximum distance received by each receiver in a telemetry file"""

    _rx_records = {}

    for _line in telem:

        # Payload Position
        _lat = _line['latitude']
        _lon = _line['longitude']
        _alt = _line['altitude']

        # List of receivers
        _rx_list = _line['_receivers']

        for _rx in _rx_list:
            if _rx not in rxers:
                # Don't know this receiver.
                continue
            
            # Grab receiver info
            _rx_lat = rxers[_rx]['lat']
            _rx_lon = rxers[_rx]['lon']
            _rx_alt = rxers[_rx]['alt']

            # Calculate distance
            _pos_info = position_info((_rx_lat, _rx_lon, _rx_alt), (_lat ,_lon, _alt))
            _distance = _pos_info['straight_distance']

            if _rx not in _rx_records:
                # Initialise entry.
                _rx_records[_rx] = {'distance': 0, 'pos_info': {}, 'rx_info': rxers[_rx]}
            
            if _distance > _rx_records[_rx]['distance']:
                _rx_records[_rx]['distance'] = _distance
                _rx_records[_rx]['pos_info'] = _pos_info
        

    return _rx_records





def main():
    # Read command-line arguments
    parser = argparse.ArgumentParser(description="Telemetry Distance Records", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("telemetry", help="JSON Telemetry Export")
    parser.add_argument("--receivers", default="receivers.json", help="Receiver JSON file. (Default: receivers.json)")
    parser.add_argument("--ntop", default=10, help="Print Top N distance records")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Verbose output (set logging level to DEBUG)")
    args = parser.parse_args()

    if args.verbose:
        _log_level = logging.DEBUG
    else:
        _log_level = logging.INFO

    # Setup Logging
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s", level=_log_level
    )


    receivers = read_receivers(args.receivers)

    telem = read_telemetry(args.telemetry)

    _records = calculate_distances(receivers, telem)

    _distances = {}

    # Print out individual records for all listeners.
    for _call in _records:
        _distance = _records[_call]['distance']/1000
        _balloon_alt = _records[_call]['pos_info']['balloon'][2]
        _elevation = _records[_call]['pos_info']['elevation']
        _bearing = _records[_call]['pos_info']['bearing']
        print(f"{_call}: {_distance:.1f} km (Payload Alt: {_balloon_alt:.1f} m, Elevation:{_elevation:.1f}˚, Bearing: {_bearing:.1f}˚)")

        _distances[_distance] = {'call': _call, 'data':_records[_call]}

    # Top N distances.
    print("\n\nDistance Records")
    _distance_keys = list(_distances.keys())
    _distance_keys.sort()

    _i = 1
    while _i <= args.ntop:
        _dist = _distance_keys[-1*_i]
        
        _call = _distances[_dist]['call']
        _balloon_alt = _distances[_dist]['data']['pos_info']['balloon'][2]
        _elevation = _distances[_dist]['data']['pos_info']['elevation']
        _bearing = _distances[_dist]['data']['pos_info']['bearing']

        print(f"#{_i}: {_dist:.1f} km by {_call} (Payload Alt: {_balloon_alt:.1f} m, Elevation:{_elevation:.1f}˚, Bearing: {_bearing:.1f}˚)")

        _i += 1



if __name__ == "__main__":
    main()