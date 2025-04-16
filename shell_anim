import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import random

# Bezier class
class Bezier:
    def __init__(self, control_points, collapse_axes):
        self.control_points = control_points
        self.collapse_axes = collapse_axes

    def __call__(self, ts):
        t, *ts = ts
        m, *ms = self.collapse_axes
        scp = np.array_split(self.control_points, self.control_points.shape[m], m)
        while len(scp) > 1:
            scp = [self.convolve(t, p, c) for p, c in zip(scp, scp[1:])]
        retv, *_ = scp
        retv = np.squeeze(retv, axis=m)
        if ms:
            ms = [x if x < m else x - 1 for x in ms]
            retv = Bezier(retv, ms)(ts)
        return retv

    def convolve(self, t, a, b):
        return (1 - t) * a + t * b

class Bezier3D(Bezier): pass

def generate_random_control_points(n=12):
    return np.array([[random.uniform(-5, 5) for _ in range(3)] for _ in range(n)])

# Setup
control_points = generate_random_control_points(12)
bezier = Bezier3D(control_points, [0])
t_vals = np.linspace(0, 1, 100)

# Build the shell by rotating the control points
draw_rotations = np.linspace(0, 360, 180)
layered_curves = []

for angle in draw_rotations:
    theta = np.radians(angle)
    rot = np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta),  np.cos(theta), 0],
        [0, 0, 1]
    ])
    rotated = control_points @ rot.T
    bezier_rot = Bezier3D(rotated, [0])
    curve = np.array([bezier_rot([t]) for t in t_vals])
    layered_curves.append(curve)

# Compute bounds
all_points = np.concatenate(layered_curves)
xmin, xmax = np.min(all_points[:, 0]), np.max(all_points[:, 0])
ymin, ymax = np.min(all_points[:, 1]), np.max(all_points[:, 1])
zmin, zmax = np.min(all_points[:, 2]), np.max(all_points[:, 2])
center = np.mean(all_points, axis=0)
margin = 1
base_xlim = (xmin - margin, xmax + margin)
base_ylim = (ymin - margin, ymax + margin)
base_zlim = (zmin - margin, zmax + margin)

# Plot setup
fig = plt.figure(figsize=(19.2, 10.8))
ax = fig.add_subplot(111, projection='3d')

# Frame counts
draw_frames = len(layered_curves)
orbit_frames = 180
total_frames = draw_frames + orbit_frames

# Helper: smooth easing (sinusoidal)
def ease_in_out(t):
    return 0.5 - 0.5 * np.cos(np.pi * t)

# Animation function
def update(frame):
    ax.cla()
    ax.axis('off')

    if frame < draw_frames:
        zoom_factor = 1.0
    else:
        orbit_progress = (frame - draw_frames) / orbit_frames
        eased = ease_in_out(orbit_progress)
        zoom_factor = 1 + 0.25 * np.sin(eased * 2 * np.pi)  # subtle pulsing zoom

    # Apply zoom to limits
    xlim = center[0] + (np.array(base_xlim) - center[0]) * zoom_factor
    ylim = center[1] + (np.array(base_ylim) - center[1]) * zoom_factor
    zlim = center[2] + (np.array(base_zlim) - center[2]) * zoom_factor

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_zlim(zlim)
    ax.set_box_aspect([1, 1, 1])

    if frame < draw_frames:
        # Phase 1: progressive drawing
        for i in range(frame + 1):
            ax.plot(layered_curves[i][:, 0], layered_curves[i][:, 1], layered_curves[i][:, 2],
                    lw=0.08, color='0.2')
    else:
        # Phase 2: orbit the full shape
        for curve in layered_curves:
            ax.plot(curve[:, 0], curve[:, 1], curve[:, 2], lw=0.08, color='0.2')

        # Orbit camera around all angles
        progress = (frame - draw_frames) / orbit_frames
        azim = 360 * progress
        elev = 30 + 15 * np.sin(2 * np.pi * progress)  # up and down
        ax.view_init(elev=elev, azim=azim)

    return []

# Animate and save
ani = FuncAnimation(fig, update, frames=total_frames, blit=False)
ani.save("bezier_sculpture_orbit_smooth.mp4", fps=30, dpi=200, extra_args=['-vcodec', 'libx264'])
