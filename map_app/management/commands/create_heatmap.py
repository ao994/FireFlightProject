import os
import csv
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from django.conf import settings
from django.core.management.base import BaseCommand
from rasterio.transform import from_origin
from scipy.ndimage import gaussian_filter  # For smoothing
from map_app.models import Grid

class Command(BaseCommand):
    help = 'Generate heatmap raster from grid data (DB) and filtered posterior median values (CSV)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting raster generation...'))
        
        # Define the output directory and ensure it exists.
        output_dir = os.path.join('map_app', 'static', 'images')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Set the output raster file path.
        output_raster = os.path.join(output_dir, 'heatmap_raster.tif')
        
        self.create_heatmap_raster(output_raster)
        self.stdout.write(self.style.SUCCESS('Raster generation and visualization completed.'))

    def create_heatmap_raster(self, output_raster):
        # Build a dictionary mapping grid_OID to Grid objects.
        grid_dict = {grid.id: grid for grid in Grid.objects.all()}
        
        # Path to the CSV file (assumed at the repo's top level).
        csv_file_path = os.path.join(settings.BASE_DIR, 'bird_data.csv')
        
        latitudes, longitudes, medians = [], [], []
        
        # Read the CSV file.
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                grid_oid = row.get('grid_OID')
                if not grid_oid:
                    continue
                try:
                    grid_oid_int = int(grid_oid)
                except ValueError:
                    continue  # Skip rows with invalid grid_OID
                
                grid = grid_dict.get(grid_oid_int)
                if grid is None:
                    continue  # Skip if grid not found in the database
                
                # Append grid coordinates from the DB.
                latitudes.append(grid.Grid_Lat_NAD83)
                longitudes.append(grid.Grid_Long_NAD83)
                
                # Append the posterior median value from the CSV.
                try:
                    medians.append(float(row.get('posterior_median', 0)))
                except ValueError:
                    medians.append(0)
        
        # Ensure we have data to process.
        if not latitudes or not longitudes or not medians:
            self.stdout.write(self.style.ERROR("No valid data found in CSV or matching grid records."))
            return

        # Define raster grid parameters.
        min_lat, max_lat = min(latitudes), max(latitudes)
        min_lon, max_lon = min(longitudes), max(longitudes)
        pixel_size = 0.01  # Adjust as needed.
        nrows = int((max_lat - min_lat) / pixel_size) + 1
        ncols = int((max_lon - min_lon) / pixel_size) + 1
        raster_data = np.zeros((nrows, ncols), dtype=np.float32)

        # Use from_origin(min_lon, max_lat, pixel_size, pixel_size) for correct alignment.
        transform = from_origin(min_lon, max_lat, pixel_size, pixel_size)

        # Populate the raster with posterior median values.
        for lat, lon, median in zip(latitudes, longitudes, medians):
            row = int((max_lat - lat) / pixel_size)
            col = int((lon - min_lon) / pixel_size)
            # Ensure indices are within bounds.
            if 0 <= row < nrows and 0 <= col < ncols:
                raster_data[row, col] = median

        # Apply Gaussian smoothing (sigma=2.0) and boost intensity.
        raster_data = gaussian_filter(raster_data, sigma=2.0)
        raster_data = raster_data * 20  # Adjust multiplier as needed.

        # Write the smoothed/scaled raster to a GeoTIFF.
        with rasterio.open(
            output_raster, 'w', driver='GTiff', 
            height=nrows, width=ncols, count=1, dtype='float32',
            crs='+proj=latlong', transform=transform
        ) as dst:
            dst.write(raster_data, 1)

        self.stdout.write(self.style.SUCCESS(f"Raster file created at '{output_raster}'."))
