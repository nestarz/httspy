from collections import Counter
from faker import Faker


def check_high_trafic(logs, period=60 * 2, max_req_per_second=10):
    fq = len(logs) / period  # n / dt(min -> sec)
    return fq > max_req_per_second


def count_sections(logs):
    return Counter([log["path"].split("/")[1] for log in logs])


def stats():
    mean = {
        "N": 0,
        "status": Counter(),
        "version": Counter(),
        "bytes": 0,
        "country": Counter(),
        "sections": Counter(),
    }
    fake = Faker()

    cache = {"mean": mean, "last": {**mean}}

    def analyze(logs=None):
        if not logs: return cache
        last = {}
        last["sections"] = count_sections(logs)
        last["status"] = Counter(log["status"] for log in logs)
        last["version"] = Counter(log["version"] for log in logs)
        last["country"] = (Counter(fake.country() for _ in logs))
        last["bytes"] = sum(log["bytes"]
                            for log in logs) / len(logs) if logs else 0
        last["N"] = len(logs)

        for x in mean.keys():
            mean[x] += last[x]

        cache["mean"] = {**mean, "country": mean["country"].most_common(3)}
        cache["last"] = {**last, "country": last["country"].most_common(3)}
        return cache

    return analyze