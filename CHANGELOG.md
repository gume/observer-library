# Changelog

The library version (library.yaml) follows semantic versioning: minor for
new or improved items, major when an item's inputs or outputs change
incompatibly. Every item has its own integer version in tool.yaml /
SKILL.md, raised whenever it changes.

## 0.2.0 - 2026-11-02

Room analysis.

* Tools: `temperature_segments` (rising/falling/flat with rates),
  `cooling_fit` (free cooling: time constant, loss rate, free gains),
  `room_rc_fit` (heating gain, losses, required supply temperature),
  `heatup_events` (delay, rate, time to target per heating start),
  `comfort_stats` (time in band, degree-hours below, day/night),
  `daily_profile`, `degree_hours`.
* Skills: `room_heat_loss`, `room_heat_up`, `room_comfort`, `emitter_sizing`.

## 0.1.0 - 2026-11-02

First items, moved out of the HeatpumpsN observer repository.

* Tools: `resample_hold`, `debounce_binary`, `on_periods`, `pair_offset`,
  `setpoint_tracking`, `fopdt_fit`.
* Skills: `sensor_health`, `heating_start`, `boiler_cycling`,
  `plant_identification`.
