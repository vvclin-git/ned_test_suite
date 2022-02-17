#%%

import cv2
import matplotlib.pyplot as plt
import numpy as np
import time

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

def get_grid_coords(thresh):
    _, labels, stat, centroids = cv2.connectedComponentsWithStats(thresh, connectivity=8)
    labels[labels > 0] = 255
    labels_out = np.stack((np.zeros_like(labels), labels, thresh), -1)        
    print(f'{len(centroids)} connected components extracted from the image')
    return centroids, labels_out

def grid_generator(grid_dim, chart_res, marker_size, padding):    
    chart_res = np.array(chart_res).astype('uint')
    grid_dim = np.array(grid_dim).astype('uint')
    padding = np.array(padding).astype('uint')
    grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0]) 
    grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1])
    grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
    grid_pitch = (chart_res - 2 * padding) / (grid_dim - 1)
    print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
    print(f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}')
    chart_im = np.zeros((chart_res[1], chart_res[0], 3))
    grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')
    
    for i in range(len(grid_coords)):
        cv2.circle(chart_im, (grid_coords[i, 0], grid_coords[i, 1]), marker_size, (255, 255, 255), -1)
    
    return Grid(grid_coords, grid_dim), chart_im   


def get_norm_coords(coords):
    centroid_x = np.average(coords[:, 0])
    centroid_y = np.average(coords[:, 1])
    centroid_dist = np.sqrt(np.power((coords[:, 0] - centroid_x), 2) + np.power((coords[:, 1] - centroid_y), 2))
    nearest_pts = coords[centroid_dist.argsort(), :][0:4, :]
    y_dist = abs(nearest_pts[:, 1] - nearest_pts[0, 1])
    x_dist = abs(nearest_pts[:, 0] - nearest_pts[0, 0])
    x_dist.sort()
    y_dist.sort()
    min_x_pitch = np.average(x_dist[2:])
    min_y_pitch = np.average(y_dist[2:])
    # print(f'min X pitch: {min_x_pitch}, min Y pitch: {min_y_pitch}')
    coords_norm = np.zeros_like(coords)
    coords_norm[:, 0] = coords[:, 0] / min_x_pitch
    coords_norm[:, 1] = coords[:, 1] / min_y_pitch
    return coords_norm

def get_nearest_coords(coords):
    centroid_x = np.average(coords[:, 0])
    centroid_y = np.average(coords[:, 1])
    centroid_dist = np.sqrt(np.power((coords[:, 0] - centroid_x), 2) + np.power((coords[:, 1] - centroid_y), 2))
    nearest_pts = coords[centroid_dist.argsort(), :][0:4, :]
    return nearest_pts

def get_coords_center(coords):
    nearest_pts = get_nearest_coords(coords)
    return np.array([np.average(nearest_pts[:, 0]), np.average(nearest_pts[:, 1])])

def draw_coords_index(coords, img_res, pad_ratio):
    coords_dim = (((coords[:, 0].max() - coords[:, 0].min())), ((coords[:, 1].max() - coords[:, 1].min())))    
    scale_factor = (img_res[0] / coords_dim[0] * pad_ratio, img_res[1] / coords_dim[1] * pad_ratio)       
    coords_scaled = np.vstack((coords[:, 0] * scale_factor[0], coords[:, 1] * scale_factor[1])).transpose()    
    coords_scaled_center = np.array([(np.average(coords_scaled[:, 0]), np.average(coords_scaled[:, 1]))])    
    coords_shift = np.array([img_res]) / 2 - coords_scaled_center    
    coords_output = (coords_scaled + np.tile(coords_shift, (len(coords_scaled), 1))).astype('uint')
    img = np.zeros((img_res[1], img_res[0], 3))    
    for i, p in enumerate(coords_output):        
        cv2.putText(img, str(i), (p[0], p[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)
    return img

def get_pt_dist(coords, pt):
    pt_vect = np.tile(pt, (len(coords), 1))
    center_dist = np.sqrt(np.power((coords[:, 0] - pt_vect[:, 0]), 2) + np.power((coords[:, 1] - pt_vect[:, 1]), 2))
    return center_dist

def get_coords_dimension(coords):
    coords_width = coords[:, 0].max() - coords[:, 0].min()
    coords_height = coords[:, 1].max() - coords[:, 1].min()
    return coords_width, coords_height

def coords_compare(coords_1, coords_2):
    fig, ax = plt.subplots()
    coords_1 = np.atleast_2d(coords_1)
    coords_2 = np.atleast_2d(coords_2)
    ax.scatter(coords_1[:, 0], coords_1[:, 1], marker='x', s=1.5, c='red', linewidths=0.3, label='coords_1')
    ax.scatter(coords_2[:, 0], coords_2[:, 1], marker='o', s=1, c='blue', linewidths=0.3, label='coords_2')
    # ax.legend()
    fig.legend(loc='upper center', ncol=2)
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    plt.show()
    return fig, ax

def plot_coords_mesh(coords_val, grid_dim, chart_res, vmax, vmin, cmap='viridis'):
    fig, ax = plt.subplots()    
    x = np.linspace(0, chart_res[0], grid_dim[0])
    y = np.linspace(0, chart_res[1], grid_dim[1])
    xx, yy = np.meshgrid(x, y)
    coords_val_mesh = coords_val.reshape((grid_dim[1], grid_dim[0]))    
    c = ax.pcolormesh(xx, yy, coords_val_mesh, cmap=cmap, vmax=vmax, vmin=vmin)        
    fig.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
    return fig, ax

def dist_eval(eval_grid, std_grid):
    if not (eval_grid.sorted and std_grid.sorted):
        print('The grid must be sorted first')
        return None
    eval_grid.normalize()
    std_grid.normalize()
    std_center_dist = std_grid.get_pt_dist(std_grid.coords[eval_grid.center_ind].squeeze())
    dist_center_dist = eval_grid.get_pt_dist(eval_grid.coords[eval_grid.center_ind].squeeze())
    dist_diff = dist_center_dist - std_center_dist
    dist_rel = dist_diff / std_center_dist
    print(f'Max relative distortion: {(np.nanmax(abs(dist_rel)) * 100)} %')    
    print(f'Max absolute distortion: {np.max(abs(dist_diff))}')
    return dist_rel, dist_diff



input_path = '.\\20211202\\Input\\'
output_path = '.\\20211202\\Output\\'
#%% Test Pattern Generation
timestr = time.strftime("%Y%m%d-%H-%M-%S")
grid_dimension = (65, 37)
chart_resolution = (2560, 1440)
padding = (0, 0)
marker_size = 10

std_grid, chart_im = grid_generator(grid_dimension, chart_resolution, 10, padding)

#%% Extract Grid Coordinate from Image (Distorted Image)

dist_angle = 30
max_ratio = 1.5

filename = 'Freeform_Image_65x37.png'
img = cv2.imread(input_path + filename, cv2.IMREAD_GRAYSCALE)
# _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
_, thresh = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)
thresh = cv2.medianBlur(thresh, 5)

dist_coords, labeled_im = get_grid_coords(thresh)
dist_grid = Grid(dist_coords[1:, :], grid_dimension)
dist_grid.sort(dist_angle, max_ratio)

# img = draw_coords_index(dist_grid.coords, (2560, 1440), 0.8)
# cv2.imwrite(output_path + 'dist_norm_sorted.png', img)


#%% Extract Grid Coordinate from Image (Corrected Image 1)

dist_angle = 30
max_ratio = 1.5

filename = 'Freeform_Image_65x37_Corrected_OD.png'
img = cv2.imread(input_path + filename, cv2.IMREAD_GRAYSCALE)
# _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
_, thresh = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)
thresh = cv2.medianBlur(thresh, 5)

crr_coords_1, labeled_im = get_grid_coords(thresh)
crr_grid_1 = Grid(crr_coords_1[1:, :], grid_dimension)
crr_grid_1.sort(dist_angle, max_ratio)

# img = draw_coords_index(dist_grid.coords, (2560, 1440), 0.8)
# cv2.imwrite('dist_norm_sorted.png', img)

#%% Extract Grid Coordinate from Image (Corrected Image 2)

dist_angle = 30
max_ratio = 1.5

filename = 'Freeform_Image_65x37_Corrected_SYNOPSYS.png'
img = cv2.imread(input_path + filename, cv2.IMREAD_GRAYSCALE)
# _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
_, thresh = cv2.threshold(img, 25, 255, cv2.THRESH_BINARY)
thresh = cv2.medianBlur(thresh, 5)

crr_coords_2, labeled_im = get_grid_coords(thresh)
crr_grid_2 = Grid(crr_coords_2[1:, :], grid_dimension)
crr_grid_2.sort(dist_angle, max_ratio)

#%% Distortion Analysis (Distorted Image)

dist_rel, dist_diff = dist_eval(dist_grid, std_grid)
top_dist_rel_ind = np.argsort(-1 * abs(dist_rel))[0:10]
top_dist_diff_ind = np.argsort(-1 * abs(dist_diff))[0:10]


fig, _ = plot_coords_mesh((dist_rel) * 100, grid_dimension, chart_resolution, 5, -5, 'coolwarm')
fig.savefig(output_path + 'distorted_dist_rel.png', dpi=600)
fig, _ = plot_coords_mesh((dist_diff), grid_dimension, chart_resolution, 5, -5, 'coolwarm')
fig.savefig(output_path + 'distorted_dist_diff.png', dpi=600)

coords_compare(dist_grid.coords, dist_grid.coords[top_dist_rel_ind, :])
coords_compare(dist_grid.coords, dist_grid.coords[top_dist_diff_ind, :])
print(dist_rel[top_dist_rel_ind])
print(dist_rel[top_dist_diff_ind])

#%% Distortion Analysis (Corrected Image 1)

dist_rel, dist_diff = dist_eval(crr_grid_1, std_grid)
top_dist_rel_ind = np.argsort(-1 * abs(dist_rel))[0:10]
top_dist_diff_ind = np.argsort(-1 * abs(dist_diff))[0:10]

fig, _ = plot_coords_mesh((dist_rel) * 100, grid_dimension, chart_resolution, 2, -2, 'coolwarm')
fig.savefig(output_path + 'crr_1_dist_rel.png', dpi=600)
fig, _ = plot_coords_mesh((dist_diff), grid_dimension, chart_resolution, 1, -1, 'coolwarm')
fig.savefig(output_path + 'crr_1_dist_diff.png', dpi=600)

coords_compare(crr_grid_1.coords, crr_grid_1.coords[top_dist_rel_ind, :])
coords_compare(crr_grid_1.coords, crr_grid_1.coords[top_dist_diff_ind, :])
print(dist_rel[top_dist_rel_ind])
print(dist_rel[top_dist_diff_ind])


#%% Distortion Analysis (Corrected Image 2)

dist_rel, dist_diff = dist_eval(crr_grid_2, std_grid)
top_dist_rel_ind = np.argsort(-1 * abs(dist_rel))[0:10]
top_dist_diff_ind = np.argsort(-1 * abs(dist_diff))[0:10]

fig, _ = plot_coords_mesh((dist_rel) * 100, grid_dimension, chart_resolution, 2, -2, 'coolwarm')
fig.savefig(output_path + 'crr_2_dist_rel.png', dpi=600)
fig, _ = plot_coords_mesh((dist_diff), grid_dimension, chart_resolution, 1, -1, 'coolwarm')
fig.savefig(output_path + 'crr_2_dist_diff.png', dpi=600)

coords_compare(crr_grid_2.coords, crr_grid_2.coords[top_dist_rel_ind, :])
coords_compare(crr_grid_2.coords, crr_grid_2.coords[top_dist_diff_ind, :])
print(dist_rel[top_dist_rel_ind])
print(dist_rel[top_dist_diff_ind])


# %%
