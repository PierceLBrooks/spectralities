
import os
import sys
import math
import shutil
import subprocess
#import diplib as dip
from ridge_detector import RidgeDetector
from PIL import Image

if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
    sys.exit()
intermediary = os.path.basename(sys.argv[1])
if not "." in intermediary:
    sys.exit()
intermediary = intermediary[:intermediary.rindex(".")]+".png"
intermediary = os.path.join(os.path.abspath(os.path.dirname(sys.argv[1])), intermediary)
if sys.flags.debug:
    print(intermediary)
if not os.path.exists(intermediary):
    command = []
    command.append(sys.executable)
    command.append(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "audio2spec", "wav2png.py"))
    command.append("--filename")
    command.append(sys.argv[1])
    command.append("single")
    if sys.flags.debug:
        print(str(command))
    subprocess.check_output(command)
"""
intermediary = dip.ImageRead(intermediary)
output = dip.Image()
dip.DanielssonLineDetector(intermediary, out=output)
output.Show()
dip.ImageWrite(output, sys.argv[0]+".png")
"""
det = RidgeDetector(line_widths=[1, 2, 3],  # Line widths to detect
                    low_contrast=100,  # Lower bound of intensity contrast
                    high_contrast=200,  # Higher bound of intensity contrast
                    min_len=10, # Ignore ridges shorter than this length
                    max_len=0, # Ignore ridges longer than this length, set to 0 for no limit
                    dark_line=True, # Set to True if detecting black ridges in white background, False otherwise
                    estimate_width=True, # Estimate width for each detected ridge point
                    extend_line=True, # Tend to preserve ridges near junctions if set to True
                    correct_pos=False,  # Correct ridge positions with asymmetric widths if set to True
                    )
det.detect_lines(intermediary)
#det.show_results()
det.save_results(os.getcwd())
left = Image.open(intermediary)
right = Image.open(os.path.join(os.getcwd(), "_binary_contours.png"))
if sys.flags.debug:
    print(str(left.size))
    print(str(right.size))
width = left.size[0]
height = left.size[1]
if not (width == right.size[0] or height == right.size[1]):
    sys.exit()
out = Image.new("RGBA", (width, height))
pixels = []
pixels.append(left.load())
pixels.append(right.load())
pixels.append(out.load())
domain = 5
threshold = 10
for x in range(width):
    for y in range(height):
        total = 0
        for i in range(-domain, domain):
            for j in range(-domain, domain):
                if ((float(i)**2.0)+(float(j)**2.0))**0.5 > float(domain):
                    continue
                position = [x+i, y+j]
                if position[0] < 0 or position[0] >= width or position[1] < 0 or position[1] >= height:
                    continue
                pixel = pixels[1][position[0], position[1]]
                color = []
                if "int" in str(type(pixel)):
                    color.append(pixel)
                else:
                    color += list(pixel)
                #print(str(color)+" @ "+str(position))
                if 0 in color:
                    total += 1
        #print(str(total)+" = "+str([x, y])+" @ "+str(float(total-threshold)/(float(threshold)*0.5)))
        if total < threshold:
            pixels[2][x, y] = (0, 0, 0, 255)
            continue
        pixel = pixels[0][x, y]
        color = []
        if not "int" in str(type(pixel)):
            pixel = pixel[0]
        pixel = int(min(1.0, max(0.0, (float(pixel)/255.0)*(float(total-threshold)/(float(threshold)*0.5))))*255.0)
        color.append(pixel)
        color.append(pixel)
        color.append(pixel)
        color.append(255)
        pixels[2][x, y] = tuple(color)
intermediary = os.path.join(os.getcwd(), os.path.basename(sys.argv[0])+".png")
if sys.flags.debug:
    print(intermediary)
out.save(intermediary)
shutil.copyfile(sys.argv[1], os.path.join(os.getcwd(), os.path.basename(sys.argv[0])+".wav"))
if os.path.exists(intermediary):
    command = []
    command.append(sys.executable)
    command.append(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "audio2spec", "png2wav.py"))
    command.append("--filename")
    command.append(intermediary)
    command.append("--wavfile")
    command.append(os.path.join(os.getcwd(), os.path.basename(sys.argv[0])+".png.wav"))
    if sys.flags.debug:
        print(str(command))
    subprocess.check_output(command)

