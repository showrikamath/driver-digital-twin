# Driver Digital Twin

A Python-based simulation project exploring how a Digital Twin can learn and identify driver behaviour from vehicle telemetry.

## Overview

This project simulates a vehicle and its driver behaviour using Python.

The system collects vehicle telemetry such as speed, acceleration, braking and driver actions. The collected data is then used to identify the driver's behaviour, maintain a Digital Twin state, provide real-time feedback, and learn new driver profiles when an unknown driver is detected.

The project currently includes three predefined driver profiles:

- Calm
- Normal
- Aggressive

It can also learn new driver profiles such as `driver_1`, `driver_2`, etc.

---

## How It Works

Driver Behaviour
       |
       v
Vehicle Simulation
       |
       v
Telemetry
       |
       +----------------------+
       |                      |
       v                      v
Digital Twin          Driver Identification
       |                      |
       v                      v
Real-time Feedback      Profile Matching
                              |
                     +--------+--------+
                     |                 |
                   Known            Unknown
                     |                 |
                     v                 v
                Driver ID       Store Evidence
                                       |
                                  3 Observations
                                       |
                                       v
                                Consistency Check
                                       |
                                       v
                                New Driver Profile


