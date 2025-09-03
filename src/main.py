import krpc
import utils
import time

# Connect to KSP
conn = krpc.connect(name='Booster Test')
vessel = conn.space_center.active_vessel

print(f"Controlling vessel: {vessel.name}")

# get starting lat/lon
position = vessel.position(vessel.orbit.body.reference_frame)
lp_lat = vessel.orbit.body.latitude_at_position(position, vessel.orbit.body.reference_frame)
lp_lon = vessel.orbit.body.longitude_at_position(position, vessel.orbit.body.reference_frame)
print(f"Launch pad position: {lp_lat}, {lp_lon}")

while True:
    impact_lat, impact_lon = utils.calculate_impact_position(conn, vessel.orbit.body, vessel.orbit)
    print(f"Impact position: {impact_lat}, {impact_lon}")
    distance = utils.great_circle_distance(lp_lat, lp_lon, impact_lat, impact_lon, vessel.orbit.body.equatorial_radius)
    print(f"Distance from launch pad: {distance} meters")
    time.sleep(1)