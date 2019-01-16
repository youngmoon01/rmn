import json
from util.ANSI import *

from base_layer import base_layer

# Brain structure of relative matching neural network
class brain:
    def __init__(self, brain_profile):
        #####################################
        # DEFAULT PARAMETER SETTINGS STARTS #
        #####################################

        # brain file path
        self.brain_file_path = ""

        # number of gradient difference level
        self.gradient_level = 8

        # filter size (let's set these larger than the filter sizes in typical CNN)
        self.f_width = 30
        self.f_height = 30

        # spatial locality diminishing weight
        self.spatial_weight = 1.0

        # gradient difference weight
        self.gradient_weight = 1.0

        # derived parameters(calculated in __init__())
        self.base_layer_depth = 0

        ###################################
        # DEFAULT PARAMETER SETTINGS ENDS #
        ###################################

        # reads parameter settings from profile
        self.gradient_level = brain_profile['gradient_level']

        self.f_width = brain_profile['f_width']
        self.f_height = brain_profile['f_height']

        self.spatial_weight = brain_profile['spatial_weight']
        self.gradient_weight = brain_profile['gradient_weight']

        self.brain_file_path = brain_profile['brain_file_path']

        # calculate derived parameters
        self.base_layer_depth = 2*self.gradient_level + 1
        self.gradient_step = 256//self.gradient_level

        self.init_brain(brain_profile)

        # check if brain file exists and matches to brain profile
        brain_file_valid = False
        something = False

        if brain_file_valid:
            # import brain data from the brain file
            something

    # newly initialize a brain
    def init_brain(self, brain_profile):
        self.base_layer = base_layer(brain_profile)

    # process a target image, guess the output, learn and return the report
    def process_img(self, img, label):
        # intensity quantization
        img_data = list(img.getdata())
        for i in range(len(img_data)):
            img_data[i] = img_data[i]//self.gradient_step

        # initialize activated index and output_layer
        self.output_layer = dict()
        self.base_layer.clear_activated_index()

        img_width = img.width
        img_height = img.height

        for x in range(img_width):
            for y in range(img_height):
                self.process_pixel(img_data, x, y, img_width, img_height, label)

        # learn and report the processing of image
        # initialize feedback lists
        feedback_list = list()

        # report related boolean
        is_hit = False
        is_max_match = False
        is_clean_match = True

        max_activated = "A phrase which is less likely to be a label of an image"
        max_weight = -float("inf")

        report = "================\n"
        if label in self.output_layer.keys():

            if self.output_layer[label] > 1.0: # hit
                # update max_activated
                if max_weight < self.output_layer[label]:
                    max_weight = self.output_layer[label]
                    max_activated = label

                is_hit = True

                weight = str(int(self.output_layer[label]*100)/100.0)
                report += ANSI_BGREEN + str(label) + ": " + weight + ANSI_RESET + "\n"
            else: # positive feedback
                # report related
                is_clean_match = False

                weight = str(int(self.output_layer[label]*100)/100.0)
                report += ANSI_RED + str(label) + ": " + weight + ANSI_RESET + "\n"

                # calculate the activation difference
                difference = 1.0 - self.output_layer[label]
                if difference < 1.0: #minimum update amount
                    difference = 1.0

                feedback_list.append((label, difference))
        else: # consider as 0.0 activation positive feedback
            # report related
            is_clean_match = False

            report += ANSI_RED + str(label) + ": 0.0" + ANSI_RESET + "\n"
            feedback_list.append((label, 1.0))

        for output in self.output_layer.keys():
            # update max_activated
            if max_weight < self.output_layer[output]:
                max_weight = self.output_layer[output]
                max_activated = output

            if self.output_layer[output] > 1.0:
                if output != label: # negative feedback
                    # report related
                    is_clean_match = False

                    weight = str(int(self.output_layer[output]*100)/100.0)
                    report += ANSI_BLUE + str(output) + ": " + weight + ANSI_RESET + "\n"

                    # calculate the activation difference
                    difference = 1.0 - self.output_layer[output]
                    if difference > -1.0: # minimum update amount
                        difference = -1.0

                    feedback_list.append((output, difference))
            else:
                if output != label:
                    weight = str(int(self.output_layer[output]*100)/100.0)
                    report += str(output) + ": " + weight + "\n"

        if label == max_activated:
            is_max_match = True

        report += "================\n"
        report += "label: " + str(label)

        # weight update after collecting history
        self.base_layer.collect_history(label)
        self.base_layer.weight_update(feedback_list, label)

        return (report, is_hit, is_max_match, is_clean_match)

    # process a pixel
    def process_pixel(self, img_data, x, y, img_width, img_height, label):
        # load some member variables
        f_width = self.f_width
        f_height = self.f_height

        # calculate the source intensity
        src_intensity = img_data[img_width*x + y]

        # determine the scan range
        if x - f_width > 0:
            x_start = x - f_width
        else:
            x_start = 0

        if x + f_width + 1 < img_width:
            x_end = x + f_width + 1
        else:
            x_end = img_width

        if y + f_height + 1 < img_height:
            y_end = y + f_height + 1
        else:
            y_end = img_height

        # process first line
        for i in range(x + 1, x_end):
            # calculate the destination intensity
            dst_intensity = img_data[img_width*i + y]

            # accumulate weight to each label
            self.scan_pixel(x, y, i , y, src_intensity, dst_intensity)

        # process rest bottom lines
        for i in range(x_start, x_end):
            for j in range(y + 1, y_end):
                # calculate the destination intensity
                dst_intensity = img_data[img_width*i + j]

                # accumulate weight to each label
                self.scan_pixel(x, y, i , j, src_intensity, dst_intensity)

    def scan_pixel(self, src_x, src_y, dst_x, dst_y, src_intensity, dst_intensity):
        map_x = (dst_x - src_x) + self.f_width
        map_y = (dst_y - src_y)

        gradient = dst_intensity - src_intensity
        self.base_layer.activate_cell(map_x, map_y, gradient, self.output_layer)

    # import brain from a brain file
    def import_brain(self, profile_path):
        something

    # export brain to brain file
    def export_brain(self, profile_path):
        something
