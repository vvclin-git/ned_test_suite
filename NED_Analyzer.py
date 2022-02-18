
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




class Distortion_Eval():
    def __init__(self):        
        self.raw_img = None
        self.thresh = None
        self.labeled_img = None
        self.indexed_img = None
        self.std_grid = None
        self.dist_grid = None
        self.grid_dim = None
        self.dist_coords = None
        self.extracted_pts_count = 0    
    
    def std_grid_gen(self, chart_res, grid_dim, padding):    
        chart_res = np.array(chart_res).astype('uint')
        grid_dim = np.array(grid_dim).astype('uint')
        padding = np.array(padding).astype('uint')
        grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0]) 
        grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1])
        grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
        grid_pitch = (chart_res - 2 * padding) / (grid_dim - 1)
        # print(f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, ', end='')
        # print(f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}')
        # chart_im = np.zeros((chart_res[1], chart_res[0], 3))
        grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')        
        # for i in range(len(grid_coords)):
        #     cv2.circle(chart_im, (grid_coords[i, 0], grid_coords[i, 1]), marker_size, (255, 255, 255), -1)
        self.std_grid = Grid(grid_coords, grid_dim)
        self.std_grid.sorted = True
        self.grid_dim = grid_dim
        return    
    
    def img_grid_extract(self, thresh_low, thresh_high, blur_kernel):
        _, thresh = cv2.threshold(self.raw_img, thresh_low, thresh_high, cv2.THRESH_BINARY)
        self.thresh = cv2.medianBlur(thresh, blur_kernel)
        _, labels, stat, centroids = cv2.connectedComponentsWithStats(self.thresh, connectivity=8)
        labels[labels > 0] = 255
        labels_out = np.stack((np.zeros_like(labels), labels, self.thresh), -1)
        self.labeled_img = labels_out                
        self.extracted_pts_count = len(centroids)
        self.dist_coords = centroids
        output_msg = f'{self.extracted_pts_count} connected components extracted from the image'        
        print(output_msg)
        return output_msg    
    
    def sort_dist_grid(self, dist_angle, max_ratio):
        self.dist_grid = Grid(self.dist_coords[1:, :], self.grid_dim)
        self.dist_grid.sort(dist_angle, max_ratio)
        self.dist_coords = self.dist_grid.coords
        return

    def dist_eval(self):                
        if not (self.dist_grid.sorted and self.std_grid.sorted):
            print('The grid must be sorted first')
            return None
        self.dist_grid.normalize()
        self.std_grid.normalize()
        std_center_dist = self.std_grid.get_pt_dist(self.std_grid.coords[self.dist_grid.center_ind].squeeze())
        dist_center_dist = self.dist_grid.get_pt_dist(self.dist_grid.coords[self.dist_grid.center_ind].squeeze())
        dist_diff = dist_center_dist - std_center_dist
        out = np.zeros_like(std_center_dist)
        np.divide(dist_diff, std_center_dist, out=out, where=std_center_dist!=0)
        # dist_rel = dist_diff / std_center_dist
        dist_rel = out
        print(f'Max relative distortion: {(np.nanmax(abs(dist_rel)) * 100)} %')    
        print(f'Max absolute distortion: {np.max(abs(dist_diff))}')
        return dist_rel, dist_diff

    def draw_coords_index(self, pad_ratio):
        chart_res = (self.raw_img.shape[1], self.raw_img.shape[0])        
        coords_dim = (((self.dist_coords[:, 0].max() - self.dist_coords[:, 0].min())), ((self.dist_coords[:, 1].max() - self.dist_coords[:, 1].min())))    
        scale_factor = (chart_res[0] / coords_dim[0] * pad_ratio, chart_res[1] / coords_dim[1] * pad_ratio)       
        coords_scaled = np.vstack((self.dist_coords[:, 0] * scale_factor[0], self.dist_coords[:, 1] * scale_factor[1])).transpose()    
        coords_scaled_center = np.array([(np.average(coords_scaled[:, 0]), np.average(coords_scaled[:, 1]))])    
        coords_shift = np.array([chart_res]) / 2 - coords_scaled_center    
        coords_output = (coords_scaled + np.tile(coords_shift, (len(coords_scaled), 1))).astype('uint')
        self.indexed_img = np.zeros((chart_res[1], chart_res[0], 3))    
        for i, p in enumerate(coords_output):        
            cv2.putText(self.indexed_img, str(i), (p[0], p[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)
        return

if __name__=='__main__':
    img = cv2.imread('Freeform_Image_65x37.png', cv2.IMREAD_GRAYSCALE)
    
    dist_eval = Distortion_Eval()
    dist_eval.raw_img = img
    dist_eval.std_grid_gen((2560, 1440), (65, 37), (0, 0))
    dist_eval.img_grid_extract(25, 255, 5)
    dist_eval.sort_dist_grid(30, 1.5)
    dist_eval.draw_coords_index(0.8)
    cv2.imwrite('indexed_img.png', dist_eval.indexed_img)
    dist_eval, dist_diff = dist_eval.dist_eval()
    # cv2.imwrite('labeled_img.png', dist_eval.labeled_img)
# def coords_compare(coords_1, coords_2):
#     fig, ax = plt.subplots()
#     coords_1 = np.atleast_2d(coords_1)
#     coords_2 = np.atleast_2d(coords_2)
#     ax.scatter(coords_1[:, 0], coords_1[:, 1], marker='x', s=1.5, c='red', linewidths=0.3, label='coords_1')
#     ax.scatter(coords_2[:, 0], coords_2[:, 1], marker='o', s=1, c='blue', linewidths=0.3, label='coords_2')
#     # ax.legend()
#     fig.legend(loc='upper center', ncol=2)
#     fig.tight_layout()
#     fig.subplots_adjust(top=0.9)
#     plt.show()
#     return fig, ax

# def plot_coords_mesh(coords_val, grid_dim, chart_res, vmax, vmin, cmap='viridis'):
#     fig, ax = plt.subplots()    
#     x = np.linspace(0, chart_res[0], grid_dim[0])
#     y = np.linspace(0, chart_res[1], grid_dim[1])
#     xx, yy = np.meshgrid(x, y)
#     coords_val_mesh = coords_val.reshape((grid_dim[1], grid_dim[0]))    
#     c = ax.pcolormesh(xx, yy, coords_val_mesh, cmap=cmap, vmax=vmax, vmin=vmin)        
#     fig.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
#     return fig, ax