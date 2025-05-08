
import numpy as np
import math
import osmnx as ox

"""
def midpoint(point1, point2):
    return np.array([np.mean([point1[0], point2[0]]), np.mean([point1[1], point2[1]])])

def perpendicular(vector):
    vector_t = np.array([-vector[1], vector[0]]) / np.linalg.norm(vector)
    return vector_t

def vector(p1, p2):
    return (p2-p1) / np.linalg.norm(p2-p1)

def three_points_intersection(p1, p2, p3):
    "Three points can define two mediatrix which intersection is the searched point.

    Args:
        p1 (_type_): _description_
        p2 (_type_): _description_
        p3 (_type_): _description_
    "
    mid_points = [midpoint(p1,p2), midpoint(p2,p3)]
    vectors = [vector(p1,p2), vector(p2,p3)]
    mediatrix = [perpendicular(v) for v in vectors]
    aux_points = [mid_points[0] + mediatrix[0], mid_points[1] + mediatrix[1]]
    
    mid_points.extend(aux_points)
    points = mid_points
    
    # Cramer (intersection between line p1-p3 and line p2-p4)
    x1 = points[0][0]; y1 = points[0][1]
    x2 = points[2][0]; y2 = points[2][1]
    x3 = points[1][0]; y3 = points[1][1]
    x4 = points[3][0]; y4 = points[3][1]

    m1 = np.array([[x1*y2-x2*y1, x1-x2],[x3*y4-x4*y3, x3-x4]])
    m2 = np.array([[y2-y1, x1-x2],[y4-y3, x3-x4]])
    m3 = np.array([[y2-y1, x1*y2-x2*y1],[y4-y3, x3*y4-x4*y3]])
    m4 = np.array([[y2-y1, x1-x2],[y4-y3, x3-x4]])
    
    x_inter = np.linalg.det(m1)/np.linalg.det(m2)
    y_inter = np.linalg.det(m3)/np.linalg.det(m4)
    
    return (x_inter, y_inter)


def meetpoint(*args, dist=2000, fairness=1.0):
    "Function to obtain the midpoint or mid points

    Args:
        *points: earch arg should be a point (tuple point)
        dist (int, optional): distance from point to search pois. Defaults to 2000.
        fairness (float, optional): unbalanced search. Defaults to 1.0.
    "
    in_points = args[0]
    points = []
    for p in in_points:
        points.append(np.array(p))
    
    N = len(points)
    
    if N < 2:
        print('N<2')
        result = points[0]
    
    elif N == 2:
        print('N==2')
        result = midpoint(points[0], points[1])
    
    elif N == 3:
        print('N==3')
        result = three_points_intersection(points[0], points[1], points[2])
    
    else:
        print(f'N={N}')
        new_points = points_reduction_to_three(points)
        result = meetpoint(new_points, dist=dist, fairness=fairness)
        
    return result
        
        

        
        
def points_reduction_to_three(*args):
    in_points = args[0]
    N = len(in_points)
    if N > 3:
        points = {}
        distance = {}
        for i, arg in enumerate(in_points):
            points[f'{i}'] = arg
        for i in range(N):
            for j in range(i+1, N):
                distance[f"{i}-{j}"] = np.linalg.norm(points[f'{i}'] - points[f'{j}'])
        min_val = np.inf
        for key, val in distance.items():
            if val < min_val:
                min_val = val
                min_key = key
        # as i < j always when we detect the min distance, the new point will replace the i value and the j will be deleted to create new dict
        i_point = min_key.split('-')[0]
        j_point = min_key.split('-')[1]
        points[f'{i_point}'] = midpoint(points[f'{i_point}'],points[f'{j_point}'])
        del points[f'{j_point}']
        
        result = points_reduction_to_three(np.array(list(points.values())))    
    
    else:
        result = in_points.copy()
        
    return result

"""

    
def distance_from_ref(name, point, ref_point):
    print(f'dist {name}: {distance(point, ref_point)}')
    
def distance(p1, p2):
    p1_ = np.array(p1)
    p2_ = np.array(p2)
    return np.linalg.norm(p2_ - p1_)

def fairness(*args):
    
    total = np.sum(args)
    N = len(args)
    
    dist = []
    
    for arg in args:
        dist.append(arg/total*N)
        
    return dist      

def mean_location(coords_df):
    x = 0.0
    y = 0.0
    z = 0.0

    for i, coord in coords_df.iterrows():
        latitude = math.radians(coord['Latitude'])
        longitude = math.radians(coord['Longitude'])

        x += math.cos(latitude) * math.cos(longitude)
        y += math.cos(latitude) * math.sin(longitude)
        z += math.sin(latitude)

    total = len(coords_df)

    x = x / total
    y = y / total
    z = z / total

    central_longitude = math.atan2(y, x)
    central_square_root = math.sqrt(x * x + y * y)
    central_latitude = math.atan2(z, central_square_root)

    mean_location_ = {
        'latitude': math.degrees(central_latitude),
        'longitude': math.degrees(central_longitude)
        }
        
    return (mean_location_['latitude'], mean_location_['longitude'])

def get_pois(center_point, tags, distance=2000, count=0):
    if count > 10:
        print(f'{tags} not found!')
        return None
    try:
        gdf_pois = ox.features_from_point(center_point, tags=tags, dist=distance)[['geometry','name']]
        pois = gdf_pois[gdf_pois['name'].notna()].loc[('node',)]
        coords = pois.get_coordinates(ignore_index=True)
        names = pois['name'].values
        coords['name'] = names
        
        result = coords.rename(columns={'x':'Longitude', 'y': 'Latitude'})
        
    
    except Exception:#KeyError or osmnx._errors.InsufficientResponseError:
        
        result = get_pois(center_point, tags, distance=distance+1000, count=count+1)
        
    return result


if __name__=='__main__':
    
    # testing meetpoint

    # mp = meetpoint([(0,1),(1,0),(0,0),(-1,0),(2,0), (2,2)])
    pass
