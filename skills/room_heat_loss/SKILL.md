---
version: 1
title: Room heat loss (free cooling)
description: How fast each room loses heat when it is not heated - time constant, loss rate, free gains - and a ranking of the rooms. Best measured when the heating is off (before the heating season, nights without heating, a circuit switched off).
tools: [cooling_fit, temperature_segments, daily_profile]
---
Goal: for each room, how well it keeps its heat, with evidence, and which
rooms lose heat fastest.

1. `house_context`: the rooms, their floors and circuits, and from the owner
   knowledge what heats each room (radiators, floor heating, AC, stove), what
   is unheated, and known disturbances (open doors, sun, a warm boiler room).
2. `find_signals` (quantity temperature, role room) and the outdoor
   temperature; `data_coverage` for all of them. Use as much history as
   exists; prefer periods when nothing heats the room.
3. Which times are unheated? The heat call and the circuit pumps of the
   room's circuit (on = heated). If an AC or another source exists that is
   not recorded, say so: it shows up as free gains and lower confidence.
4. In `run_python`: per room `obs.data.series` (room, outdoor, the pump/heat
   call at 1 min), mask = not heated, `tools.call("cooling_fit", room,
   outdoor, mask=mask)`. Also `temperature_segments` to show the falling
   segments and their rates, and `daily_profile` for sun or use patterns
   (gains in the afternoon point to sun).
5. Judge each fit: enough points and hours (a day or more), r2, plausible tau
   (typical 20-150 h for a room; under 15 h means strong losses or a
   ventilated / open space; negative or no fit means heat sources dominate).
   A large positive gain means sun, neighbours or an unrecorded heater.
6. `finish`: a table room | tau_h | cooling K/h at 10 K difference | gains |
   r2 | hours | remark, ranked by loss; plots of the falling segments; what
   to check (windows, doors, insulation, sensor position near a window or a
   warm wall). Rooms whose result is not trustworthy are listed separately.
