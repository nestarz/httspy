# Technical Test

## Formulation

The program will consume an actively written-to w3c-formatted HTTP access log.

It should default to reading /var/log/access.log and be overridable.

Display stats every 10s about the traffic during those 10s:

The sections of the web site with the most hits, as well as interesting summary statistics on the
traffic as a whole.

A section is defined as being what&#39;s before the second / in the path. For example,
the section for http://my.site.com/pages/create is http://my.site.com/pages.

Make sure a user can keep the app running and monitor the log file continuously. Whenever total traffic for the past 2 minutes
exceeds a certain number on average, add a message saying that: &quot;High traffic generated an alert -
hits = {value}, triggered at {time}&quot;.

The default threshold should be 10 requests per second and should
be overridable. Whenever the total traffic drops again below that value on average for the past 2
minutes, print or displays another message detailing when the alert recovered.

## Dependencies

- Poetry
- Python ^3.8

## Install

```sh
poetry install
```

## Helper

```sh
poetry run python main.py -h

usage: main.py [-h] [--threshold THRESHOLD] [--period PERIOD] [log_file]

Monitor W3C Formatted HTTP access log.

positional arguments:
  log_file              W3C Formatted HTTP access log

optional arguments:
  -h, --help            show this help message and exit
  --threshold THRESHOLD
                        Request per seconds when to generate an alert
  --period PERIOD       Display stats every x secs
```

## Run

```sh
poetry run python main.py
```

While all information is available on the stdout, a web page will popup as a monitoring interface, be aware that the alert is only visible in the console.

## W3C Log Generator

A Log Generator is available for testing purpose under src/generator.py

```python
poetry run python src/generator.py -h
```

## Architecture Choices

Discovering is done by putting the cursor at the end of the log file and by reading backward. This allow us to process arbitrary heavy files. The reading stops when the date of one entry is out of range, then, an other read is scheldule after we finished to monitor the current context.

By using this async architecture we separate the monitoring in two pieces, one for the alert system, that needs to be highly synchronized (at a fast rate) with the current context and the analytics system which is schelduled only each 10sec.

I started the project by writing the unnitest using pytest, hint typing and tried some ways to mock the access.log fill, thus the creation of the generator.

Regarding the analystics, a fake lookup of the ip is used to target the location of the clients, a mean analysis is done for the byte length of the files and a weighted sum is done for the others fields. Also, for the alert, a state is passed after each loop to the next scheldule to notify the alert.

Also, I tried in this project to do as much as possible functional programming with the less state than possible, I would be glad to dicuss the reasons with you.

Thank you,
Elias