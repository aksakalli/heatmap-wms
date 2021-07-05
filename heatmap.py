from io import BytesIO

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from matplotlib import cm, colors

alpha_heat = colors.LinearSegmentedColormap(
    "alpha_heat",
    {
        "red": [
            (0, 0, 0),
            (0.001, 0.54, 0.54),
            (0.1, 1, 1),
            (0.55, 1, 1),
            (0.7, 0.48, 0.48),
            (0.85, 0, 0),
            (1, 0, 0),
        ],
        "green": [
            (0, 0, 0),
            (0.1, 0, 0),
            (0.25, 0.27, 0.27),
            (0.4, 0.64, 0.64),
            (0.55, 1, 1),
            (0.7, 0.98, 0.98),
            (0.85, 1, 1),
            (1.0, 0, 0),
        ],
        "blue": [(0.0, 0, 0), (0.7, 0, 0), (0.85, 1, 1), (1, 1, 1)],
        "alpha": [
            (0.0, 0, 0),
            (0.001, 0, 0),
            (0.1, 0.25, 0.25),
            (0.25, 0.5, 0.5),
            (1, 0.5, 0.5),
        ],
    },
)

cm.register_cmap(cmap=alpha_heat)


class Heatmap:
    """Creates a heatmap image from added points

    usage:

    >>> heatmap = Heatmap(5, 5, 0, 0, 50, 50)
    >>> heatmap.add_point(32, 11)
    >>> heatmap.add_point(22, 21)
    >>> heatmap.pixel_grid
    array([[0., 0., 0., 0., 0.],
           [0., 0., 0., 0., 0.],
           [0., 0., 1., 0., 0.],
           [0., 0., 0., 1., 0.],
           [0., 0., 0., 0., 0.]])

    The added points are scaled out to
    the existing pixel size of the image grid.
    Use the same map projection for constructing the heatmap
    and adding new points.

    >>> heatmap.update_pixel_grid_rgba()
    >>> image_bytes = heatmap.get_heatmap_image_bytes()
    """

    def __init__(self, width, height, west, south, east, north):
        self.pixel_grid = np.zeros((height, width))
        self.pixel_grid_rgba = []
        self.west = west
        self.south = south
        self.east = east
        self.north = north

    def add_point(self, lon, lat, val=1):
        """adds a new point to the grid"""
        height, width = self.pixel_grid.shape
        if self.north > lat > self.south and self.west < lon < self.east:
            y = int(height - height * (lat - self.south) / (self.north - self.south))
            x = int(width * (lon - self.west) / (self.east - self.west))
            self.pixel_grid[y][x] += val

    def update_pixel_grid_rgba(self, blur_sigma=10, cmap_name="alpha_heat"):
        """The `pixel_grid_rgba` attribute is not updated after addding points.
        This method needs to be called before getting rgba images.

        Parameters
        ----------
        blur_sigma: scalar or sequence of scalars
        creates more blurred image when you increase it

        cmap_name: matplotlib's colormap name
        you can set it to a different one or register your custom color map
        using `matplotlib.cm.register_cmap`.
        """
        normalize = colors.Normalize()
        cmap = cm.get_cmap(cmap_name)
        pixel_grid_blurred = gaussian_filter(self.pixel_grid, sigma=blur_sigma)
        self.pixel_grid_rgba = cmap(normalize(pixel_grid_blurred))

    def get_heatmap_image(self):
        """returns PIL image object"""
        pixel_grid_rgba_hex = (self.pixel_grid_rgba * 255).astype(np.uint8)
        return Image.fromarray(pixel_grid_rgba_hex, "RGBA")

    def get_heatmap_image_bytes(self):
        """returns PNG image bytes"""
        image = self.get_heatmap_image()
        with BytesIO() as png_buffer:
            image.save(png_buffer, format="PNG")
            image_byte_values = png_buffer.getvalue()
        return image_byte_values


if __name__ == "__main__":
    import doctest

    doctest.testmod()
