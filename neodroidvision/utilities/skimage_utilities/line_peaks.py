from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from skimage import color
from skimage import io
from skimage.draw import line
from skimage.transform import hough_line, hough_line_peaks

if __name__ == "__main__":

    def aushd():
        file = "3.jpg"
        # file = "NdNLO.jpg"
        # image = cv2.imread(str(Path.home() / "Pictures" / file))

        # Constructing test image
        image = color.rgb2gray(io.imread(str(Path.home() / "Pictures" / file)))

        # Classic straight-line Hough transform
        # Set a precision of 0.05 degree.
        tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 3600)

        h, theta, d = hough_line(image, theta=tested_angles)
        hpeaks = hough_line_peaks(h, theta, d, threshold=0.2 * h.max())

        fig, ax = plt.subplots()
        ax.imshow(image, cmap=cm.gray)

        for _, angle, dist in zip(*hpeaks):
            (x0, y0) = dist * np.array([np.cos(angle), np.sin(angle)])
            ax.axline((x0, y0), slope=np.tan(angle + np.pi / 2))

        plt.show()


def auishd():

    # Constructing test image
    image = np.zeros((200, 200))
    idx = np.arange(25, 175)
    image[idx, idx] = 255
    image[line(45, 25, 25, 175)] = 255
    image[line(25, 135, 175, 155)] = 255

    # Classic straight-line Hough transform
    # Set a precision of 0.5 degree.
    tested_angles = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    h, theta, d = hough_line(image, theta=tested_angles)

    # Generating figure 1
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    ax = axes.ravel()

    ax[0].imshow(image, cmap=cm.gray)
    ax[0].set_title("Input image")
    ax[0].set_axis_off()

    angle_step = 0.5 * np.diff(theta).mean()
    d_step = 0.5 * np.diff(d).mean()
    bounds = [
        np.rad2deg(theta[0] - angle_step),
        np.rad2deg(theta[-1] + angle_step),
        d[-1] + d_step,
        d[0] - d_step,
    ]
    ax[1].imshow(np.log(1 + h), extent=bounds, cmap=cm.gray, aspect=1 / 1.5)
    ax[1].set_title("Hough transform")
    ax[1].set_xlabel("Angles (degrees)")
    ax[1].set_ylabel("Distance (pixels)")
    ax[1].axis("image")

    ax[2].imshow(image, cmap=cm.gray)
    ax[2].set_ylim((image.shape[0], 0))
    ax[2].set_axis_off()
    ax[2].set_title("Detected lines")

    for _, angle, dist in zip(*hough_line_peaks(h, theta, d)):
        (x0, y0) = dist * np.array([np.cos(angle), np.sin(angle)])
        ax[2].axline((x0, y0), slope=np.tan(angle + np.pi / 2))

    plt.tight_layout()
    plt.show()


auishd()
