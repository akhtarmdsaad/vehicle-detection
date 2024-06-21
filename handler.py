import math 
def dist(p1,p2) -> float:
    # print(p1,p2)
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 )

class Tracker:
    def __init__(self,rows) -> None: 
        l = [] 
        rows.sort(key=lambda x:x[4],reverse=True)
        for row in rows:
            x1,y1,x2,y2,conf,obj = row
            width = x2-x1 
            height = y2-y1 

            c1 = x1 + width // 2 
            c2 = y1 + height // 2 

            # check whether to accept or reject the rectangle (if its too close)
            add = True 
            for i in l:
                pts = i[-1]
                if dist(pts,(c1,c2)) < 10:
                    add=False 
                    break
            if add:
                l.append((int(x1),int(y1),int(x2),int(y2),int(conf*100),int(obj),(int(c1),int(c2))))
        self.rows = l 
    
    def get_rects(self):
        return [(row[0],row[1],row[2],row[3]) for row in self.rows]
    
    def get_center_points(self):
        return [row[6] for row in self.rows]
    
    def get_objects(self):
        return [row(5) for row in self.rows]


def get_closest_point_dict(l1, l2):
    """
    l1: list of points in previous frame 
    l2: list of points in current frame 

    returns a dictionary where keys are previous points of object and are mapped
    to current points of object
    """
    d = {}
    for i1 in l1:
        min_dist = float("inf")
        min_dist_point = l2[0]
        for i2 in l2:
            if dist(i1,i2) < min_dist:
                min_dist = dist(i1,i2)
                min_dist_point = i2 
        if min_dist < 40:
            d[i1] = min_dist_point
    return d 


"""
                
def get_closest_point_dict_test(l1,l2):
    closest_dict = {}
    i = 0 
    j = 0 
    while i < len(l1):
        point1 = l1[i]
        min_dist = float("inf")     # min dist of point 1 to a point
        min_dist_point = None 
        for index,j in l2:
            d = dist(point1, j)
            if d < min_dist:
                min_dist = d 
                min_dist_point = j 
                min_dist_point_index = index 
        
        l2.pop(min_dist_point_index)

        closest_dict[point1] = min_dist_point
    return closest_dict

"""