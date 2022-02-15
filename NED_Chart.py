
import numpy as np
import cv2

class Coords:
    def __init__(self, coords):
        self.coords = coords
        self.orig_coords = coords                
        return      

    def normalize(self):
        centroid = self.get_centroid()
        # centroid_x = np.average(self.coords[:, 0])
        # centroid_y = np.average(self.coords[:, 1])
        centroid_dist = self.get_pt_dist(centroid)
        # centroid_dist = np.sqrt(np.power((self.coords[:, 0] - centroid_x), 2) + np.power((self.coords[:, 1] - centroid_y), 2))
        nearest_pts = self.coords[centroid_dist.argsort(), :][0:4, :]
        y_dist = abs(nearest_pts[:, 1] - nearest_pts[0, 1])
        x_dist = abs(nearest_pts[:, 0] - nearest_pts[0, 0])
        x_dist.sort()
        y_dist.sort()
        min_x_pitch = np.average(x_dist[2:])
        min_y_pitch = np.average(y_dist[2:])        
        coords_norm = np.zeros_like(self.coords)
        coords_norm[:, 0] = self.coords[:, 0] / min_x_pitch
        coords_norm[:, 1] = self.coords[:, 1] / min_y_pitch
        self.coords = coords_norm
        return
    
    def get_dim(self):
        coords_width = self.coords[:, 0].max() - self.coords[:, 0].min()
        coords_height = self.coords[:, 1].max() - self.coords[:, 1].min()
        return np.array([coords_width, coords_height])

    def get_pt_dist(self, pt):
        pt_vect = np.tile(pt, (len(self.coords), 1))
        center_dist = np.sqrt(np.power((self.coords[:, 0] - pt_vect[:, 0]), 2) + np.power((self.coords[:, 1] - pt_vect[:, 1]), 2))
        return center_dist

    def get_centroid(self):
        return np.array([np.average(self.coords[:, 0]), np.average(self.coords[:, 1])])  

    def shift_coords(self, shift):
        self.coords = self.coords + shift
        return

    def get_neighbors(self, pt, coords, max_ratio):        
        coords_dist = self.get_pt_dist(pt)        
        close_neighbhors = coords_dist[coords_dist < coords_dist.min() * max_ratio]
        ind = close_neighbhors.argsort()        
        # neighbors = coords[ind]
        neighbors = close_neighbhors[ind]
        return neighbors

    def scale_coords(self, scale):
        self.coords = self.coords * scale
        return
    
    def restore_coords(self):
        self.coords = self.orig_coords
        return

class Grid(Coords):
    def __init__(self, coords, grid_dim):
        if (grid_dim[0] * grid_dim[1]) != len(coords):
            raise Exception(f"Invalid grid dimension! (grid_dim={grid_dim}, coords length={len(coords)})")    
        super().__init__(coords)
        self.grid_dim = grid_dim
        self.sorted = False
        self.center_ind = None           
    
    def get_next_pt(self, pt, dist_angle, max_ratio):    
        # pt_vect = np.tile(pt, (len(self.coords), 1))
        # coords_dist = np.sqrt(np.power((self.coords[:, 0] - pt_vect[:, 0]), 2) + np.power((self.coords[:, 1] - pt_vect[:, 1]), 2))
        coords_dist = self.get_pt_dist(pt)
        neighbors = self.coords[np.argwhere((coords_dist > 0) & (coords_dist < coords_dist[coords_dist.nonzero()].min() * 1.5))]
        neighbors = neighbors.squeeze()
        pt_vect = np.tile(pt, (len(neighbors), 1))
        neighbors_theta = abs(np.arctan2((neighbors - pt_vect)[:, 1], (neighbors - pt_vect)[:, 0]))    
        next_pt = np.atleast_2d(neighbors[neighbors_theta.argsort()])[0]
        
        if neighbors_theta.min() > np.rad2deg(dist_angle):
            return None
        
        return next_pt

    def sort(self, dist_angle, max_ratio):
        left_col = self.coords[self.coords[:, 0].argsort()[0:self.grid_dim[1]]]
        left_col = left_col[(left_col[:, 1]).argsort()]
        sorted_coords = np.zeros_like(self.coords)
        ind = 0
        for p in left_col:        
            next_pt = p
            for i in range(self.grid_dim[0]):
                sorted_coords[ind] = next_pt                    
                next_pt = self.get_next_pt(next_pt, dist_angle, max_ratio) 
                ind += 1    
        self.coords = sorted_coords
        self.orig_coords = sorted_coords
        self.sorted = True
        
        if self.grid_dim[0] % 2 == 0:
            center_ind_x = np.array([self.grid_dim[0] / 2 - 1, self.grid_dim[0] / 2]).astype('uint')
        else:
            center_ind_x = np.array([int(self.grid_dim[0] / 2)])
        if self.grid_dim[1] % 2 == 0:
            center_ind_y = np.array([self.grid_dim[1] / 2 - 1, self.grid_dim[1] / 2]).astype('uint')
        else:
            center_ind_y = np.array([int(self.grid_dim[1] / 2)])
        center_ind_xx, center_ind_yy = np.meshgrid(center_ind_x, center_ind_y)
        
        self.center_ind = (center_ind_yy * self.grid_dim[0] + center_ind_xx).flatten()
        self.left_ind = (center_ind_yy * self.grid_dim[0]).flatten()
        self.right_ind = (center_ind_yy * self.grid_dim[0] + (self.grid_dim[0] - 1)).flatten()
        self.top_ind = center_ind_xx.flatten()
        self.bottom_ind = ((self.grid_dim[1] - 1) * self.grid_dim[0] + center_ind_xx).flatten()
        
        return

    def get_center_dim(self):
        center_width = abs(np.average(self.coords[self.right_ind, 0]) - np.average(self.coords[self.left_ind, 0]))
        center_height = abs(np.average(self.coords[self.top_ind, 1]) - np.average(self.coords[self.bottom_ind, 1]))
        return np.array([center_width, center_height])

    def center_grid(self, std_grid):
        if not self.sorted:
            print('Coordinate not indexed!')
            return
        if np.any(std_grid.grid_dim != self.grid_dim):
            raise Exception("Invalid grid dimension!") 

        std_grid_center = np.array([np.average(std_grid.coords[self.center_ind, 0]), np.average(std_grid.coords[self.center_ind, 1])])     
        grid_center = np.array([np.average(self.coords[self.center_ind, 0]), np.average(self.coords[self.center_ind, 1])])        
        
        coords_shift = std_grid_center - grid_center
        self.shift_coords(coords_shift)            
        return

    def copy(self):
        return Grid(self.coords, self.grid_dim)
    
def gen_circle_grid(chart_res, grid_dim, marker_size, padding):            
    grid_dim = np.array(grid_dim).astype('uint')
    chart_res = np.array(chart_res).astype('uint')
    padding = np.array(padding).astype('uint')
    grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0]) 
    grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1])
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = (chart_res - 2 * padding) / (grid_dim - 1)
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}')
    print(f'Dot Size: {marker_size}')
    print(f'Padding: {padding[0]}x{padding[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 3))
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')
    
    for i in range(len(grid_coords)):
        cv2.circle(chart_im, (grid_coords[i, 0], grid_coords[i, 1]), marker_size, (255, 255, 255), -1)
    
    return chart_im, Grid(grid_coords, grid_dim)

def gen_grille(chart_res, width, orient):
    if orient == 'vertical':
        grid_dim = np.array([chart_res[0] / (width * 2) + 1, 2]).astype('uint')
        grille_size = np.array([width, chart_res[1]])
    elif orient == 'horizontal':
        grid_dim = np.array([2, chart_res[1] / (width * 2) + 1]).astype('uint')
        grille_size = np.array([chart_res[0], width])
    else:
        raise Exception('Invalid orientation (horizontal / vertical)')            
        
    grid_x = np.linspace(0, chart_res[0], grid_dim[0]) 
    grid_y = np.linspace(0, chart_res[1], grid_dim[1])
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = (chart_res) / (grid_dim - 1)
    
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}')
    print(f'Grille Size: {grille_size[0]} x {grille_size[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 1)).astype('uint8')
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')

    for p in grid_coords:
        pt_1 = np.array([p[0], p[1]])
        pt_2 = pt_1 + grille_size - 1
        cv2.rectangle(chart_im, [*pt_1], [*pt_2], (255), -1)
        
    return chart_im, grid_coords

def gen_checkerboard(chart_res, grid_dim, begin_with, padding):
    chart_res = np.array(chart_res).astype('uint')
    padding = np.array(padding).astype('uint')
    grid_dim = np.array(grid_dim).astype('uint')        
    grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0], endpoint=False) 
    grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1], endpoint=False)
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = ((chart_res - 2 * padding) / (grid_dim)).astype('uint')
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Square Size: {grid_pitch[0]} x {grid_pitch[1]}')    
    print(f'Padding: {padding[0]}x{padding[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 3))
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')
    
    fill_val = {'black':0, 'white':255}
    prev_fill = fill_val[begin_with]

    for i, p in enumerate(grid_coords):
        pt_1 = np.array([p[0], p[1]])
        pt_2 = pt_1 + grid_pitch
        # switch between 0 and 1 while filling
        if prev_fill == 0:
            fill_val = 1
        else:
            fill_val = 0
        # continue the filling for grid with even numbered column
        if i % grid_dim[0] == 0 and grid_dim[0] % 2 == 0:
            fill_val = prev_fill
        cv2.rectangle(chart_im, [*pt_1], [*pt_2], ([fill_val * 255] * 3), -1)        
        prev_fill = fill_val
    
    grid_coords = (grid_coords + grid_pitch * 0.5).astype('uint')

    return chart_im, grid_coords

def draw_se_MTF_pattern(chart_im, center, edge_angle, pattern_size, line_type):    
    anchor = center - 0.5 * pattern_size
    pt1 = anchor + np.array([0, pattern_size])
    pt2 = pt1 + np.array([0.5 * pattern_size * (1 - np.tan(np.radians(edge_angle))), 0])
    pt3 = pt2 + np.array([0.5 * pattern_size * (np.tan(np.radians(edge_angle))), -pattern_size])    
    pts = np.array([anchor, pt1, pt2, pt3, anchor]).astype('int32')
    pts = np.expand_dims(pts, axis=1)  
    cv2.fillPoly(chart_im, [pts], color=(255, 255, 255), lineType=line_type)
    return chart_im, None

def gen_se_MTF(chart_res, grid_dim, edge_angle, pattern_size, padding, line_type):
    grid_dim = np.array(grid_dim).astype('uint')        
    chart_res = np.array(chart_res).astype('uint')
    padding = np.array(padding).astype('uint')
    grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0], endpoint=False) 
    grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1], endpoint=False)
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = ((chart_res - 2 * padding) / (grid_dim)).astype('uint')
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Square Size: {grid_pitch[0]} x {grid_pitch[1]}')    
    print(f'Padding: {padding[0]}x{padding[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 3), dtype='uint8')
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')
    grid_coords = (grid_coords + np.array([pattern_size * 0.5, pattern_size * 0.5])).astype('uint')
    
    for p in grid_coords:
        chart_im, _ = draw_se_MTF_pattern(chart_im, p, edge_angle, pattern_size, line_type)    

    return chart_im, grid_coords



def gen_reticle(chart_res, color, cross_size, marker_size, thickness):
    chart_im = np.zeros((chart_res[1], chart_res[0], 3))
    # Center
    cv2.drawMarker(chart_im, np.array([chart_res[0] * 0.5, chart_res[1] * 0.5], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=cross_size, thickness=thickness)
    # Left Top
    center = (np.array([0, 0]) + np.array([marker_size * 0.5, marker_size * 0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([0, 0], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Left Center
    center = (np.array([0, chart_res[1] * 0.5]) + np.array([marker_size * 0.5, 0])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([0, chart_res[1] * 0.5], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Left Bottom
    center = (np.array([0, chart_res[1]]) + np.array([marker_size * 0.5, marker_size * -0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([0, chart_res[1]], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Center Top
    center = (np.array([chart_res[0] * 0.5, 0]) + np.array([0, marker_size * 0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0] * 0.5, 0], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Center Bottom
    center = (np.array([chart_res[0] * 0.5, chart_res[1]]) + np.array([0, marker_size * -0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0] * 0.5, chart_res[1]], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Right Top
    center = (np.array([chart_res[0], 0]) + np.array([marker_size * -0.5, marker_size * 0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0], 0], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Right Center
    center = (np.array([chart_res[0], chart_res[1] * 0.5]) + np.array([marker_size * -0.5, 0])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0], chart_res[1] * 0.5], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    # Right Botoom
    center = (np.array([chart_res[0], chart_res[1]]) + np.array([marker_size * -0.5, marker_size * -0.5])).astype('uint')
    cv2.circle(chart_im, center, int(marker_size * 0.5), color=color, thickness=thickness)
    # cv2.drawMarker(chart_im, np.array([chart_res[0], chart_res[1]], dtype='uint'), markerType=cv2.MARKER_TILTED_CROSS, color=color, markerSize=size, thickness=thickness)
    return chart_im, None

# def gen_reticle(chart_res, rect_color, cross_color, thickness, filled):
#     chart_im = np.zeros((chart_res[1], chart_res[0], 3))
#     pt1 = (np.array([0, 0]) + thickness * 0.5).astype('uint')
#     pt2 = (chart_res - thickness * 0.5).astype('uint')
#     if filled:
#         cv2.rectangle(chart_im, pt1, pt2, color=rect_color, thickness=-1)
#     else:
#         cv2.rectangle(chart_im, pt1, pt2, color=rect_color, thickness=thickness)
#     cv2.line(chart_im, np.array([0, chart_res[1] * 0.5], dtype='uint'), np.array([chart_res[0], chart_res[1] * 0.5], dtype='uint'), color=cross_color, thickness=thickness)
#     cv2.line(chart_im, np.array([chart_res[0] * 0.5, 0], dtype='uint'), np.array([chart_res[0] * 0.5, chart_res[1]], dtype='uint'), color=cross_color, thickness=thickness)
#     return chart_im

if __name__ == '__main__':

    chart_res = np.array([2560, 1440])
    chart_im = gen_reticle(chart_res, (0, 255, 0), 8)
    cv2.imwrite('reticle_test.bmp', chart_im)
    grid_dim = np.array([16, 9])
    padding = np.array([0, 0])

    chart_coords, chart_im = gen_se_MTF(chart_res, grid_dim, 11.25, 100, padding, cv2.LINE_8)

    cv2.imwrite('se_MTF_test_20220104.png', chart_im)

    for p in chart_coords:
        p1 = p - np.array([50, 50])
        p2 = p + np.array([50, 50])
        cv2.rectangle(chart_im, p1, p2, color=(0, 255, 0), thickness=5)

    cv2.imwrite('se_MTF_annotated_20220104.png', chart_im)


