# -------------------------------------------------------------------------------
# Name:        Built UP Area creator
# Purpose:     intern
#
# Author:      rnicolescu
#
# Created:     06/09/2022
# Copyright:   (c) rnicolescu 2022
# Licence:     <your license here>
# -------------------------------------------------------------------------------
print "Loading arcpy..."
from arcpy import env
import time
import arcpy
import os, sys

print "Arcpy loaded!"

t1 = time.time()

class BUA(object):
    print "Creates polygons to represent built-up areas by delineating densely clustered arrangements of buildings on small-scale maps."

    CWD = os.getcwd()

    def __init__(self, path):
        self.path = path

    def check_extension(self):

        if os.path.isdir(self.path) and self.path.endswith(".gdb"):
            print "File valid!"
            return self.path
        else:
            print "Invalid file!"
            sys.exit()

    def parameters(self, path):
        # by default, the feature name in my case is SAL013 for buildings

        env.workspace = path
        env.referenceScale = "5000" # it can be changed due to the project settings
        env.overwriteOutput = True

        print 'Checking if extra fields exist and delete them before creating BUA'
        # Check if fields exists . It exists,delete them
        to_delete = ["CENTROID_X", "CENTROID_Y", "INSIDE_X", "INSIDE_Y", "NEAR_FID", "NEAR_DIST", "ClassValue"]

        for field in arcpy.ListFields(os.path.join(path, 'ThematicData', "SAL013")):
            if field.name in to_delete:
                print "Deleting {}".format(field.name)
                arcpy.DeleteField_management(in_table=os.path.join(path, 'ThematicData', "SAL013"),
                                             drop_field=[field.name])

        print "Adding extra field for processing BUA Creator"
        # Shapefile path can be interpretated. You can change the path and the name by your default
        arcpy.AddField_management(os.path.join(path, "ThematicData", "SAL013"), 'ClassValue', 'Long', 10, )
        print "Creating BUA. Please wait..."

        buildings = os.path.join(path, "ThematicData", "SAL013") #can be different from a gdb to another. Better check before
        field_name = 'ClassValue'
        grouping_distance = "100 Meters"  # grouping_distance and minimum_detail_size are set here for the optimal result after other values on parameters and tests
        minimum_detail_size = "75 Meters"
        output_fcs = os.path.join(path, "bua__BUILDINGS") # these can be changed. I just put the output path inside my gdb
        min_building_count = 200 # default value. It can be changed during different areas

        arcpy.DelineateBuiltUpAreas_cartography(in_buildings=buildings,
                                                identifier_field=field_name,
                                                grouping_distance=grouping_distance,
                                                minimum_detail_size=minimum_detail_size,
                                                out_feature_class=output_fcs,
                                                minimum_building_count=min_building_count)
        print "BUA created successfully!"

        print "Deleting extra fields added"
        for field in arcpy.ListFields(os.path.join(path, 'ThematicData', "SAL013")):
            if field.name in to_delete:
                print "Deleting extra field added: {}".format(field.name)
                arcpy.DeleteField_management(in_table=os.path.join(path, 'ThematicData', "SAL013"),
                                             drop_field=[field.name])

    def surface(self, path):

        env.workspace = path
        env.overwriteOutput = True

        print "Checking for surfaces smaller than 15600 sqm.."
        fc = os.path.join(path, 'bua__BUILDINGS')
        with arcpy.da.UpdateCursor(fc, ["Shape_Area"]) as cursor:
            for row in cursor:
                if row[0] < 15600:
                    cursor.deleteRow()

    def main(self):
        ext = self.check_extension()
        creating = self.parameters(ext)
        surface = self.surface(ext)

if __name__ == "__main__":
    bua_creator = BUA(raw_input("Add gdb path:\n"))
    bua_creator.main()
    t2 = time.time()
    total_time = t2 - t1
    print 'Total time: {} minutes'.format(int((total_time % 3600)//60))