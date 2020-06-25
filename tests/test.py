import datetime
from tzlocal import get_localzone

import src.tail
import src.monitor
import src.parser
from src.generator import generate_w3c_log

def test_common_parse_log():
    assert src.parser.common_parse_log(
        src.parser.log_to_string(**generate_w3c_log())) == {
            "remotehost": "127.0.0.1",
            "rfc931": "-",
            "authuser": "-",
            "date": "1970-01-01 00:00:00",
            "request": "GET / HTTP/2.0",
            "status": "200",
            "bytes": "380",
        }


def test_common_to_rich_log():
    log = generate_w3c_log()
    common_log = src.parser.common_parse_log(src.parser.log_to_string(**log))
    assert src.parser.common_to_rich_log(**common_log) == log


def test_is_old():
    period = 10
    t0 = datetime.datetime(1970, 1, 1, tzinfo=get_localzone())
    old = generate_w3c_log(date=t0 - datetime.timedelta(seconds=period + 1))
    recent = generate_w3c_log(date=t0 - datetime.timedelta(seconds=period - 2))
    assert src.parser.is_old(old["date"], t0, period) == True
    assert src.parser.is_old(recent["date"], t0, period) == False


def test_stream_log():
    log_path = "/tmp/blade_access.log"
    with open(log_path, "w") as f:
        for log in [
                '127.0.0.1 - - [24/Jun/2020 04:16:23] "GET / HTTP/1.1" 200 -',
                '127.0.0.1 - - [24/Jun/2020 04:16:25] "GET /pages HTTP/1.1" 200 -',
                '127.0.0.1 - - [24/Jun/2020 04:16:27] "GET /pages/create HTTP/1.1" 200 -',
                '127.0.0.1 - - [24/Jun/2020 04:16:30] "GET /admin HTTP/1.1" 200 -',
                '167.96.134.91 - - [24/Jun/2020:07:04:35 +0200] "DELETE /app/main/posts HTTP/1.0" 200 5009 "http://hensley.com/category.jsp" "Mozilla/5.0 (Macintosh; PPC Mac OS X 10_12_0; rv:1.9.3.20) Gecko/2010-02-19 10:12:37 Firefox/3.8"'
        ]:
            f.write(log + "\n")
    assert len(src.parser.get_logs(path=log_path, period=10000000)) > 0


def test_section_stat():
    logs = [
        src.parser.common_to_rich_log(**src.parser.common_parse_log(string))
        for string in [
            '127.0.0.1 - - [24/Jun/2020 04:16:23] "GET / HTTP/1.1" 200 -',
            '127.0.0.1 - - [24/Jun/2020 04:16:25] "GET /pages HTTP/1.1" 200 -',
            '127.0.0.1 - - [24/Jun/2020 04:16:27] "GET /pages/create HTTP/1.1" 200 -',
            '127.0.0.1 - - [24/Jun/2020 04:16:30] "GET /admin HTTP/1.1" 200 -',
            '167.96.134.91 - - [24/Jun/2020:07:04:35 +0200] "DELETE /app/main/posts HTTP/1.0" 200 5009 "http://hensley.com/category.jsp" "Mozilla/5.0 (Macintosh; PPC Mac OS X 10_12_0; rv:1.9.3.20) Gecko/2010-02-19 10:12:37 Firefox/3.8"'
        ]
    ]
    assert src.monitor.count_sections(logs) == {
        "": 1,
        "pages": 2,
        "admin": 1,
        "app": 1
    }


def test_alert_high_trafic():
    assert src.monitor.check_high_trafic([
        src.parser.common_to_rich_log(**src.parser.common_parse_log(
            '127.0.0.1 - - [24/Jun/2020 04:16:23] "GET / HTTP/1.1" 200 -'))
        for _ in range(0, 10000)
    ]) == True

    assert src.monitor.check_high_trafic([
        src.parser.common_to_rich_log(**src.parser.common_parse_log(
            '127.0.0.1 - - [24/Jun/2020 04:16:23] "GET / HTTP/1.1" 200 -'))
        for _ in range(0, 10)
    ]) == False
