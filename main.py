from datetime import datetime
import asyncio

import src.parser
import src.monitor
import src.web

def monitor_stats(loop, log_file, period, analyzer):
    logs = src.parser.get_logs(path=log_file, period=period)
    print(analyzer(logs))
    loop.call_later(period, monitor_stats, loop, log_file, period, analyzer)


def monitor_alerts(loop, log_file, threshold, period, refresh_rate, was_high):
    alert = lambda m: f"{m} - hits = {len(logs)}, triggered at {datetime.now()}"
    logs = src.parser.get_logs(path=log_file, period=period)
    high = src.monitor.check_high_trafic(logs,
                                         period,
                                         max_req_per_second=threshold)
    if high and not was_high: print(alert("High traffic generated an alert"))
    if not high and was_high: print(alert("Traffic recover a normal state"))
    loop.call_later(refresh_rate, monitor_alerts, loop, log_file, threshold,
                    period, refresh_rate, high)

def main(log_file, threshold, period):
    analyzer = src.monitor.stats()
    loop = asyncio.get_event_loop()
    loop.call_soon(monitor_stats, loop, log_file, period, analyzer)
    loop.call_soon(monitor_alerts, loop, log_file, threshold, 60 * 2, 2, False)
    src.web.web_monitor(analyzer)

    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Monitor W3C Formatted HTTP access log.')
    parser.add_argument('log_file',
                        type=str,
                        nargs="?",
                        default="/var/log/access.log",
                        help='W3C Formatted HTTP access log')
    parser.add_argument('--threshold',
                        dest='threshold',
                        default=10,
                        type=int,
                        help='Request per seconds when to generate an alert')
    parser.add_argument('--period',
                        dest='period',
                        type=int,
                        default=10,
                        help='Display stats every x secs')

    args = parser.parse_args()

    main(args.log_file, args.threshold, args.period)