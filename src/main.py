# external imports
import json
import os.path
import sys
from PIL import Image

# internal imports
from util.ANSI import *
from brain import brain

##########################
# ENVIRONMENT PARAMETERS #
##########################
RMN_HOME = "/home/youngmoon01/rmn/"
RUN_PROFILE_HOME = RMN_HOME + "data/profile/run_profile/"
BRAIN_PROFILE_HOME = RMN_HOME + "data/profile/brain_profile/"

REPORT_WINDOW = 200

# ignore todos with keyword 'something'
something = False


############################
# MAIN PROGRAM FLOW STARTS #
############################
if len(sys.argv) < 3:
    print(ANSI_GREEN + "Usage: " + ANSI_RESET + "py main.py [run_profile] [brain_profile]")
    exit()

run_profile_path = RUN_PROFILE_HOME + sys.argv[1]
brain_profile_path = BRAIN_PROFILE_HOME + sys.argv[2]

# check if there is run profile file
if not os.path.isfile(run_profile_path):
    print(ANSI_RED + "Error: " + ANSI_RESET + "Run profile with specified path does not exist.")
    exit()

# check if there is brain profile file
if not os.path.isfile(brain_profile_path):
    print(ANSI_RED + "Error: " + ANSI_RESET + "Brain profile with specified path does not exist.")
    exit()

# read run profiles
f = open(run_profile_path)
dump = f.read()
f.close()
run_profile = json.loads(dump)
del dump

# extract data from run_profile
image_directory_path = run_profile['image_directory_path']
image_label_path = run_profile['image_label_path']
target_range = run_profile['target_range']

# determine start index and end index
start_idx = target_range[0]
end_idx = target_range[1]
total = end_idx - start_idx + 1

# open label file and set position to start index
if not os.path.isfile(image_label_path):
    print(ANSI_RED + "Error: " + ANSI_RESET + "Image label with specified path does not exist.")
    exit()
label_file = open(image_label_path)
for i in range(start_idx - 1):
    label_file.readline()

# read brain profiles
f = open(brain_profile_path)
dump = f.read()
f.close()
brain_profile = json.loads(dump)
del dump

brain = brain(brain_profile)

# start processing target images
# initialize variables related to report
iter_num = 0
hit_count = 0
max_match_count = 0
clean_match_count = 0

hit_window = 0
hit_queue = list()
max_match_window = 0
max_match_queue = list()
clean_match_window = 0
clean_match_queue = list()

for num in range(start_idx, end_idx + 1):
    iter_num += 1
    # get image data
    img_path = image_directory_path + str(num) + ".png"
    img = Image.open(img_path)

    # get label from label file
    label = label_file.readline()
    label = int(label)

    # process image, guess the output, learn and report the result
    ret = brain.process_img(img, label)
    report = ret[0]
    is_hit = ret[1]

    is_max_match = ret[2]
    is_clean_match = ret[3]

    if is_hit:
        hit_count += 1
        hit_window += 1
        hit_queue.append(1)
    else:
        hit_queue.append(0)

    if len(hit_queue) > REPORT_WINDOW:
        hit_window -= hit_queue.pop(0)

    if is_max_match:
        max_match_count += 1
        max_match_window += 1
        max_match_queue.append(1)
    else:
        max_match_queue.append(0)

    if len(max_match_queue) > REPORT_WINDOW:
        max_match_window -= max_match_queue.pop(0)

    if is_clean_match:
        clean_match_count += 1
        clean_match_window += 1
        clean_match_queue.append(1)
    else:
        clean_match_queue.append(0)

    if len(clean_match_queue) > REPORT_WINDOW:
        clean_match_window -= clean_match_queue.pop(0)

    print(report)
    print("Processing: " + str(iter_num) + "/" + str(total))
    hit_rate = ((10000*hit_count)//iter_num)/100
    print("Hit count: " + str(hit_count) + "/" + str(iter_num) + " (" + str(hit_rate) + " %)")
    max_match_rate = ((10000*max_match_count)//iter_num)/100
    print("Max match count: " + str(max_match_count) + "/" + str(iter_num) + " (" + str(max_match_rate) + " %)")
    clean_match_rate = ((10000*clean_match_count)//iter_num)/100
    print("Clean match count: " + str(clean_match_count) + "/" + str(iter_num) + " (" + str(clean_match_rate) + " %)\n")

    # windows statistics
    hit_rate = ((10000*hit_window)//REPORT_WINDOW)/100
    print("Hit count window rate: " + str(hit_rate) + " %")
    max_match_rate = ((10000*max_match_window)//REPORT_WINDOW)/100
    print("Max match window rate: " + str(max_match_rate) + " %")
    clean_match_rate = ((10000*clean_match_window)//REPORT_WINDOW)/100
    print("Clean match window rate: " + str(clean_match_rate) + " %")

print("Processing finished.")
