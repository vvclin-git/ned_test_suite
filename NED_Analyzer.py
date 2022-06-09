
import cv2
from cv2 import COLOR_GRAY2RGB
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from mpl_toolkits.mplot3d import Axes3D
import subprocess
from NED_Types import *

class Distortion_Eval():
    def __init__(self):        
        self.raw_im = None
        self.thresh = None
        self.labeled_im = None
        self.indexed_im = None
        self.std_grid_im = None
        self.std_grid = None
        self.dist_grid = None
        self.grid_dim = None
        self.dist_coords = None
        self.extracted_pts_count = None
        self.std_grid_pts_count = None    
        self.dist_rel = None
        self.dist_diff = None
        self.std_grid_im = None
        
    def std_grid_gen(self, pitch, grid_dim, center_pt):    
        # chart_res = np.array(chart_res).astype('uint')
        grid_dim = np.array(grid_dim).astype('uint')
        # padding = np.array(padding).astype('uint')
        grid_x = np.linspace(0, (grid_dim[0] - 1) * pitch[0], grid_dim[0]) 
        grid_y = np.linspace(0, (grid_dim[1] - 1) * pitch[1], grid_dim[1])
        
        grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)    
        
        output_msg = f'Grid Dimension: {grid_dim[0]} x {grid_dim[1]}, '
        output_msg += f'{grid_dim[0] * grid_dim[1]} points\n'
        output_msg += f'Grid Pitch: {pitch[0]} x {pitch[1]}'
        # # print(f'Grid Pitch: {grid_pitch[0]} x {grid_pitch[1]}')
        # # chart_im = np.zeros((chart_res[1], chart_res[0], 3))
        # self.std_grid_im = np.zeros((chart_res[1], chart_res[0], 3))
        grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).transpose().astype('int')        
        # for i in range(len(grid_coords)):
        #     cv2.circle(chart_im, (grid_coords[i, 0], grid_coords[i, 1]), marker_size, (255, 255, 255), -1)
        self.std_grid = Grid(grid_coords, grid_dim)
        self.std_grid.sorted = True
        self.std_grid.center_ind = self.dist_grid.center_ind        
        self.std_grid_pts_count = int(grid_dim[0] * grid_dim[1])
        std_grid_center_pt = np.array(self.std_grid.get_center_pt())
        shift = np.array(center_pt) - std_grid_center_pt
        self.std_grid.shift_coords(shift)
        if self.std_grid.coords[self.std_grid.coords < 0].size > 0:
            output_msg = 'Negative coordinate detected, check grid center values'
            self.std_grid = None
            return output_msg
        self.grid_dim = grid_dim
        self.std_grid_im = self.labeled_im.copy()
        for i in range(len(self.std_grid.coords)):
            cv2.circle(self.std_grid_im, (self.std_grid.coords[i, 0].astype('uint'), self.std_grid.coords[i, 1].astype('uint')), 5, (255, 0, 0), -1)
        
        return output_msg   


    def img_grid_extract(self, thresh_low, thresh_high, blur_kernel):
        if len(self.raw_im.shape) > 2:
            output_msg = 'Grid extraction failed: only grayscale image is acceptable'
            return output_msg
        norm_im = np.zeros_like(self.raw_im)
        norm_im = cv2.normalize(self.raw_im, norm_im, 255, 0, cv2.NORM_INF)    
        _, thresh = cv2.threshold(norm_im, thresh_low, thresh_high, cv2.THRESH_BINARY)
        # print(thresh.shape)
        # print(blur_kernel)
        self.thresh = cv2.medianBlur(thresh, blur_kernel).astype('uint8')
        _, labels, stat, centroids = cv2.connectedComponentsWithStats(self.thresh, connectivity=8)
        labels[labels > 0] = 255
        labels_out = np.stack((np.zeros_like(labels), labels, self.thresh), -1)
        self.labeled_im = labels_out                
        self.extracted_pts_count = len(centroids) - 1
        self.dist_coords = centroids[1:, :]
        self.dist_coords_bbox = cv2.boundingRect(self.dist_coords.astype('float32'))
        output_msg = f'{self.extracted_pts_count} connected components extracted from the image\n'
        output_msg += f'Bounding Box Anchor: {self.dist_coords_bbox[0]}, {self.dist_coords_bbox[1]}\n'
        output_msg += f'Bounding Box Dimension: {self.dist_coords_bbox[2]}x{self.dist_coords_bbox[3]}\n'       
        
        return output_msg    
    
    def sort_dist_grid(self, dist_angle, max_ratio):
        # self.dist_grid = Grid(self.dist_coords[1:, :], self.grid_dim)
        self.dist_grid = Grid(self.dist_coords[:, :], self.grid_dim)
        self.dist_grid.sort(dist_angle, max_ratio)
        self.dist_coords = self.dist_grid.coords        
        return
    
    def get_center_pts(self):
        if not self.dist_grid.sorted:
            return None
        center_pts = np.atleast_2d(self.dist_grid.coords[self.dist_grid.center_ind].squeeze())
        return center_pts

    def get_center_pt(self):
        if not self.dist_grid.sorted:
            return None
        center_pt = np.atleast_2d(self.dist_grid.coords[self.dist_grid.center_ind].squeeze())
        if center_pt.shape[0] > 1:
            center_pt = np.average(center_pt, axis=0)
        if len(center_pt.shape) > 1:
            center_pt = center_pt.squeeze()
        return center_pt

    def dist_eval(self):                
        if not (self.dist_grid.sorted and self.std_grid.sorted):
            output_msg = 'The grid must be sorted first'
            return output_msg
        # self.dist_grid.normalize()
        # self.std_grid.normalize()
        # center_pt = self.get_center_pt()
        dist_center_pt = self.dist_grid.get_center_pt()
        std_center_pt = self.std_grid.get_center_pt()
        std_center_dist = self.std_grid.get_pt_dist(std_center_pt)
        # dist_center_dist = self.dist_grid.get_pt_dist(dist_center_pt)
        dist_center_dist = self.dist_grid.get_pt_dist(std_center_pt)
        dist_diff = dist_center_dist - std_center_dist
        out = np.zeros_like(std_center_dist)
        np.divide(dist_diff, std_center_dist, out=out, where=std_center_dist!=0)
        # dist_rel = dist_diff / std_center_dist
        dist_rel = out
        self.dist_rel = dist_rel
        self.dist_diff = dist_diff
        output_msg = f'Max relative distortion: {(np.nanmax(abs(dist_rel)) * 100)} %\n'
        output_msg += f'Max absolute distortion: {np.max(abs(dist_diff))}'
        return output_msg

    def draw_coords_index(self, pad_ratio):
        chart_res = (self.raw_im.shape[1], self.raw_im.shape[0])        
        # coords_dim = (((self.dist_coords[:, 0].max() - self.dist_coords[:, 0].min())), ((self.dist_coords[:, 1].max() - self.dist_coords[:, 1].min())))    
        # dist_coords_sorted_bbox = cv2.boundingRect(self.dist_coords.astype('float32'))        
        coords_dim = (self.dist_coords_bbox[2], self.dist_coords_bbox[3])
        scale_factor = (chart_res[0] / coords_dim[0] * pad_ratio, chart_res[1] / coords_dim[1] * pad_ratio)       
        coords_scaled = np.vstack((self.dist_coords[:, 0] * scale_factor[0], self.dist_coords[:, 1] * scale_factor[1])).transpose()    
        coords_scaled_center = np.array([(np.average(coords_scaled[:, 0]), np.average(coords_scaled[:, 1]))])    
        coords_shift = np.array([chart_res]) / 2 - coords_scaled_center    
        coords_output = (coords_scaled + np.tile(coords_shift, (len(coords_scaled), 1))).astype('uint')
        self.indexed_im = np.zeros((chart_res[1], chart_res[0], 3))    
        for i, p in enumerate(coords_output):        
            cv2.putText(self.indexed_im, str(i), (p[0], p[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1, cv2.LINE_AA)
        
        return
    
    def get_center_pitch(self):
        if not self.dist_grid.sorted:
            return None        
        center_pt = self.dist_grid.get_center_pt()
        dist_center_dist = self.dist_grid.get_pt_dist(center_pt)
        center_pts = self.dist_grid.coords[np.argsort(dist_center_dist)].squeeze()[0:4]
        if (self.dist_grid.grid_dim[0] % 2 == 1 and self.dist_grid.grid_dim[1] % 2 == 1):
            x_pitch = max(abs(center_pts[1:4, 0] - center_pts[0, 0]))
            y_pitch = max(abs(center_pts[1:4, 1] - center_pts[0, 1]))
        else:
            x_pitch = center_pts[:, 0].max() - center_pts[:, 0].min()
            y_pitch = center_pts[:, 1].max() - center_pts[:, 1].min()
        return (x_pitch, y_pitch)


class Grille_Eval():
    def __init__(self):        
        self.raw_im = None
        self.preview_im = None        
        self.labeled_im = None        
        
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
        # self.labeled_im = cv2.cvtColor(self.raw_im, cv2.COLOR_GRAY2RGB)
        self.labeled_im = self.preview_im.copy()
        for i, c in enumerate(self.roi_grid_coords):
            cv2.rectangle(self.labeled_im, c, c + self.img_roi_size, (0, 255, 0), 1)            
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
                # cv2.rectangle(self.labeled_im, c, c + self.img_roi_size, (0, 255, 0), 1)
                roi = self.raw_im[c[1]:c[1] + self.img_roi_size[1], c[0]:c[0] + self.img_roi_size[0]]
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
        roi_valleys, _ = signal.find_peaks(roi_max - roi_avg, height=(np.average((roi_max - roi_avg))))
        roi_min = np.average(roi_avg[roi_valleys])
        mc = (roi_max - roi_min) / (roi_max + roi_min)
        if np.isnan(mc):
            mc = 0
        return mc    
    

class SMTF_Eval():
    def __init__(self, roi_path, se_pattern_path):
        
        self.pixel_size = None
        self.threshold = None
        self.mtf_contrast = None
        self.mtf_analysis_options = None
        self.roi_path = roi_path        
        self.se_pattern_path = se_pattern_path
        self.raw_im = None
        self.extracted_im = None
        self.extracted_label_im = None
        self.controller = None
        self.pattern_size = None
        pass
    
    def draw_se_pattern(self, edge_angle, pattern_size, line_type, reverse):    
        chart_im = np.zeros((pattern_size, pattern_size, 3))
        center = (np.array(chart_im.shape[0:2]) * 0.5).astype('uint')
        anchor = center - 0.5 * pattern_size
        pt1 = anchor + np.array([0, pattern_size])
        pt2 = pt1 + np.array([0.5 * pattern_size * (1 - np.tan(np.radians(edge_angle))), 0])
        pt3 = pt2 + np.array([0.5 * pattern_size * (np.tan(np.radians(edge_angle))), -pattern_size])    
        pts = np.array([anchor, pt1, pt2, pt3, anchor]).astype('int32')
        pts = np.expand_dims(pts, axis=1)  
        cv2.fillPoly(chart_im, [pts], color=(255, 255, 255), lineType=line_type)
        if reverse:
            chart_rev_im = np.zeros_like(chart_im)
            chart_rev_im[np.where(chart_im == 0)] = 255
            return chart_rev_im
        return chart_im

    def get_se_patterns(self, edge_angle, pattern_size, line_type, reverse, method, threshold, iou_thresh):
        
        # method = eval('cv2.TM_CCOEFF_NORMED')
        se_pattern_im = self.draw_se_pattern(edge_angle, pattern_size, line_type, reverse)
        self.extracted_im = self.raw_im.copy()
        self.extracted_im = (self.extracted_im // (self.extracted_im.max() / 256 + 1)).astype('uint8')
        self.extracted_label_im = cv2.cvtColor(self.extracted_im, cv2.COLOR_GRAY2RGB)
        stat = cv2.imwrite(self.se_pattern_path + 'se_pattern.png', se_pattern_im)
        se_pattern = cv2.imread(self.se_pattern_path + 'se_pattern.png', cv2.IMREAD_GRAYSCALE)        
        res_se_pattern = cv2.matchTemplate(self.extracted_im, se_pattern, method)       
        
        loc = np.where(res_se_pattern >= threshold)
        loc_value = res_se_pattern[res_se_pattern >= threshold]
        res_box_list = np.zeros((len(loc[0]), 3))
        res_box_list[:, 0] = loc[1]
        res_box_list[:, 1] = loc[0]
        res_box_list[:, 2] = loc_value
        self.res_box_num = len(res_box_list[:, 2])
        self.pick_list = []
        self.nms(res_box_list, iou_thresh, np.array((pattern_size, pattern_size)))
        
        self.controller.msg_box.console('')
        for pt in self.pick_list:
            cv2.rectangle(self.extracted_label_im, (int(pt[0]), int(pt[1])), (int(pt[0]) + pattern_size, int(pt[1]) + pattern_size), (0,255,255), 1)
        
        # cv2.imwrite('labeled.png', self.labeled_img)      
                     
        self.controller.msg_box.console(f'{len(self.pick_list)} SE MTF patterns founded')

    def nms(self, res_box_list, iou_thresh, pattern_size):
        
        if res_box_list.size == 0:
            return 
        else:
                     
            res_box_list = res_box_list[np.argsort(res_box_list[:, 2])[::-1]]
            box1 = res_box_list[0, 0:3]
            self.pick_list.append(box1.astype('uint'))
            for box2 in res_box_list[1:, 0:3]:
                iou, _, _ = self.iou_calc(box1[0:2], box2[0:2], pattern_size)
                if iou > iou_thresh:
                    box2[2] = 0
            box1[2] = 0
            progress = 1 - (res_box_list[:, 0].size / self.res_box_num)
            msg_output = f'{len(self.pick_list)} pattern extracted, progress: {progress: 3.2%}'            
            self.controller.msg_box.console_update(msg_output)
            
            return self.nms(res_box_list[res_box_list[:, 2] > 0], iou_thresh, pattern_size)

    def iou_calc(self, box1, box2, shape):
        x1, y1 = box1[0], box1[1]
        x2, y2 = box2[0], box2[1]
        if abs(x1-x2) >= shape[0] or abs(y1-y2) >= shape[1]:
            return -1, None, None
        x_inter, y_inter = max(x1, x2), max(y1, y2)    
        coord_inter = np.array((x_inter, y_inter))
        shape_inter = np.array((shape[0] - abs(x1-x2), shape[1] - abs(y1-y2)))
        area_inter = shape_inter[0] * shape_inter[1]
        area_union = (shape[0] * shape[1]) * 2 - area_inter
        iou = area_inter / area_union
        return iou, coord_inter, shape_inter
    
    def get_mtf_mesh(self):
        mesh_size = len(self.pick_list)
        self.mtf_value_list = []
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        for i, pt in enumerate(self.pick_list):
            h, w = self.pattern_size, self.pattern_size
            roi_im = self.raw_im[int(pt[1]):pt[1] + w, pt[0]:pt[0] + h]            
            # roi_im = cv2.cvtColor(roi_im, cv2.COLOR_RGB2GRAY)
            stat = cv2.imwrite(self.roi_path + f'roi_{i}.png', roi_im)
            mtf_value = self.mtf_analyzer(f'roi_{i}.png')            
            self.controller.msg_box.console(f'MTF value of ROI {i} at {pt[0]}, {pt[1]}: {mtf_value}')
            self.controller.msg_box.update()           
            self.mtf_value_list.append(mtf_value)
            cv2.putText(self.extracted_label_im, str(mtf_value), (pt[0], pt[1]), fontScale=0.25, thickness=1, fontFace=font, color=(0, 255, 255), lineType=cv2.LINE_AA)
        
    
    
    def set_mtf_analysis_paras(self, pixel_size, threshold, mtf_contrast):
        self.mtf_analysis_paras = ['--single-roi', f'--threshold {threshold}', f'--pixelsize {pixel_size}', f'--mtf {mtf_contrast}', '--esf-sampler line', '-l', '-a']

    def mtf_analyzer(self, roi_filename):
        # print(f'Processing file {roi_filename}...', end='')
        # mtf_analyze = subprocess.run(['mtf_mapper', '--single-roi', '--pixelsize 5', '--mtf 20', '-l', '-a', self.roi_img_path + roi_filename, '.\\'], stdout=subprocess.PIPE)
        mtf_analyze = subprocess.run(['mtf_mapper', *self.mtf_analysis_paras, self.roi_path + roi_filename, '.\\'], stdout=subprocess.PIPE)
        mtf_value = 0
        print(mtf_analyze.stdout.decode('UTF-8').splitlines())
        if len(mtf_analyze.stdout.decode('UTF-8').splitlines()) == 8:
            mtf_report = mtf_analyze.stdout.decode('UTF-8').splitlines()[7]
            try:
                mtf_value = float(mtf_report.split(' ')[14])
                print(f'MTF evaluation completed, value:{mtf_value}...', end='')                
                # store the annotated picture
                output_filename = roi_filename.replace('.png', '_annotated.png')
                subprocess.run(['copy', '.\\annotated.png', self.roi_path + 'annotated\\' + output_filename], shell=True)
                print('Annotated image dumped')                
            except:            
                print(f'MTF evaluation failed!')
                
        return mtf_value 
    
    def set_controller(self, controller):        
        self.controller = controller


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
    
        # plt.savefig(self.output_path + roi_filename, dpi=600)
        return
    
    def draw_eyebox_volume(self, proj_pts, roi_pts, proj_theta_phi, proj_plane_grid, aper_depth_grid, view, alpha):
        
        aper_pts_list = []
        for d in aper_depth_grid:
            aper_pts_list.append(self.get_eyebox_aperture(proj_pts, proj_theta_phi, d))        
        fig = plt.figure()            
        ax = Axes3D(fig)        
        for a in aper_pts_list:
            self.draw_outline_projection(ax, view, proj_pts, a, alpha[1], alpha[2], proj_plane_grid)
        # draw pinhole rays
        # self.draw_outline_projection(ax, view, roi_pts, proj_pts, alpha[0], alpha[1], proj_plane_grid)
        return aper_pts_list, ax, fig

    def draw_eyebox_area(self, aper_pts_list, proj_plane_grid, aper_depth_grid):
        fig, ax = plt.subplots()
        for i, aper_pts in enumerate(aper_pts_list):
            ax.plot([*aper_pts[:, 0], aper_pts[0, 0]], [*aper_pts[:, 1], aper_pts[0, 1]], ls='-', marker='o', markersize=2, label=f'Z={[0, *aper_depth_grid][i]} mm')
        ax.set_xlim(proj_plane_grid.min(), proj_plane_grid.max())
        ax.set_ylim(proj_plane_grid.min(), proj_plane_grid.max())
        ax.set_xticks(proj_plane_grid)
        ax.set_aspect('equal')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.legend(prop={'size': 6})
        ax.grid()
        fig.set_dpi(200)
        return ax, fig
    



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