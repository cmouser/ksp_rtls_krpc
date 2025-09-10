from enum import Enum
from abc import ABC, abstractmethod
from math import atan2, degrees, inf
import time
import utils

class BoosterStateMachine:
    log_interval = 1.0
    loop_interval = 0.1
    
    def __init__(self, conn, vessel, launch_params, initial_state_type):
        self.conn = conn
        self.vessel = vessel
        self.launch_params = launch_params
        self.current_state_type = None
        self.states = {
            State.COUNTDOWN: CountdownState(),
            State.IGNITION: IgnitionState(),
            State.LIFTOFF: LiftoffState(),
            State.PITCH_OVER: PitchOverState(),
            State.ROLL_PROGRAM: RollProgramState(),
            State.GRAVITY_TURN: GravityTurnState(),
            State.STAGE_SEPARATION: StageSeparationState(),
            State.FLIP: FlipState(),
            State.BOOSTBACK: BoostbackState(),
            State.COAST: CoastState(),
            State.ENTRY: EntryState(),
            State.LANDING: LandingState(),
            State.BALANCE: BalanceState(),
        }

        self.state_init_time = time.time()
        self.transition_to_state(initial_state_type)

    def transition_to_state(self, state):
        print(f"Transitioning from {self.current_state_type} to state: {state}")
        self.current_state_type = state
        self.state_init_time = time.time()
        self.states[self.current_state_type].enter(self)

    def run(self):
        last_log_time = time.time()
        while True:
            current_time = time.time()

            should_log =  (current_time - last_log_time) > self.log_interval
            if should_log:
                last_log_time = current_time

            state_elapsed_time = current_time - self.state_init_time
            self.states[self.current_state_type].update(self, state_elapsed_time, should_log)
            time.sleep(self.loop_interval)


class StateInterface(ABC):
    @abstractmethod
    def enter(self, state_machine):
        pass
    
    @abstractmethod
    def update(self, state_machine, state_elapsed_time, should_log):
        pass

# Create Enum of states
class State(Enum):
    COUNTDOWN = "Countdown"
    IGNITION = "Ignition"
    LIFTOFF = "Liftoff"
    PITCH_OVER = "Pitch Over"
    ROLL_PROGRAM = "Roll Program"
    GRAVITY_TURN = "Gravity Turn"
    STAGE_SEPARATION = "Stage Separation"
    FLIP = "Flip"
    BOOSTBACK = "Boostback"
    COAST = "Coast"
    ENTRY = "Entry"
    LANDING = "Landing"
    BALANCE = "Balance"

class CountdownState(StateInterface):
    def enter(self, state_machine):
        print("Countdown!")
    
    def update(self, state_machine, state_elapsed_time, should_log):
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        state_machine.transition_to_state(State.IGNITION)

class IgnitionState(StateInterface):
    throttle_up_seconds = 1
    def enter(self, state_machine):
        state_machine.vessel.control.throttle = 0.5
        state_machine.vessel.control.activate_next_stage()
        print("Ignition!")
    
    def update(self, state_machine, state_elapsed_time, should_log):
        throttle = min(1, 0.5 + 0.5 * state_elapsed_time / self.throttle_up_seconds)
        state_machine.vessel.control.throttle = throttle

        weight = state_machine.vessel.mass * state_machine.vessel.orbit.body.surface_gravity
        thrust = state_machine.vessel.thrust
        twr = thrust / weight

        if throttle >= 1 and twr > 1:
            print(f"TWR: {twr} Throttle: {throttle}")
            state_machine.transition_to_state(State.LIFTOFF)

        if should_log:
            print(f"TWR: {twr:.2f} Throttle: {throttle:.2f}")

class LiftoffState(StateInterface):
    def enter(self, state_machine):
        state_machine.vessel.control.throttle = 1
        state_machine.vessel.control.activate_next_stage()
        print("Liftoff!")

    def update(self, state_machine, state_elapsed_time, should_log):
        altitude = state_machine.vessel.flight().mean_altitude
        if altitude > 250:
            state_machine.transition_to_state(State.PITCH_OVER)

        if should_log:
            print(f"Altitude: {int(altitude)} meters")

class PitchOverState(StateInterface):
    def enter(self, state_machine):
        state_machine.vessel.auto_pilot.engage()
       # state_machine.vessel.control.rcs = True
        print("Pitch Over!")
    
    def update(self, state_machine, state_elapsed_time, should_log):
        target_pitch = 85
        target_heading = state_machine.launch_params["inclination"]
        state_machine.vessel.auto_pilot.target_pitch_and_heading(target_pitch, target_heading)

        pitch_error = abs(target_pitch - state_machine.vessel.flight().pitch)
        heading_error = abs(target_heading - state_machine.vessel.flight().heading)
        if pitch_error < 4 and heading_error < 8:
            state_machine.transition_to_state(State.ROLL_PROGRAM)

        if should_log:
            print(f"Pitch: {state_machine.vessel.flight().pitch:.2f} Heading: {state_machine.vessel.flight().heading:.2f} vs Target {target_heading:.2f}")

class RollProgramState(StateInterface):
    def enter(self, state_machine):
        state_machine.vessel.auto_pilot.engage()
        state_machine.vessel.control.rcs = True
    
    def update(self, state_machine, state_elapsed_time, should_log):
        target_roll = 0
        state_machine.vessel.auto_pilot.target_roll = target_roll
        roll_error = abs(target_roll - state_machine.vessel.flight().roll)
        if roll_error < 3:
            state_machine.transition_to_state(State.GRAVITY_TURN)
        
        if should_log:
            print(f"Roll: {state_machine.vessel.flight().roll:.2f} vs Target {target_roll:.2f}")

class GravityTurnState(StateInterface):
    min_fuel = 0.18
    def enter(self, state_machine):
        state_machine.vessel.auto_pilot.engage()
        # state_machine.vessel.control.rcs = False
        self.initial_altitude = state_machine.vessel.flight().mean_altitude
    
    def update(self, state_machine, state_elapsed_time, should_log):
        target_heading = state_machine.launch_params["inclination"]
        mean_altitude = state_machine.vessel.flight().mean_altitude
        target_pitch = max(0, 85 - 85 * (mean_altitude - self.initial_altitude) / 60000)
        state_machine.vessel.auto_pilot.target_pitch_and_heading(target_pitch, target_heading)
        
        # Exit Conditions
        liquid_fuel_percentage = state_machine.vessel.resources.amount("LiquidFuel") / state_machine.vessel.resources.max("LiquidFuel")
        current_apoapsis = state_machine.vessel.orbit.apoapsis_altitude
        if liquid_fuel_percentage < self.min_fuel or current_apoapsis >= state_machine.launch_params["apoapsis"]:
            state_machine.transition_to_state(State.STAGE_SEPARATION)
        
        if should_log:
            print(f"Pitch: {state_machine.vessel.flight().pitch:.2f} vs Target {target_pitch:.2f} Fuel: {liquid_fuel_percentage:.2f} Apoapsis: {current_apoapsis:.2f}")

class StageSeparationState(StateInterface):
    stage_seperation_confirmed = False
    pre_separation_delay = 3
    total_separation_delay = 7
    

    def enter(self, state_machine):
        state_machine.vessel.control.throttle = 0
        state_machine.vessel.auto_pilot.disengage()
        state_machine.vessel.auto_pilot.sas = True
        state_machine.vessel.control.rcs = True
        state_machine.vessel.control.sas_mode = state_machine.vessel.control.sas_mode.stability_assist

    def update(self, state_machine, state_elapsed_time, should_log):
        # Delay until time to separte the stage
        print(f"State elapsed time: {state_elapsed_time}")
        if state_elapsed_time > self.pre_separation_delay:
            if not self.stage_seperation_confirmed:
                self.stage_seperation_confirmed = True
                state_machine.vessel.control.activate_next_stage()
        
        if state_elapsed_time > self.total_separation_delay:
            state_machine.transition_to_state(State.FLIP)

class FlipState(StateInterface):
    def enter(self, state_machine):
        state_machine.vessel.control.throttle = 0
        state_machine.vessel.auto_pilot.disengage()
        state_machine.vessel.auto_pilot.sas = True
        state_machine.vessel.control.rcs = True
        state_machine.vessel.control.sas_mode = state_machine.vessel.control.sas_mode.retrograde

    def update(self, state_machine, state_elapsed_time, should_log):
        state_machine.vessel.control.sas_mode = state_machine.vessel.control.sas_mode.retrograde
        opposite_heading = (state_machine.launch_params["inclination"] + 180) % 360
        d_heading = abs(state_machine.vessel.flight().heading - opposite_heading)
        if d_heading < 90 or d_heading > 270:
            state_machine.transition_to_state(State.BOOSTBACK)
        
        if should_log:
            print(f"Heading: {state_machine.vessel.flight().heading:.2f} vs Target {opposite_heading:.2f}")

class BoostbackState(StateInterface):

    overshoot = 1000
    def enter(self, state_machine):
        state_machine.vessel.control.throttle = 0
        state_machine.vessel.auto_pilot.engage()
        state_machine.vessel.auto_pilot.sas = False
        state_machine.vessel.control.rcs = False
    
    def update(self, state_machine, state_elapsed_time, should_log):
        vessel_lat = state_machine.vessel.flight(state_machine.vessel.orbit.body.reference_frame).latitude
        vessel_lon = state_machine.vessel.flight(state_machine.vessel.orbit.body.reference_frame).longitude
        lp_lat = state_machine.launch_params["launch_pad_lat"]
        lp_lon = state_machine.launch_params["launch_pad_lon"]
        kerbin_radius = state_machine.vessel.orbit.body.equatorial_radius

        dy = lp_lat - vessel_lat
        dx = lp_lon - vessel_lon
        target_heading = (90 - degrees(atan2(dy, dx))) % 360
        impact_distance = inf

        impact_position = utils.impact_calculations.calculate_impact_position(state_machine.conn, state_machine.vessel.orbit.body, state_machine.vessel.orbit)
        if impact_position is not None:
            impact_lat, impact_lon = impact_position
            dy = state_machine.launch_params["launch_pad_lat"] - impact_lat
            dx = state_machine.launch_params["launch_pad_lon"] - impact_lon
            impact_target_heading = (90 - degrees(atan2(dy, dx))) % 360
            if abs(impact_target_heading - target_heading) < 110:
                target_heading = impact_target_heading
            
            impact_distance = utils.impact_calculations.great_circle_distance(lp_lat, lp_lon, impact_lat, impact_lon, kerbin_radius)
            lp_distance = utils.impact_calculations.great_circle_distance(lp_lat, lp_lon, vessel_lat, vessel_lon, kerbin_radius)
            vi_distance = utils.impact_calculations.great_circle_distance(vessel_lat, vessel_lon, impact_lat, impact_lon, kerbin_radius)

            if impact_distance < 2000 and vi_distance - self.overshoot > lp_distance:
                print(f"impact distance: {impact_distance:.2f} lp distance: {lp_distance:.2f} vi distance: {vi_distance:.2f}")
                state_machine.transition_to_state(State.COAST)

        state_machine.vessel.auto_pilot.target_pitch_and_heading(0, target_heading)
        state_machine.vessel.control.throttle = min(1, 0.05 + 0.95 * impact_distance / 40000)

        
        if should_log:
            print(f"impact distance: {impact_distance:.2f} lp distance: {lp_distance:.2f} vi distance: {vi_distance:.2f}")

class CoastState(StateInterface):
    def enter(self, state_machine):
        state_machine.vessel.control.throttle = 0
        state_machine.vessel.auto_pilot.disengage()
        state_machine.vessel.auto_pilot.sas = True
        state_machine.vessel.control.speed_mode = state_machine.vessel.control.speed_mode.surface
        state_machine.vessel.control.rcs = True
        state_machine.vessel.control.sas_mode = state_machine.vessel.control.sas_mode.retrograde
        state_machine.vessel.control.brakes = True
    
    def update(self, state_machine, state_elapsed_time, should_log):
        state_machine.vessel.control.throttle = 0
        state_machine.vessel.control.sas_mode = state_machine.vessel.control.sas_mode.retrograde
        vessel_lat = state_machine.vessel.flight(state_machine.vessel.orbit.body.reference_frame).latitude
        vessel_lon = state_machine.vessel.flight(state_machine.vessel.orbit.body.reference_frame).longitude
        lp_lat = state_machine.launch_params["launch_pad_lat"]
        lp_lon = state_machine.launch_params["launch_pad_lon"]
        kerbin_radius = state_machine.vessel.orbit.body.equatorial_radius

        impact_position = utils.impact_calculations.calculate_impact_position(state_machine.conn, state_machine.vessel.orbit.body, state_machine.vessel.orbit)
        impact_lat, impact_lon = impact_position  
        impact_distance = utils.impact_calculations.great_circle_distance(lp_lat, lp_lon, impact_lat, impact_lon, kerbin_radius)

        if should_log:
            print(f"impact distance: {impact_distance:.2f}")

class EntryState(StateInterface):
    def enter(self, state_machine):
        pass
    def update(self, state_machine, state_elapsed_time, should_log):
        pass

class LandingState(StateInterface):
    def enter(self, state_machine):
        pass
    def update(self, state_machine, state_elapsed_time, should_log):
        pass

class BalanceState(StateInterface):
    def enter(self, state_machine):
        pass
    def update(self, state_machine, state_elapsed_time, should_log):
        pass