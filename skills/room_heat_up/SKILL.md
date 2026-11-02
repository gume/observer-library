---
version: 1
title: Room heat-up after heating starts
description: How fast each room warms up after a heating start of its circuit - dead time, rate (K/h), rise, time to target - and which rooms lag behind on the same circuit.
tools: [heatup_events, debounce_binary, on_periods, temperature_segments]
---
Goal: how each room responds to its heating, and whether some rooms on the
same circuit are clearly slower (undersized emitter, closed valve, air,
balancing).

1. `house_context`: the circuits and the rooms on each (radiator circuits per
   floor, floor heating), the circuit pumps / heat call signals, the room
   targets from the owner knowledge (and any schedule).
2. Signals: room temperatures per circuit, the circuit's pump state (or
   demand), the circuit supply temperature, outdoor. `data_coverage`; use all
   history with heating starts.
3. In `run_python`: per circuit, the pump state (`debounce_binary` if noisy);
   per room on it `tools.call("heatup_events", room, pump, target=<target>)`.
   Summarise per room: median delay, median rate, typical rise, how often
   the target was reached and how fast. Note the supply temperature and the
   outdoor temperature of each start (a cold day and a low supply slow
   everything; compare like with like).
4. Compare rooms of one circuit: a room with a much longer delay or a rate
   below half of its neighbours is a finding. Rooms with other heat sources
   (AC) are compared with care.
5. `finish`: table circuit | room | starts | median delay | median rate K/h |
   reached target | remark; plots of a typical start per circuit (all rooms
   of the circuit, the supply temperature); proposals (bleed, balance, check
   the valve, a higher supply temperature) for the owner.
