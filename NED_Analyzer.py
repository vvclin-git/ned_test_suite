
import cv2
from cv2 import COLOR_GRAY2RGB
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import time
from scipy import signal
from mpl_toolkits.mplot3d import Axes3D



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

class ROI():
    def __init__(self, roi_coord, roi_shape, camera_eff, sensor_size, pixel_size, weight):               
        
        self.roi_coord = np.array(roi_coord)
        self.shape = np.array(roi_shape)
        self.sensor_size = np.array(sensor_size)
        self.pt1 = self.roi_coord - (self.shape * 0.5).astype('int')
        self.pt2 = self.roi_coord + (self.shape * 0.5).astype('int')        
        self.weight = weight
        
        pixel_size = np.array(pixel_size)
        
        sensor_center_coord_real = (self.sensor_size * 0.5)
        self.roi_coord_real = self.roi_coord * pixel_size - sensor_center_coord_real
        self.roi_dist_real = np.linalg.norm(self.roi_coord_real)
        self.alpha = np.arctan(self.roi_dist_real / camera_eff)
        if self.roi_coord_real[0] > 0 and self.roi_coord_real[1] > 0:
            self.phi = np.arctan(self.roi_coord_real[0] / self.roi_coord_real[1])
        elif self.roi_coord_real[0] > 0 and self.roi_coord_real[1] == 0:
            self.phi = np.pi * 0.5
        elif self.roi_coord_real[0] > 0 and self.roi_coord_real[1] < 0:
            self.phi = np.pi + np.arctan(self.roi_coord_real[0] / self.roi_coord_real[1])
        elif self.roi_coord_real[0] <= 0 and self.roi_coord_real[1] < 0:
            self.phi = np.pi + np.arctan(self.roi_coord_real[0] / self.roi_coord_real[1])
        elif self.roi_coord_real[0] < 0 and self.roi_coord_real[1] == 0:
            self.phi = np.pi * 1.5
        elif self.roi_coord_real[0] <= 0 and self.roi_coord_real[1] > 0:
            self.phi = 2 * np.pi + np.arctan(self.roi_coord_real[0] / self.roi_coord_real[1])


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
        self.extracted_pts_count = None
        self.std_grid_pts_count = None    
        self.dist_rel = None
        self.dist_diff = None
    
    def std_grid_gen(self, chart_res, grid_dim, padding):    
        chart_res = np.array(chart_res).astype('uint')
        grid_dim = np.array(grid_dim).astype('uint')
        padding = np.array(padding).astype('uint')
        grid_x = np.linspace(0 + padding[0], chart_res[0] - padding[0], grid_dim[0]) 
        grid_y = np.linspace(0 + padding[1], chart_res[1] - padding[1], grid_dim[1])
        grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
        grid_pitch = (chart_res - 2 * padding) / (grid_dim - 1)
        output_msg = f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, '
        output_msg += f'{grid_dim[0] * grid_dim[1]} points\n'
        output_msg += f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}'
        # print(f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}')
        # chart_im = np.zeros((chart_res[1], chart_res[0], 3))
        grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')        
        # for i in range(len(grid_coords)):
        #     cv2.circle(chart_im, (grid_coords[i, 0], grid_coords[i, 1]), marker_size, (255, 255, 255), -1)
        self.std_grid = Grid(grid_coords, grid_dim)
        self.std_grid.sorted = True
        self.grid_dim = grid_dim
        self.std_grid_pts_count = int(grid_dim[0] * grid_dim[1])
        return output_msg   
    
    def img_grid_extract(self, thresh_low, thresh_high, blur_kernel):
        _, thresh = cv2.threshold(self.raw_img, thresh_low, thresh_high, cv2.THRESH_BINARY)
        # print(thresh.shape)
        # print(blur_kernel)
        self.thresh = cv2.medianBlur(thresh, blur_kernel)
        _, labels, stat, centroids = cv2.connectedComponentsWithStats(self.thresh, connectivity=8)
        labels[labels > 0] = 255
        labels_out = np.stack((np.zeros_like(labels), labels, self.thresh), -1)
        self.labeled_img = labels_out                
        self.extracted_pts_count = len(centroids) - 1
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
            output_msg = 'The grid must be sorted first'
            return output_msg
        self.dist_grid.normalize()
        self.std_grid.normalize()
        std_center_dist = self.std_grid.get_pt_dist(self.std_grid.coords[self.dist_grid.center_ind].squeeze())
        dist_center_dist = self.dist_grid.get_pt_dist(self.dist_grid.coords[self.dist_grid.center_ind].squeeze())
        dist_diff = dist_center_dist - std_center_dist
        out = np.zeros_like(std_center_dist)
        np.divide(dist_diff, std_center_dist, out=out, where=std_center_dist!=0)
        # dist_rel = dist_diff / std_center_dist
        dist_rel = out
        self.dist_rel = dist_rel
        self.dist_diff = dist_diff
        output_msg = f'Max relative distortion: {(np.nanmax(abs(dist_rel)) * 100)} %\n'
        output_msg += f'Max absolute distortion: {np.max(abs(dist_diff))} %'
        return output_msg

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



class Grille_Eval():
    def __init__(self):        
        self.raw_img = None        
        self.labeled_img = None        
        
        self.img_roi_size = None
        self.grille_mc = None
        self.roi_grid_coords = None
    
    def gen_mc_grid(self, fov_anchor, fov_size, grid_dim):        
        fov_anchor = np.array(fov_anchor).astype('uint')
        fov_size = np.array(fov_size).astype('uint')
        grid_dim = np.array(grid_dim).astype('uint')
        self.img_roi_size = (fov_size / grid_dim).astype('uint')
        # roi_grid_shape = (fov_size / self.img_roi_size).astype('uint')
        roi_grid_x = np.linspace(fov_anchor[0],fov_anchor[0] + fov_size[0], grid_dim[0], endpoint=False, dtype='uint')
        roi_grid_y = np.linspace(fov_anchor[1], fov_anchor[1] + fov_size[1], grid_dim[1], endpoint=False, dtype='uint')

        roi_grid_xx, roi_grid_yy = np.meshgrid(roi_grid_x, roi_grid_y)
        self.roi_grid_coords = np.vstack((roi_grid_xx.flatten(), roi_grid_yy.flatten())).transpose()

        self.grille_mc = np.zeros((grid_dim[1], grid_dim[0]))

        for i, c in enumerate(self.roi_grid_coords):
            cv2.rectangle(self.labeled_img, c, c + self.img_roi_size, (0, 255, 0), 1)            
            # cv2.imwrite(roi_path + f'ROI_{i}.png', roi)                
        output_msg = f'Grille Contrast Merit Grid Generated\n'
        output_msg += f'FoV Anchor: ({fov_anchor[0]}, {fov_anchor[1]}), FoV Size: {fov_size[0]}x{fov_size[1]}\n'
        output_msg += f'Grid Dimension: {grid_dim[0]}x{grid_dim[1]}, Cell Size: {self.img_roi_size[0]}x{self.img_roi_size[1]}\n'
        return output_msg

    def grille_eval(self):
        if self.roi_grid_coords is None:
            output_msg = 'Merit grid not initialized!'
            return output_msg
        else:
            for i, c in enumerate(self.roi_grid_coords):
                # cv2.rectangle(self.labeled_img, c, c + self.img_roi_size, (0, 255, 0), 1)
                roi = self.raw_img[c[1]:c[1] + self.img_roi_size[1], c[0]:c[0] + self.img_roi_size[0]]
                mc = self.get_roi_mc(roi)
                self.grille_mc[np.unravel_index(i, self.grille_mc.shape)] = mc
                # cv2.imwrite(roi_path + f'ROI_{i}.png', roi)
            
            output_msg = f'Grille Contrast:\n'
            output_msg += f'Max Value: {self.grille_mc.max()}\n'
            output_msg += f'Min Value: {self.grille_mc.min()}\n'
            return output_msg
        

    def get_roi_mc(self, roi):
        roi_avg = np.average(roi, 0)    
        roi_peaks, _ = signal.find_peaks(roi_avg, height=(np.average(roi_avg)))
        roi_max = np.average(roi_avg[roi_peaks])
        roi_valleys, _ = signal.find_peaks(roi_max - roi_avg, height=(np.average(roi_avg)))
        roi_min = np.average(roi_avg[roi_valleys])
        mc = (roi_max - roi_min) / (roi_max + roi_min)
        return mc    
    

class SMTF_Eval():
    def __init__(self) -> None:
        pass

class Draper_Eval():
    def __init__(self, camera_eff, sensor_res, sensor_size, output_path):        
        self.output_path = output_path
        self.pixel_size = (sensor_size[0] / sensor_res[0], sensor_size[1] / sensor_res[1])        
        self.camera_eff = camera_eff
        self.sensor_size = sensor_size
        self.sensor_res = sensor_res             
        self.alpha_phi_array = None

    def LinePlaneCollision(self, planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6): 
        ndotu = planeNormal.dot(rayDirection)
        if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or line is within plane")    
        w = rayPoint - planePoint
        si = -planeNormal.dot(w) / ndotu
        Psi = w + si * rayDirection + planePoint
        return Psi
    
    def get_proj_pt_phi(self, proj_pt):
        if proj_pt[0] > 0 and proj_pt[1] > 0:
            phi = np.arctan(proj_pt[0] / proj_pt[1])
        elif proj_pt[0] > 0 and proj_pt[1] == 0:
            phi = np.pi * 0.5
        elif proj_pt[0] > 0 and proj_pt[1] < 0:
            phi = np.pi + np.arctan(proj_pt[0] / proj_pt[1])
        elif proj_pt[0] <= 0 and proj_pt[1] < 0:
            phi = np.pi + np.arctan(proj_pt[0] / proj_pt[1])
        elif proj_pt[0] < 0 and proj_pt[1] == 0:
            phi = np.pi * 1.5
        elif proj_pt[0] <= 0 and proj_pt[1] > 0:
            phi = 2 * np.pi + np.arctan(proj_pt[0] / proj_pt[1])
         
        return phi

    def aper_upscaler(self, aper_pts, upscale_multiplr):
        if upscale_multiplr < 2:
            return aper_pts
        else:
            output = np.zeros((aper_pts.shape[0] * 2, aper_pts.shape[1]))
            for i, p in enumerate(aper_pts):
                output[i * 2, :] = p
                output[i * 2 + 1, :] = (aper_pts[i, :] + aper_pts[(i + 1) % aper_pts.shape[0], :]) * 0.5
            return self.aper_upscaler(output.astype('int'),upscale_multiplr - 1)
    
        
    def get_aper_roi(self, aper_pts):
        aper_rois = []
        for p in aper_pts:            
            aper_rois.append(ROI(p[0:2], (1, 1), self.camera_eff, self.sensor_size, self.pixel_size, 1))
            # cv2.drawMarker(img_output, tuple(p[0:2].astype('int')), markerType=cv2.MARKER_TILTED_CROSS, color=(0, 255, 0), markerSize=20) 
        return aper_rois

    
    def init_pupil_image(self, aper_pts):
        
        aper_rois = self.get_aper_roi(aper_pts)
        self.alpha_phi_array = np.zeros((len(aper_rois), 2))
        for i, r in enumerate(aper_rois):
            self.alpha_phi_array[i, 0] = r.phi
            self.alpha_phi_array[i, 1] = r.alpha
        ind = self.alpha_phi_array[:, 0].argsort()
        self.alpha_phi_array = self.alpha_phi_array[ind]
        return
    
    def get_eyebox_aperture_pupil(self, camera_distance, aper_pts):
        
        aper_rois = self.get_aper_roi(aper_pts)           
        
        roi_pts = np.zeros(((len(aper_rois), 3)))
        for i, r in enumerate(aper_rois):
            roi_pts[i, 0:2] = r.roi_coord_real
        roi_pts[:, 2] = camera_distance
        # project outline ROI location onto pupil plane
        camera_point = np.array([0, 0, camera_distance])
        pupil_plane_normal = np.array([0, 0, 1])
        pupil_plane_point = np.array([0, 0, 0])
        proj_pts = np.zeros((len(aper_rois), 3))
        ray_pts = np.zeros((len(aper_rois), 3))
        proj_theta_phi = np.zeros((len(aper_rois), 2))
        for i, r in enumerate(aper_rois):
            ray_point = np.array([*r.roi_coord_real, self.camera_eff + camera_distance])
            ray_pts[i, :] = ray_point
            ray_direction = (camera_point - ray_point) / np.linalg.norm((camera_point - ray_point))
            proj_pts[i, :] = self.LinePlaneCollision(pupil_plane_normal, pupil_plane_point, ray_direction, ray_point, epsilon=1e-6)           
            proj_theta_phi[i, 0] = self.get_proj_pt_phi(proj_pts[i, 0:2])        
        # assign alpha value usign phi of outline ROIs to projected points on pupil plane
        
        proj_theta_phi[:, 1] = np.interp(proj_theta_phi[:, 0], self.alpha_phi_array[:, 0], self.alpha_phi_array[:, 1])
                
        return proj_pts, roi_pts, proj_theta_phi


    
    def get_eyebox_aperture(self, proj_pts, proj_theta_phi, aperture_depth):               
        
        aper_plane_point = np.array([0, 0, aperture_depth])
        aper_plane_normal = np.array([0, 0, 1])
        aper_pts = np.zeros_like(proj_pts)
        for i, p in enumerate(proj_pts):
            r = np.linalg.norm(proj_pts[0:2])
            pd = r / np.tan(proj_theta_phi[i, 1])
            pd_point = np.array([0, 0, pd])
            aper_direction = (pd_point - p) / np.linalg.norm((pd_point - p))
            aper_pts[i, :] = self.LinePlaneCollision(aper_plane_normal, aper_plane_point, aper_direction, p)
        # np.savetxt('proj_coord.csv', proj_pts)
        # np.savetxt('roi_outline_coord.csv', outline_coords_array)
        return aper_pts
    
    def draw_outline_projection(self, ax, view, outline_1_in, outline_2_in, plane_1_alpha, plane_2_alpha, proj_plane_grid):   

        outline_temp = np.zeros((len(outline_1_in) + 1, len(outline_1_in[0])))
        outline_temp[0:len(outline_1_in), :] = outline_1_in
        outline_temp[-1, :] = outline_1_in[0, :]
        outline_1 = outline_temp
        outline_temp = np.zeros((len(outline_2_in) + 1, len(outline_2_in[0])))
        outline_temp[0:len(outline_2_in), :] = outline_2_in
        outline_temp[-1, :] = outline_2_in[0, :]
        outline_2 = outline_temp

        ax.view_init(view[0], view[1])
        proj_plane_size = proj_plane_grid.max() - proj_plane_grid.min()
        proj_distance = abs(outline_2[0][2] - outline_1[0][2])    
        ax.set_box_aspect((proj_plane_size, proj_distance, proj_plane_size))    
        
        xx, yy = np.meshgrid(proj_plane_grid, proj_plane_grid)
        zz_1 = np.ones_like(xx) * outline_1[0][2]
        zz_2 = np.ones_like(xx) * outline_2[0][2]   
        
        ax.plot_surface(xx, zz_1, yy, alpha=plane_1_alpha)    
        ax.plot_surface(xx, zz_2, yy, alpha=plane_2_alpha)   
        
        for i, p in enumerate(outline_1):        
            ax.plot([p[0], outline_2[i, 0]], [p[2], outline_2[i, 2]], [p[1], outline_2[i, 1]], 'r-', lw=0.2)
        ax.plot(outline_1[:, 0], outline_1[:, 2], outline_1[:, 1], 'b--', lw=1)
        ax.plot(outline_2[:, 0], outline_2[:, 2], outline_2[:, 1], 'b--', lw=1)
    
        # plt.savefig(self.output_path + filename, dpi=600)
        return
    
    def draw_eyebox_volume(self, proj_pts, roi_pts, proj_theta_phi, proj_plane_grid, aper_depth_grid, view, alpha):
        
        aper_pts_list = []
        for d in aper_depth_grid:
            aper_pts_list.append(self.get_eyebox_aperture(proj_pts, proj_theta_phi, d))        
        fig = plt.figure()            
        ax = Axes3D(fig)        
        for a in aper_pts_list:
            self.draw_outline_projection(ax, view, proj_pts, a, alpha[1], alpha[2], proj_plane_grid)
        # self.draw_outline_projection(ax, view, roi_pts, proj_pts, alpha[0], alpha[1], proj_plane_grid)
        return aper_pts_list, ax, fig


    



if __name__=='__main__':
    
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
    

    def plot_coords_mesh(title, coords_val, grid_dim, chart_res, vmax, vmin, cmap='viridis'):
        fig, ax = plt.subplots()    
        ax.set_title(title)
        x = np.linspace(0, chart_res[0], grid_dim[0])
        y = np.linspace(0, chart_res[1], grid_dim[1])
        xx, yy = np.meshgrid(x, y)
        coords_val_mesh = coords_val.reshape((grid_dim[1], grid_dim[0]))    
        c = ax.pcolormesh(xx, yy, coords_val_mesh, cmap=cmap, vmax=vmax, vmin=vmin)        
        fig.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
        return fig, ax


    raw_img = cv2.imread('Grille_4px_vertical_Corrected_2.5mm_20211222-12-01-28.png', cv2.IMREAD_GRAYSCALE)
    labeled_img = cv2.cvtColor(raw_img, COLOR_GRAY2RGB)

    grille_eval = Grille_Eval()
    grille_eval.raw_img = raw_img
    grille_eval.labeled_img = labeled_img
    grid_dim = np.array([67, 39])
    fov_anchor = np.array([120, 67])
    fov_size = np.array([2010, 1170])

    grille_eval.gen_mc_grid(fov_anchor, fov_size, grid_dim)
    grille_eval.grille_eval()

    fig, ax = plot_coords_mesh('grille contrast', grille_eval.grille_mc, grille_eval.grid_dim, grille_eval.fov_size, 1, 0)
    plt.show()

    # cv2.imwrite('grille_grid.png', grille_eval.labeled_img)

    # self.raw_img = cv2.imread('Freeform_Image_65x37.png', cv2.IMREAD_GRAYSCALE)
    
    # dist_eval = Distortion_Eval()
    # dist_eval.raw_img = self.raw_img
    # dist_eval.std_grid_gen((2560, 1440), (65, 37), (0, 0))
    # dist_eval.img_grid_extract(25, 255, 5)
    # dist_eval.sort_dist_grid(30, 1.5)
    # dist_eval.draw_coords_index(0.8)
    # cv2.imwrite('indexed_img.png', dist_eval.indexed_img)

    # dist_grid_norm = dist_eval.dist_grid.copy()
    # std_grid_norm = dist_eval.std_grid.copy()
    # dist_grid_norm.normalize()
    # std_grid_norm.normalize()
    # dist_grid_norm.sort(30, 1.5)
    # dist_grid_norm.center_grid(std_grid_norm)

    # dist_eval, dist_diff = dist_eval.dist_eval()
    # cv2.imwrite('labeled_img.png', dist_eval.labeled_img)
    

    

    # coords_compare(dist_grid_norm.coords, std_grid_norm.coords)