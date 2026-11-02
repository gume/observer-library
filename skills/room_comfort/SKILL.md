---
version: 1
title: Room comfort against targets
description: How well each room holds its target - time in band, too cold or too warm, degree-hours below, day and night - and the typical daily course.
tools: [comfort_stats, daily_profile, degree_hours]
---
Goal: which rooms are too cold or too warm, when, and how much.

1. `house_context`: the room targets and schedules from the owner knowledge
   (day/night targets, rooms not heated on purpose, rooms heated by other
   means). Without a stated target, ask in the report and use 21 °C for
   living rooms and 18-19 °C for bedrooms as a stated assumption.
2. Room temperatures and outdoor; `data_coverage`; use the longest period
   with the heating in operation (and separately without, if both exist).
3. In `run_python`: per room `tools.call("comfort_stats", room, target,
   band=0.5, periods={"day": [6, 22], "night": [22, 6]}, tz=<house time
   zone>)` and `tools.call("daily_profile", room, tz=...)`;
   `tools.call("degree_hours", outdoor)` for the weather of the period.
4. Judge: in-band share, the share and degree-hours below (cold is the
   usual complaint), over-heating (energy), the daily profile (morning dips,
   afternoon sun). Relate cold periods to the weather and to the heating
   state of the circuit (`get_events`, pump states).
5. `finish`: table room | target | day in band % | night in band % | below
   % | degree-hours below | remark; daily profile plots of the worst rooms;
   proposals (targets, schedules, heating curve) for the owner.
