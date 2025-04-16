import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import random
import tempfile
import os

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

# Generate control points
def generate_random_control_points(n=12):
    return np.array([[random.uniform(-5, 5) for _ in range(3)] for _ in range(n)])

# Generate and save animation as GIF
def generate_animation_gif():
    control_points = generate_random_control_points(12)
    bezier = Bezier3D(control_points, [0])
    t_vals = np.linspace(0, 1, 100)
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

    all_points = np.concatenate(layered_curves)
    center = np.mean(all_points, axis=0)
    margin = 1
    base_xlim = (np.min(all_points[:, 0]) - margin, np.max(all_points[:, 0]) + margin)
    base_ylim = (np.min(all_points[:, 1]) - margin, np.max(all_points[:, 1]) + margin)
    base_zlim = (np.min(all_points[:, 2]) - margin, np.max(all_points[:, 2]) + margin)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')

    draw_frames = len(layered_curves)
    orbit_frames = 90
    total_frames = draw_frames + orbit_frames

    def ease_in_out(t):
        return 0.5 - 0.5 * np.cos(np.pi * t)

    def update(frame):
        ax.cla()
        ax.axis('off')
        if frame < draw_frames:
            zoom_factor = 1.0
        else:
            orbit_progress = (frame - draw_frames) / orbit_frames
            eased = ease_in_out(orbit_progress)
            zoom_factor = 1 + 0.25 * np.sin(eased * 2 * np.pi)

        xlim = center[0] + (np.array(base_xlim) - center[0]) * zoom_factor
        ylim = center[1] + (np.array(base_ylim) - center[1]) * zoom_factor
        zlim = center[2] + (np.array(base_zlim) - center[2]) * zoom_factor

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_zlim(zlim)
        ax.set_box_aspect([1, 1, 1])

        if frame < draw_frames:
            for i in range(frame + 1):
                ax.plot(layered_curves[i][:, 0], layered_curves[i][:, 1], layered_curves[i][:, 2],
                        lw=0.08, color='0.2')
        else:
            for curve in layered_curves:
                ax.plot(curve[:, 0], curve[:, 1], curve[:, 2], lw=0.08, color='0.2')

            progress = (frame - draw_frames) / orbit_frames
            azim = 360 * progress
            elev = 30 + 15 * np.sin(2 * np.pi * progress)
            ax.view_init(elev=elev, azim=azim)

        return []

    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix='.gif')
    ani = FuncAnimation(fig, update, frames=total_frames, blit=False)
    ani.save(tmpfile.name, writer='pillow', fps=20)
    return tmpfile.name

# --- STREAMLIT UI ---
st.title("✨ Bezier Shell Sculpture")

if st.button("🎬 Generate Sculpture"):
    with st.spinner("Rendering..."):
        gif_path = generate_animation_gif()
    st.success("Done! Here it is:")
    st.image(gif_path, caption="Animated Bezier Sculpture", use_column_width=True)
