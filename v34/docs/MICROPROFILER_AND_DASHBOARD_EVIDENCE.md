# MicroProfiler, Script Profiler, and Dashboard Evidence

## Diagnose the correct side

Use the Developer Console and MicroProfiler for the affected client or server. Client FPS does not diagnose server heartbeat. Server CPU time does not explain every client render issue. Capture both sides when the symptom crosses the boundary.

## MicroProfiler

Use saved frame dumps to examine expensive frames and task groups. Keep profiler mode and capture settings identical between baseline and candidate. Use the network view for relevant network-related captures, and note when a high-detail capture setting increases profiling overhead. V34 accepts structured aggregate metrics and evidence references; it does not parse binary or proprietary profiler dump files.

## Script Profiler

Record client and server separately. The profiler is focused on CPU-consuming calls; sleeping/waiting work is not counted as CPU time. Keep the sampling frequency and duration fixed when comparing runs.

## Developer Console memory investigation

For long-running server concerns, track:
- LuaHeap: a growing value can indicate retained Lua objects.
- InstanceCount: persistent instance growth can indicate objects are not being cleaned up.
- PlaceScriptMemory: helps identify script-attributed memory.
- Server memory by age and process group.

Also inspect event connections and references that outlive their owner. A trend is a diagnostic lead; it is not a definitive leak verdict.

## Performance Dashboard

Use aggregate client and server metrics to monitor a release. The current Creator Hub documentation says the client/server charts require at least 100 daily active users. If charts are unavailable, keep the metric unknown and use Studio captures or another authorized aggregate source instead.

## Useful official references

- https://create.roblox.com/docs/performance-optimization/identify
- https://create.roblox.com/docs/performance-optimization/improve
- https://create.roblox.com/docs/studio/optimization/scriptprofiler
- https://create.roblox.com/docs/production/analytics/performance
- https://create.roblox.com/docs/performance-optimization/microprofiler/network
