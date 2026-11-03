---
version: 1
title: Mixer control what-if (the controller's MPC in simulation)
description: Answers "what if" questions about the mixer control - other MPC parameters, setpoints, radiator states, a recorded morning replayed - with the controller's own MPC core in simulation (obs.sim), checked against how the real controller performed (control_metrics).
tools: [control_metrics]
---
Goal: a quantified answer to a question like "would a longer transport delay
in the floor set calm the valve?", "how fast does the floor heat up after a
setpoint step from 30 to 35 °C?", "what did this morning's prediction miss
cost?" - with its limits stated.

`obs.sim` (in run_python; `help(sim)`) runs the controller's own MPC core:

* `sim.replay(start, stop, sets=...)`: a recorded stretch (floor pump on, no
  DHW, one radiator state) with its recorded supply, return and setpoint;
  the mixer is a model, the simulated controller drives it. Best for "what
  if on a real day".
* `sim.closed_loop(hours, setpoint, radiators, dhw, preset, tout, sets=...)`:
  the identified house (boiler cycles, heat exchanger, mixer, slab, room).
  Best for scenarios that were not recorded (setpoint steps, a cold start,
  long runs).
* `sim.compare(fn, variants={name: sets}, ...)`: metrics side by side.
* `sim.current_sets()`: the controller's parameter sets now. `sets` given to
  the functions override fields of these.

Method:

1. **Restate the question** as variants of parameter sets or scenarios, and
   the metrics that answer it (error to the setpoint, overshoot, time to the
   setpoint, valve travel, motor starts, fallbacks to cautious control).
2. **Pick situations** from the record: `data.events` (prediction misses,
   homing, setpoint changes) and `data.coverage`; several stretches of 1-3 h,
   not one. Say which and why.
3. **Validate first.** Replay each stretch with the current sets (`sets=None`)
   and compute the real controller's metrics on the same stretch with
   `control_metrics` (recorded forward temperature, setpoint, recorded
   position; the replay's trace has `recorded` and `recorded_pos`). If the
   simulated and the recorded control differ widely (e.g. RMSE by more than
   0.5 K, travel by more than 50 %), the plant model does not fit that
   stretch: say so, and trust only differences between variants, not
   absolute values - or drop the stretch.
4. **Run the variants** on every stretch with `sim.compare`; collect a table
   per stretch and the totals.
5. **Judge robustness.** A change that wins on one stretch and loses on
   others is not an improvement. A single event (a setpoint drop, a homing)
   can dominate a total: report it separately.
6. **Report honestly**: the variants, the stretches, a metrics table, a plot
   of the most telling stretch (recorded vs simulated forward temperature
   and valve position), and the limits:
   * the return is replayed as recorded (in the house it follows the forward
     temperature over hours), so long-term effects are not covered by replay;
   * the controller's settings around the core (minimum opening, ceiling,
     stroke time) are assumed (`settings=`) - the defaults are the
     firmware's;
   * a parameter change reaches the controller only through a proposal the
     owner approves on the Parameters tab: put concrete values into
     `proposals` with the evidence, never anything else.
