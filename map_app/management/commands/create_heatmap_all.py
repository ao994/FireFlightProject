import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from rasterio.transform import from_origin
from scipy.ndimage import gaussian_filter
from map_app.models import Results

class Command(BaseCommand):
    help = 'Generate heatmap raster from full DB data (Results) using posterior median values'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting full database heatmap generation...'))
        
        # Define output directory and file path.
        output_dir = os.path.join('map_app', 'static', 'images')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_raster = os.path.join(output_dir, 'heatmap_raster.tif')
        
        # Create the raster using all database data.
        self.create_heatmap_raster(output_raster)
        
        # Optionally, you can include visualization here if needed.
        # self.visualize_raster(output_raster)
        
        self.stdout.write(self.style.SUCCESS('Full database heatmap generation completed.'))

    def create_heatmap_raster(self, output_raster):
        # Query the Results table to obtain grid coordinates and posterior median values.
        latitudes, longitudes, medians = [], [], []
        results = Results.objects.select_related('gridID').all()
        for result in results:
            grid = result.gridID
            latitudes.append(grid.Grid_Lat_NAD83)
            longitudes.append(grid.Grid_Long_NAD83)
            medians.append(result.posterior_median)

        # Determine the bounds and grid parameters.
        min_lat, max_lat = min(latitudes), max(latitudes)
        min_lon, max_lon = min(longitudes), max(longitudes)
        pixel_size = 0.01  # Adjust as needed.
        nrows = int((max_lat - min_lat) / pixel_size) + 1
        ncols = int((max_lon - min_lon) / pixel_size) + 1
        raster_data = np.zeros((nrows, ncols), dtype=np.float32)

        # Create the affine transform for the raster.
        transform = from_origin(min_lon, max_lat, pixel_size, pixel_size)

        # Populate the raster array with posterior median values.
        for lat, lon, median in zip(latitudes, longitudes, medians):
            row = int((max_lat - lat) / pixel_size)
            col = int((lon - min_lon) / pixel_size)
            # If multiple results fall in the same cell, you might consider aggregating them.
            raster_data[row, col] = median

        # Apply Gaussian smoothing and boost intensity.
        raster_data = gaussian_filter(raster_data, sigma=2.0)
        raster_data = raster_data * 20  # Adjust multiplier as needed.

        # Write the raster to a GeoTIFF.
        with rasterio.open(
            output_raster, 'w', driver='GTiff', 
            height=nrows, width=ncols, count=1, dtype='float32',
            crs='+proj=latlong', transform=transform
        ) as dst:
            dst.write(raster_data, 1)

        self.stdout.write(self.style.SUCCESS(f"Raster file created at '{output_raster}'."))

    def visualize_raster(self, raster_file):
        # Optional helper to visualize the raster.
        with rasterio.open(raster_file) as src:
            data = src.read(1)

        if data.max() - data.min() > 0:
            norm_data = (data - data.min()) / (data.max() - data.min())
        else:
            norm_data = data

        thresh = np.percentile(norm_data, 95)
        norm_data = np.clip(norm_data, 0, thresh)
        norm_data = norm_data / thresh

        cmap = plt.get_cmap('viridis')
        plt.figure(figsize=(10, 6))
        plt.imshow(norm_data, cmap=cmap, interpolation='bilinear', vmin=0, vmax=1)
        plt.colorbar(label='Posterior Median (normalized)')
        plt.title('Heatmap from Full DB Data')
        plt.show()
