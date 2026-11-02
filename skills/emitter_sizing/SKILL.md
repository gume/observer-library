---
version: 1
title: Emitter sizing and heating effectiveness per room
description: Fits a heat-balance model per room (heating gain, losses, free gains) from heated and unheated periods and tells which supply temperature each room needs at design outdoor temperatures - which radiators or floor loops are too small, which rooms limit the heating curve.
tools: [room_rc_fit, cooling_fit, heatup_events]
---
Goal: how effective the heating is in each room and what supply
temperature each room needs; the room that needs the highest supply
temperature limits the whole circuit (and the boiler's efficiency).

1. `house_context`: rooms per circuit, the circuit's supply temperature
   signal (radiator circuits: the boiler/circuit forward; floor: the mixed
   forward), pump states, targets from the owner knowledge.
2. Data: needs both heated and unheated periods, ideally several days with
   different outdoor temperatures. `data_coverage`; if the heating has not
   run yet, stop and report that only the losses can be measured now
   (use the `room_heat_loss` skill).
3. In `run_python`: per room `tools.call("room_rc_fit", room, outdoor,
   supply, heat_kind="supply_temp", active=<pump state>, target=<target>)`.
   Cross-check b (loss) with `cooling_fit` on the unheated periods: they
   should agree within about 30 %; if not, say the model is uncertain.
4. Judge: fit quality (r2 of the derivative fit, sim_rmse_K below about
   0.5 K), the required supply temperatures at -10/-5/0 °C, the steady-state
   room temperature at the observed supply. Rooms needing far more than
   their neighbours: emitter too small, valve throttled, or extra losses.
5. `finish`: table circuit | room | gain a | tau_h | required supply at 0 /
   -10 °C | fit quality | remark, the limiting room per circuit, and
   proposals (larger emitter, balancing, the minimum supply temperature for
   the heating curve) for the owner.
