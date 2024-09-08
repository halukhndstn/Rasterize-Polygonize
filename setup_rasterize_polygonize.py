import subprocess

subprocess.check_call(['python', '-m', 'pip', 'install', 'tifffile'])
subprocess.check_call(['python', '-m', 'pip', 'install', 'gdal'])

# After start this raster file you need to restart QGIS