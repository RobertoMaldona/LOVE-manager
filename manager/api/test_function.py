import string
import math
import random


def is_inside_area(origin, test_point, radius):
    earth_radius = 6371 # in km
    angle_1 = (origin[0]) * math.pi/180 # in radians
    angle_2 = (test_point[0]) * math.pi/180
    delta_angle1 = (test_point[0] - origin[0]) * math.pi/180
    delta_angle2 = (test_point[1] - origin[1]) * math.pi/180
    
    a = math.sin(delta_angle1/2)**2 + \
        math.cos(angle_1) * math.cos(angle_2) * math.sin(delta_angle2/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = earth_radius * c # in km 

    print( "radio actual", d)

    if d <= radius: 
        return True 
    else: 
        return False
    


def plane_generator():
    return { "id": ''.join(random.choices(string.ascii_lowercase + string.digits, k=4)), # k = id_length. 
             "loc" : (random.uniform(-30.240839 - 1.8, -30.240839 + 1.8), random.uniform(-70.736919 - 1.4, -70.736919 + 1.4)),  # South Gemini Observatory is in  lat long -30.240839, -70.736919
             "vel" : random.randint(200, 280), # mean in km/h
             }

# a = plane_generator()
# print(a)
# print(is_inside_area((-30.2326, -70.7312), a["loc"], 200))

location = "(-30.2326, -70.7312)"
location = (((location.replace("(" , "")).replace(")" , "")).replace("," , " ")).split()
location = (float(location[0]), float(location[1]))
print(location)
