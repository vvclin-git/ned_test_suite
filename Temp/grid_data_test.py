#%%

import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import numpy as np
from scipy.spatial import Voronoi
from scipy.spatial import voronoi_plot_2d
from scipy.spatial import KDTree

# pick_list = np.load('coords.npy').tolist()
# mtf_vals = np.load('mtf_vals.npy').tolist()
# pattern_size = np.array((50, 50))

mesh_dim = np.array((32, 18))
fov_dim = np.array((1950, 1116))
fov_anchor = np.array((124, 66))
grid_x = np.linspace(fov_anchor[0] + 25, fov_dim[0] + fov_anchor[0] + 25, mesh_dim[0])
grid_y = np.linspace(fov_anchor[1] + 25, fov_dim[1] + fov_anchor[1] + 25, mesh_dim[1])
grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
grid_coords = np.vstack((grid_xx.flatten(), grid_yy.flatten())).T
# points = np.zeros((len(pick_list), 2))
# values = np.zeros((len(pick_list), 1))
# for i, p in enumerate(pick_list):
#     points[i, :] = (p[0:2] + pattern_size * 0.5).astype('uint')
#     values[i] = mtf_vals[i]
# grid_z0 = griddata(points, values, (grid_xx, grid_yy), method='nearest', fill_value=0)

# plt.imshow(grid_z0, extent=(fov_anchor[0], fov_anchor[0]+fov_dim[0], fov_anchor[1]+fov_dim[1], fov_anchor[1]), origin='upper')


pick_list = np.load('coords.npy')
mtf_vals = np.load('mtf_vals.npy')
pattern_size = np.array((50, 50))
coords = pick_list[:, 0:2] + pattern_size * 0.5

fig, axes = plt.subplots()
ax = axes
ax.scatter(x=coords[:, 0], y=coords[:, 1], c=mtf_vals[:])
# ax.scatter(x=(grid_xx.flatten() + 25), y=(grid_yy.flatten() + 25), c='red')
# ax.scatter(x=(grid_coords[:, 0]), y=(grid_coords[:, 1]), c='red')

coords_kdtree = KDTree(coords)

for i in range(mesh_dim.cumprod()[1]):
    dist, _=coords_kdtree.query((grid_coords[i, 0], grid_coords[i, 1]))
    if dist > 25:
        ax.scatter(x=(grid_coords[i, 0]), y=(grid_coords[i, 1]), c='red')
        coords = np.append(coords, np.atleast_2d(grid_coords[i, :]), axis=0)
        mtf_vals = np.append(mtf_vals, np.atleast_1d(0), axis=0)

plt.show()

fig, ax = plt.subplots()
for i in range(mtf_vals.size):
    if mtf_vals[i] !=0:
        ax.scatter(x=coords[i, 0], y=coords[i, 1], c=mtf_vals[i])
    else:
        ax.scatter(x=coords[i, 0], y=coords[i, 1], c='red')
plt.show()
#%%
print(vor.point_region)
# %%
