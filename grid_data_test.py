import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import numpy as np

pick_list = np.load('coords.npy').tolist()
mtf_vals = np.load('mtf_vals.npy').tolist()
pattern_size = np.array((50, 50))

mesh_dim = np.array((32, 18))
fov_dim = np.array((2000, 1166))
fov_anchor = np.array((124, 66))
grid_x = np.linspace(fov_anchor[0], (fov_dim - fov_anchor)[0], mesh_dim[0])
grid_y = np.linspace(fov_anchor[1], (fov_dim - fov_anchor)[1], mesh_dim[1])
grid_xx, grid_yy = np.meshgrid(grid_x, grid_y)
points = np.zeros((len(pick_list), 2))
values = np.zeros((len(pick_list), 1))
for i, p in enumerate(pick_list):
    points[i, :] = (p[0:2] + pattern_size * 0.5).astype('uint')
    values[i] = mtf_vals[i]
grid_z0 = griddata(points, values, (grid_xx, grid_yy), method='nearest', fill_value=0)

plt.imshow(grid_z0, extent=(fov_anchor[0], fov_anchor[0]+fov_dim[0], fov_anchor[1]+fov_dim[1], fov_anchor[1]), origin='upper')


# pick_list = np.load('coords.npy')
# mtf_vals = np.load('mtf_vals.npy')


# plt.scatter(x=pick_list[:, 0], y=pick_list[:, 1], c=mtf_vals[:])
plt.colorbar()
plt.show()