import datetime
import re

import dateutil.parser
from tzlocal import get_localzone

import src.tail


def common_parse_log(string):
    pattern = re.compile(r' '.join([
        r'(?P<remotehost>\S+)',
        r'(?P<rfc931>\S+)',
        r'(?P<authuser>\S+)',
        r'\[(?P<date>.*?)\]',
        r'\"(?P<request>.*?)\"',
        r'(?P<status>\S+)',
        r'(?P<bytes>\S+)',
    ]))
    match = pattern.match(string)
    return match.groupdict() if match else {
        "remotehost": "-",
        "rfc931": "-",
        "authuser": "-",
        "date": "-",
        "request": "-",
        "status": "-",
        "bytes": "-",
    }


def parse_request(string):
    pattern = re.compile(
        r'(?P<method>\S+) (?P<path>\S+) HTTP/(?P<version>\S+)')
    match = pattern.match(string)
    return match.groupdict() if match else {
        "method": "-",
        "path": "-",
        "version": "-"
    }


def common_to_rich_log(remotehost: str, rfc931: str, authuser: str, date: str,
                       request: str, status: str, bytes: str):
    x = lambda s, fn=lambda x: x: None if s == "-" else fn(s)
    req = parse_request(request)
    return {
        "remotehost": x(remotehost),
        "rfc931": x(rfc931),
        "authuser": x(authuser),
        "date": x(date, lambda _: dateutil.parser.parse(date, fuzzy=True)),
        "method": x(request, lambda _: req["method"]),
        "version": x(request, lambda _: float(req["version"])),
        "path": x(request, lambda _: req["path"]),
        "status": x(status, lambda _: int(status)),
        "bytes": x(bytes, lambda _: int(bytes)),
    }


def is_old(
    log_date: datetime.datetime,
    ref_date: datetime.datetime,
    period: int = 10,
):
    if (log_date.tzinfo and not ref_date.tzinfo):
        ref_date = ref_date.replace(tzinfo=log_date.tzinfo)
    elif (not log_date.tzinfo and ref_date.tzinfo):
        log_date = log_date.replace(tzinfo=ref_date.tzinfo)

    delta = datetime.timedelta(seconds=period)
    max_date = ref_date - delta
    return log_date < max_date


def get_logs(path='/var/log/access.log', period=10):
    logs = []
    t0 = datetime.datetime.now(get_localzone())
    with open(path, 'rb') as f:
        for line in src.tail.read(f):
            if not line: continue
            log = common_to_rich_log(**common_parse_log(line))
            if not log["date"]: continue
            if (t0 - log["date"]).seconds > period: break
            else: logs.append(log)
    return logs


def log_to_string(remotehost: str, rfc931: str, authuser: str,
                  date: datetime.datetime, method: str, version: float,
                  path: str, status: int, bytes: int):
    request = f"\"{method} {path} HTTP/{version}\""
    x = lambda y: y or '-'
    return f"{x(remotehost)} {x(rfc931)} {x(authuser)} [{x(date)}] {x(request)} {x(status)} {x(bytes)}\n"