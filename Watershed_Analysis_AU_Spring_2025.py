"""This whole block of codes was used to solve the watershed
analysis problem as required by the Advanced GIS LAB-10"""

# Step 1: Import Library and Get User Inputs
import arcpy
from arcpy import sa

# Get Workspace directed by User
Workspace = input("Enter the full path to save output Files : ").strip().replace("\\", "/")
arcpy.env.workspace = Workspace
arcpy.env.overwriteOutput = True

# Get User Inputs for Analysis
inputDEM = input("Enter the full path to the raster DEM file: ").strip()
inputPourPoint = input("Enter the full path to the pour point shapefile: ").strip()
clippingMask = input("Enter the full path to the clipping mask shapefile (or leave blank if clipping is not required): ").strip()

# Clip the DEM if a Clipping Mask is Provided
if clippingMask.strip() != "":
    print("Clipping mask detected. Clipping DEM...")
    clipped_dem = sa.ExtractByMask(inputDEM, clippingMask)
    clipped_dem.save("DEM_Clipped")
    DEM = "DEM_Clipped"
else:
    print("No clipping mask provided. Using the full extent of the DEM...")
    DEM = inputDEM

print("DEM is ready for further processing!")

# Step 2: Fill Sinks Calculate Flow Direction and Accumulation
print("Filling sinks in the DEM...")
DEM = sa.Fill(DEM)

# Flow Direction
print("Calculating flow direction using D8...")
flowDir = sa.FlowDirection(DEM, "#", "#", 'D8')
flowDir.save("FlowDir.tif")
print("Flow direction saved as FlowDir.tif!")

# Flow Accumulation
print("Calculating flow accumulation using D8...")
flowAccu = sa.FlowAccumulation(in_flow_direction_raster=flowDir, data_type="FLOAT", flow_direction_type='D8')
flowAccu.save("FlowAccu.tif")
print("Flow accumulation saved as FlowAccu.tif!")

# Snap Pour Point to the Highest Accumulation Cell Nearby
print("Calculating cell size for snapping tolerance...")
cell_size = float(arcpy.management.GetRasterProperties(DEM, "CELLSIZEX").getOutput(0))
tolerance = cell_size * 2
print(f"Cell Size: {cell_size}, Tolerance: {tolerance}")

print("Snapping pour point to the highest flow accumulation within tolerance...")
snappedPourPoint = sa.SnapPourPoint(inputPourPoint, flowAccu, tolerance)
snappedPourPoint.save("SnaPP.tif")
print("Snapped pour point saved as SnaPP.tif!")

# Run Watershed Analysis
print("Running watershed analysis...")
watershed = sa.Watershed(flowDir, snappedPourPoint)
watershed.save("Watershed.tif")
print("Watershed analysis completed and saved as Watershed.tif!")

# Calculate All Watershed Sub-basins in the DEM
print("Calculating all watershed sub-basins in the DEM...")
basins = sa.Basin(flowDir)
basins.save("Basin.tif")
print("Sub-basins are also calculated and saved as Basin.tif!")

# Step 3: Convert the Processed Raster to Polygon Features
# Convert the Watershed Raster to Polygon
print("Converting Watershed raster to polygon...")
arcpy.conversion.RasterToPolygon("Watershed.tif", "Watershed_Polygon.shp", "SIMPLIFY", "Value")
print("Watershed converted and saved as Watershed_Polygon.shp!")

# Convert the Basin Raster to Polygon
print("Converting Basin raster to polygon...")
arcpy.conversion.RasterToPolygon("Basin.tif", "Basin_Polygon.shp", "SIMPLIFY", "Value")
print("Basin also converted and saved as Basin_Polygon.shp!")
