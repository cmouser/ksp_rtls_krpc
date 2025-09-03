import math

def calculate_impact_position(connection, body, orbit):
    if orbit.eccentricity >= 1 or orbit.apoapsis_altitude < 0:
        return None  # No valid suborbital trajectory
    a = orbit.semi_major_axis
    e = orbit.eccentricity
    R = body.equatorial_radius
    arg = (a * (1 - e**2) / R - 1) / e
    if abs(arg) > 1:
        return None
    nu_impact = math.acos(arg)
    candidates = [nu_impact, 2 * math.pi - nu_impact]
    current_nu = math.radians(orbit.true_anomaly)
    current_m = orbit.mean_anomaly  # Radians
    mean_motion = math.sqrt(body.gravitational_parameter / a**3)
    current_ut = connection.space_center.ut
    min_dt = float('inf')
    impact_ut = None
    for nu in candidates:
        cos_nu = math.cos(nu)
        sin_nu = math.sin(nu)
        ea = math.acos((e + cos_nu) / (1 + e * cos_nu))
        if sin_nu < 0:
            ea = 2 * math.pi - ea
        m = ea - e * math.sin(ea)
        dm = (m - current_m + 2 * math.pi) % (2 * math.pi)
        dt = dm / mean_motion
        if 0 < dt < min_dt:
            min_dt = dt
            impact_ut = current_ut + dt
    if impact_ut is None:
        return None
        
    pos = orbit.position_at(impact_ut, body.reference_frame)
    
    lat = body.latitude_at_position(pos, body.reference_frame)
    lon = body.longitude_at_position(pos, body.reference_frame)

    # account for planetary rotation
    rotation_radians = body.rotational_speed * min_dt
    lon = (lon - rotation_radians/(2*math.pi) * 360) % 360
    if lon > 180:
        lon -= 360
    
    return lat, lon

def great_circle_distance(lat1, lon1, lat2, lon2, radius):
    lat1, lat2, lon1, lon2 = map(math.radians, [lat1, lat2, lon1, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return c * radius