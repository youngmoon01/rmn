from util.ANSI import *

from gradient_layer import gradient_layer
from gradient_map import gradient_map
from matching_layer import matching_layer

# Brain structure of relative matching neural network
class brain:
    #####################################
    # DEFAULT PARAMETER SETTINGS STARTS #
    #####################################

    # brain file path
    brain_file_path = ""

    # number of gradient difference level
    gradient_level = 8

    # layer depth instead of filter size
    layer_depth = 32

    # spatial locality diminishing weight
    spatial_weight = 0.1
    spatial_locality = 1

    # gradient difference weight
    gradient_weight = 0.1
    gradient_locality = 1

    cell_next_id = 0

    ###################################
    # DEFAULT PARAMETER SETTINGS ENDS #
    ###################################

    @classmethod
    def init(br, brain_profile):
        # reads parameter settings from profile
        br.gradient_level = brain_profile['gradient_level']

        br.layer_depth = brain_profile['layer_depth']

        br.spatial_weight = brain_profile['spatial_weight']
        br.spatial_locality = brain_profile['spatial_locality']
        br.gradient_weight = brain_profile['gradient_weight']
        br.gradient_locality = brain_profile['gradient_locality']

        br.new_cell_weight = brain_profile['new_cell_weight']
        br.active_cell_weight = 1.0 - br.new_cell_weight

        br.brain_file_path = brain_profile['brain_file_path']

        # calculate derived parameters
        br.gradient_step = 256//br.gradient_level

        # check if brain file exists and matches to brain profile
        brain_file_valid = False
        something = False

        if brain_file_valid:
            # import brain data from the brain file
            something

        # initialize the gradient maps
        gradient_map.init(br.gradient_level)

        # initialize the static variables of matching layer
        matching_layer.init(brain_profile)

        # initialize the static variables of gradient layer
        gradient_layer.init(brain_profile)

    # process a target image, guess the output, learn and return the report
    @classmethod
    def process_img(br, img, label):
        # initialize activated index and output_layer
        output_layer = dict()

        # initialize feedback lists
        feedback_list = list()

        # process the image from the gradient analysis
        gradient_layer.process_img(img, output_layer)

        # report-related boolean
        is_hit = False
        is_max_match = False
        is_clean_match = True

        max_activated = "A phrase which is less likely to be a label of an image"
        max_weight = -float("inf")

        # compare the outputs with the correct output and get feedbacks
        report = "================\n"
        if label in output_layer.keys():
            if output_layer[label] > 1.0: # hit
                # update max_activated
                if max_weight < output_layer[label]:
                    max_weight = output_layer[label]
                    max_activated = label

                is_hit = True

                weight = str(int(output_layer[label]*100)/100.0)
                report += ANSI_BGREEN + str(label) + ": " + weight + ANSI_RESET + "\n"
            else: # positive feedback
                # report related
                is_clean_match = False

                weight = str(int(output_layer[label]*100)/100.0)
                report += ANSI_BLUE + str(label) + ": " + weight + ANSI_RESET + "\n"

                # calculate the activation difference
                difference = 1.1*(1.0 - output_layer[label])

                feedback_list.append((label, difference))
        else: # consider as 0.0 activation positive feedback
            # report related
            is_clean_match = False

            report += ANSI_BLUE + str(label) + ": 0.0" + ANSI_RESET + "\n"
            feedback_list.append((label, 1.1))

        for output in output_layer.keys():
            # update max_activated
            if max_weight < output_layer[output]:
                max_weight = output_layer[output]
                max_activated = output

            if output_layer[output] > 0.0:
                if output != label: # negative feedback
                    # report related
                    is_clean_match = False

                    weight = str(int(output_layer[output]*100)/100.0)
                    report += ANSI_RED + str(output) + ": " + weight + ANSI_RESET + "\n"

                    # calculate the activation difference
                    difference = 1.1*(0.0 - output_layer[output])

                    feedback_list.append((output, difference))
            else:
                if output != label:
                    weight = str(int(output_layer[output]*100)/100.0)
                    report += str(output) + ": " + weight + "\n"

        if label == max_activated:
            is_max_match = True

        report += "================\n"
        report += "label: " + str(label)

        # update the history with the label
        gradient_layer.update_history(label)

        # feedback the network
        new_cells = None # new set of cells for positive feedback
        new_cell_count = 0
        for item in feedback_list:
            output = item[0]
            difference = item[1]
            if difference > 0.0: # positive feedback
                if new_cells == None:
                    # detect new set of cells
                    new_cells = list()
                    new_cell_count = gradient_layer.detect_new_cells(img, label, new_cells)

                # feedback to new cells
                new_cell_diff = difference*br.new_cell_weight
                alpha = new_cell_diff/new_cell_count
                for cell_list in new_cells:
                    for cell in cell_list:
                        cell.feedback(output, alpha)

                # feedback to active cells
                active_cell_diff = br.active_cell_weight*difference
                weight_sum = gradient_layer.update_history(label)
                ffw = active_cell_diff/weight_sum
                gradient_layer.active_cells_feedback(output, ffw)

            else: # negative feedback
                # feedback to active cells
                weight_sum = gradient_layer.update_history(label)
                ffw = difference/weight_sum
                gradient_layer.active_cells_feedback(output, ffw)

        return (report, is_hit, is_max_match, is_clean_match)


    @classmethod
    def request_cell_id(br):
        ret = br.cell_next_id
        br.cell_next_id += 1
        return ret

    # import brain from a brain file
    def import_brain(self, profile_path):
        something

    # export brain to brain file
    def export_brain(self, profile_path):
        something
