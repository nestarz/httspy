#!/usr/bin/python
import time
import datetime
import random
import sys
import argparse
import http

from faker import Faker
from tzlocal import get_localzone


def generate_w3c_log(
    remotehost="127.0.0.1",
    rfc931=None,
    authuser=None,
    date=datetime.datetime(1970, 1, 1),
    method="GET",
    version=2.0,
    path="/",
    status=http.HTTPStatus.OK,
    byteslength=380,
):
    return {
        "remotehost": remotehost,
        "rfc931": rfc931,
        "authuser": authuser,
        "date": date,
        "method": method,
        "version": version,
        "path": path,
        "status": status,
        "bytes": byteslength,
    }


weighted_choice = lambda s, p: random.choice(
    sum(([v] * int(wt * 100) for v, wt in zip(s, p)), []))


def main(output_path, log_lines, output_type, sleep):
    faker = Faker()
    otime = datetime.datetime.now()

    status = ["200", "404", "500", "301"]
    methods = ["GET", "POST", "DELETE", "PUT"]
    resources = [
        "/list", "/wp-content", "/wp-admin", "/explore", "/search/tag/list",
        "/app/main/posts", "/posts/posts/explore", "/apps/cart.jsp?appID="
    ]

    local = get_localzone()
    batch_size = 6
    for __ in range(0, log_lines, batch_size):
        batch = []
        for _ in range(batch_size):
            otime += datetime.timedelta(seconds=sleep / batch_size)
            dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
            tz = datetime.datetime.now(local).strftime('%z')
            method = weighted_choice(methods, p=[0.6, 0.1, 0.1, 0.2])

            uri = random.choice(resources)
            if uri.find("apps") > 0:
                uri += str(random.randint(1000, 10000))

            log = generate_w3c_log(remotehost=faker.ipv4(),
                                   date=f"{dt} {tz}",
                                   method=method,
                                   version=weighted_choice([1.0, 1.1, 2.0], p=[0.2, 0.3, 0.5]),
                                   path=uri,
                                   status=weighted_choice(
                                       status, p=[0.9, 0.04, 0.02, 0.04]),
                                   byteslength=int(random.gauss(5000, 50)))
            batch.append(src.parser.log_to_string(**log))
        with open(output_path, 'a') if output_type == "LOG" else sys.stdout as f:
            f.writelines(batch)
            f.flush()
        time.sleep(sleep)


if __name__ == "__main__":
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import src.parser

    parser = argparse.ArgumentParser(__file__,
                                     description="Fake Apache Log Generator")
    parser.add_argument("--output",
                        "-o",
                        dest='output_type',
                        help="Write to a Log file, or to STDOUT",
                        choices=['LOG', 'CONSOLE'])
    parser.add_argument("--path",
                        "-p",
                        dest='output_path',
                        help="If Log file, where to store",
                        default="access.log")
    parser.add_argument("--num",
                        "-n",
                        dest='num_lines',
                        help="Number of lines to generate (0 for infinite)",
                        type=int,
                        default=1)
    parser.add_argument("--sleep",
                        "-s",
                        help="Sleep this long between lines (in seconds)",
                        default=0.0,
                        type=float)

    args = parser.parse_args()
    main(args.output_path, args.num_lines, args.output_type, args.sleep)
