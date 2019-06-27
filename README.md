# lenholesdetection
Classifying Empty Holes and Len Holes
# LOCATING AND CLASSIFYING LEN HOLES
## Quick Start
1.Run test.py
python test.py -im testimage.jpg -output path/to/output/directory
Example
python demo.py -im IMG2.png -output test
Argument List: 
 -h, --help            show this help message and exit
  -im IMAGE_PATH, --image_path IMAGE_PATH
                        path to input image
  -output OUTPUT_PATH, --output_path OUTPUT_PATH
                        path to output directory to save image and res file
  -min_radius MIN_RADIUS, --min_radius MIN_RADIUS
                        minimum_radius [default 10]
  -top_k_radius TOP_K_RADIUS, --top_k_radius TOP_K_RADIUS
                        choosing k for selecting top frequent occured radius
                        for averaging [default None, recommended=3]
2. Select Region of interest
 
Select your Region of interest, which contain the tool with len holes. Press Enter. Press C to cancle
A new window called “Region of Interest” will appear. Press Enter again to beginning analyzing process.
After processed, some new windows will appear showing you the results. Press any key to exit.
Res file and output images will be saved in your output folder.
Please note that, you should only bound the object by a sufficient rectangle. Since the bigger area the ROI is, the more computation expense and false positive len holes arise. 
Example:
 

# Note: In the original RES files, the radii components are diameter. I think there were a typo error.
  

 
Plotting with R=33 in Res file. The 3rd components are actually Diameter

## WORKING PRINCIPLES:
1.Detect all holes
As the files are large over thousand of pixels per dimension, and only 3 samples are provided, my first approach using YOLO v2 (Darkflow implementation) and Faster rcnn seem to be ineffective. Therefore, it raise a need to extract the Region of Interest. After extracting the region of interest, some traditional image processing techniques should be used to locate the holes. 
Holes are detected using Imaging Thresholding Techniques. The image is first converted to grayscale, filtered by GaussianBlur, then enhanced using Histogram Equalization. The binary image is formed by ADAPTIVE THRESHOLDING.
The binary image is then fed to find contours. Any contours with number of vertices higher than 9 and children’s hierarchy is -1 would be considered as a circular hole.
2. Feed each hole into CNN network
A pretrained CNN network is prepared to classify if the holes contain lens or not.
The output would be a green circle around hole with lens and red circles around empty holes.

## Future Improvement:
Due to the shortage of time, I have not performed an outstanding result. However, non-max suppression could be applied to remove overlapped region. A more accurate hole detection approach could be obtained via classical Sliding Window Techniques.

Thank you for your reading.
