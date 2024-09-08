import numpy as np
import csv
import argparse
from osgeo import gdal, osr

class CSVToGeoTIFFConverter:
    def __init__(self, file, output, width, height, pixel_size_x=1000, pixel_size_y=-1000, minx=0.0, maxy=0.0, epsg=4326):
        """
        Initialize the converter with the input CSV file and output TIFF file name.
        
        :param file: Path to the input CSV file.
        :param output: Path to the output TIFF file.
        :param width: Width of the output image.
        :param height: Height of the output image.
        :param pixel_size_x: Size of each pixel in the x direction.
        :param pixel_size_y: Size of each pixel in the y direction.
        """
        self.file = file
        self.output = output
        self.width = width
        self.height = height
        self.pixel_size_x = pixel_size_x
        self.pixel_size_y = pixel_size_y
        self.minx = minx 
        self.maxy = maxy 
        self.epsg = epsg 

    def convert(self):
        """
        Convert the CSV file to a TIFF file.
        """
        try:
            # Initialize an empty image array with NaN values
            img = np.full((self.height, self.width), np.nan, dtype=np.float32)

            # Read the CSV file
            with open(self.file, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header

                # Populate the image array
                for row in reader:
                    idx, classId = int(row[0]), float(row[1])
                    y, x = divmod(idx, self.width)
                    if y < self.height and x < self.width:
                        img[y, x] = classId

            # Calculate statistics, don't include NaN values
            min_val = float(img[~np.isnan(img)].min())
            max_val = float(img[~np.isnan(img)].max())
            mean_val = float(img[~np.isnan(img)].mean())
            stddev_val = float(img[~np.isnan(img)].std())

            # Write NaN to 0
            img[np.isnan(img)] = 0.0

            # Create the GeoTIFF file
            driver = gdal.GetDriverByName('GTiff')
            dataset = driver.Create(self.output, self.width, self.height, 1, gdal.GDT_Float32)

            # Set geotransform and projection
            dataset.SetGeoTransform([self.minx, self.pixel_size_x, 0, self.maxy, 0, self.pixel_size_y])
            
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(int(self.epsg))  # Example projection
            dataset.SetProjection(srs.ExportToWkt())

            # Write the image data to the band
            band = dataset.GetRasterBand(1)
            band.SetNoDataValue(0)
            band.WriteArray(img)

            # Set statistics
            band.SetStatistics(min_val, max_val, mean_val, stddev_val)

            # Clean up
            band.FlushCache()
            dataset.FlushCache()

        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    """
    Main function to parse command line arguments and initiate the conversion.
    """
    # Read args from command line
    parser = argparse.ArgumentParser(description='Convert CSV to TIFF')
    parser.add_argument('--file', type=str, required=True, help='CSV file to convert')
    parser.add_argument('--output', type=str, default='output.tiff', help='Output TIFF file name')
    parser.add_argument('--width', type=int, required=True, help='Width of the output image')
    parser.add_argument('--height', type=int, required=True, help='Height of the output image')
    parser.add_argument('--pixel_size_x', type=int, default=1000, help='Size of each pixel in the x direction')
    parser.add_argument('--pixel_size_y', type=int, default=1000, help='Size of each pixel in the y direction')
    parser.add_argument('--x', type=float, default=0, help='Minimum x coordinate')
    parser.add_argument('--y', type=float, default=0, help='Maximum y coordinate')
    parser.add_argument('--epsg', type=int, default=4326, help='EPSG code of the projection')

    args = parser.parse_args()

    converter = CSVToGeoTIFFConverter(file=args.file, output=args.output, width=args.width, height=args.height, pixel_size_x=args.pixel_size_x, pixel_size_y=args.pixel_size_y, minx=args.x, maxy=args.y, epsg=args.epsg)
    converter.convert()

if __name__ == '__main__':
    main()
