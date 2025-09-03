# Episode 1 - State Machines
(Finite) State machines are use in software to break up complex systems into a series of simpler states. Each state contains code to control the system while it is in that state. When certain conditions are met, it will transition to a new state.

A simple example could be a thermostat. It could have 3 states: Heating, Cooling, Idle. If the temperature falls to low it transitions to Heating. If it gets too high it transitions to cooling. Finally, if the temperature is in the ideal range, then it transitions to idle.

In reality these can be very comlpicated webs of states. However, for simplicity we will use an idealistic example where each state can only go to the next state.

# List of States
## Ignition
> Ignition

Turn on the Engines and throttle up.

Nominal Exit Conditions: 
* Throttle = 100%
* AND TWR > 1

## Liftoff
> Liftoff!

Release the rocket and clear the tower.

Nominal Exit Conditions:
* Above a given altitude

## Pitch Over
> Vehicle is pitching down range

Also known as a "Pad Avoidance Maneuver". We want to tilt the rocket a bit in the direction of our desired orbit.

Nominal Exit Conditions:
* Vehicle is tilted with X degrees of our target pitch.

## Roll Program
> Roll program complete

Roll the program into a consistent attitude for ascent. Imagine it as always wanting your belly down, regardless of which way you are flying. [EDA has a whole video about it!](https://everydayastronaut.com/why-do-cylindrical-rockets-roll/)

Nominal Exit Conditions:
* Vehicle has rolled within X degrees of our target roll.

## Gravity Turn
In order to go to orbit we need horizontal velocity. This stage slowly tilts us more horizontal. We're going to use a very steep ascent and descent to cut down on math. It will be very suboptimal but okay for demonstration.

Nominal Exit Conditions:
* Target separation apoapsis reached 
* OR minimum fuel level reached

## Stage Separation
> MECO.... Stage Separation Confirmed

We want to shut down our engines and deploy the second stage

Nominal Exit Conditions:
* Second stage has deployed and separated enough

## Flip
To get back to the launch site we need to flip around. 

Nominal Exit Conditions:
* Vehicle is pointed in roughly the desired direction

## Boostback
> Boostback Startup.... Boostback shutdown

We need to alter our velocity so that our ballistic trajectory will land us near the landing zone.

Nominal Exit Conditions:
* Ballistic impact point within X meters of landing zone.

## Coast
Maintain orientation and coast through space. Deploy gridfins if we have them. Perhaps some RCS puffs to help our target accuracy.

Nominal Exit Conditions:
* Vehicle enters the atmosphere.

## Entry
Use the aero surfaces to pinpoint our trajectory toward the landing zone.

Nominal Exit Conditions:
* Vehicle hits altitude where landing burn needs to begin.

## Landing
> Landing burn startup

Select final landing spot and decelerate the vehicle to 0 vertical and horiztonal velocity. Deploying landing legs when appropriate.

Nominal Exit Conditions:
* Vehicle has touched down

## Balance
KSP's landing legs kind of suck so I'm adding a state to make sure we don't fall over. It will be our final state so no need to have an exit strategy.