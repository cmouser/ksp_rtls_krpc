import krpc
import utils
import time
from state_machine import BoosterStateMachine, State

launch_params = {
    "launch_pad_lat": -0.09721504062000887,
    "launch_pad_lon": -74.55767383241698,
    "inclination": 135,
    "apoapsis": 100000
}

# Connect to KSP
conn = krpc.connect(name='Booster Test')
vessel = conn.space_center.active_vessel
state_machine = BoosterStateMachine(conn, vessel, launch_params, State.COUNTDOWN)

state_machine.run()


