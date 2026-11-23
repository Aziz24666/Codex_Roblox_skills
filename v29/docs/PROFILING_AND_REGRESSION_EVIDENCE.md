# Profiling and regression evidence

## Import measured captures

V29 comparison commands consume JSON measurements that a developer has collected separately with Roblox Studio tools or a documented test harness. The command does not import proprietary profiler formats, start Studio, or capture telemetry. Each capture identifies the build, device profile, measurement source, and numeric metrics.

A capture contains `schema_version`, `build`, `device_profile`, `measurement_source`, optional `scene` and `player_count`, and a `metrics` object containing any measured subset of `frame_time_ms_p50`, `frame_time_ms_p95`, `memory_mb`, `load_time_s`, `script_cpu_ms`, and `replication_kbps`.

Validate and compare captures stored inside the selected project directory:

```powershell
python ".\v29\tools\v29.py" compare --root "C:\Path\To\YourGame" --baseline ".codex\perf\baseline.json" --candidate ".codex\perf\candidate.json" --budgets ".codex\performance-budgets.json"
python ".\v29\tools\v29.py" report --root "C:\Path\To\YourGame" --audit ".codex\reports\v29-performance-audit.json" --comparison ".codex\reports\v29-performance-comparison.json"
```

The comparator requires different build identifiers and the same device profile. It reports numeric deltas, candidate values above configured budgets, and metrics missing from either capture. The default regression threshold is a five-percent increase; adjust it to your measurement noise and project policy.

## Evidence quality

Compare equivalent scenes, player counts, device classes, server conditions, build configurations, and profiler intervals. Repeat measurements and retain source revision and capture provenance. Do not mix cold-load with warm-load captures or compare different device tiers as if they were equivalent.

A supplied JSON file is developer-provided evidence, not independently authenticated telemetry. V29 does not verify that a capture genuinely came from Studio. Never label a planned test as executed or a static scan as a measured performance test.
