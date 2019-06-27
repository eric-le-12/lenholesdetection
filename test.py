"""
Demo of how to use LenDetection package
"""
#import neccessary tools
from LenDetection import LenDetection as ldt
import argparse

#construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-im", "--image_path", required=True,
	help="path to input image")
ap.add_argument("-output", "--output_path", required=True,
	help="path to output directory to save image")
ap.add_argument("-min_radius", "--min_radius", required=False,default=10,
	help="minimum_radius")
ap.add_argument("-top_k_radius", "--top_k_radius", required=False,default=None,
	help="choosing k for selecting top frequent occured radius for averaging")
args = vars(ap.parse_args())
#get arguments
image_path=args["image_path"]
output_path=args["output_path"]
min_radius=args["min_radius"]
top_k_radius=args["top_k_radius"]
#begining detection
detection=ldt(image_path,output_path,min_radius,top_k_radius)
detection.run()
