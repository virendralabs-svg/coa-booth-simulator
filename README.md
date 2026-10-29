# B1: Booth and Modified Booth Simulator
COA Bright Learner Activity - 25CE3PCC03, Don Bosco Institute of Technology

Name: Virendra Rawat  Roll No: 42

## Files
- booth_simulator.py - the program
- test_output.txt    - output of a full run

## How to run (Python 3, no extra libraries)
    python booth_simulator.py              # tests all 256 pairs of 4-bit numbers
    python booth_simulator.py -13 11 6     # step-by-step table for M=-13, Q=11, 6 bits

## Test results (all 4-bit signed pairs, -8 to +7)
| Measure | Booth | Modified Booth |
|---|---|---|
| Wrong products | 0 | 0 |
| Total add/sub operations | 512 | 384 |
| Average per multiplication | 2.00 | 1.50 |
| Maximum | 4 | 2 |

Modified Booth used fewer operations in 112 pairs, equal in 144, more in 0 (25% fewer overall).
