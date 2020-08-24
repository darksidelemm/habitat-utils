# Habitat Utils
Various tools for working with data from Habitat

## Dependencies
* Python 3

## Telemetry Distance Records
Calculates the maximum distance each listener on a flight received telemetry.

Download receivers list (this needs to be done just after the flight):
```console
$ wget -O receivers.json https://legacy-snus.habhub.org/tracker/receivers.php
```

Download export of payload log from http://habitat.habhub.org/ept/ in JSON format.

Run the script:
```console
$ python telemetrydistance yourtelemetrylog.json
```