from fomo.logging.stats import Stats


def test_register():
    stats = Stats()

    stats.register("naive", "sktime", 1.24, 0.31)

    assert stats.snapshot()["models"]["naive"] == {
        "executor": "sktime",
        "load_s": 1.24,
        "warmup_s": 0.31,
        "requests": {"total": 0, "ok": 0, "failed": 0},
        "latency_s": {
            "count": 0,
            "total": 0.0,
            "mean": None,
            "fastest": None,
            "slowest": None,
        },
    }


def test_record():
    stats = Stats()
    stats.register("naive", "sktime", 1.24, 0.31)

    stats.record("naive", 1.0, ok=True)
    stats.record("naive", 3.0, ok=False)

    row = stats.snapshot()["models"]["naive"]
    assert row["requests"] == {"total": 2, "ok": 1, "failed": 1}
    assert row["latency_s"] == {
        "count": 2,
        "total": 4.0,
        "mean": 2.0,
        "fastest": 1.0,
        "slowest": 3.0,
    }


def test_snapshot():
    snapshot = Stats().snapshot()

    assert snapshot["uptime_s"] >= 0
    assert "cpu_rss_mb" in snapshot["memory"]
    assert "gpu_mb" in snapshot["memory"]
    assert snapshot["models"] == {}
