from gradient_layer import gradient_layer
from history_map import history_map

class base_layer:
    def __init__(self, brain_profile):
        # loads brain profile
        self.gradient_level = brain_profile['gradient_level']

        self.f_width = brain_profile['f_width']
        self.f_height = brain_profile['f_height']

        self.spatial_weight = brain_profile['spatial_weight']
        self.gradient_weight = brain_profile['gradient_weight']

        # activated history to apply frequency weight
        self.activated_history = list()
        for gradient in range(self.gradient_level):
            self.activated_history.append(history_map(self.f_width, self.f_height))

        # activated_index accelerates learning-related calculation
        self.activated_index = list()
        for num in range(self.gradient_level):
            self.activated_index.append(dict())

        # generate gradient layers
        self.gradient_layers = list()
        for gradient in range(self.gradient_level):
            self.gradient_layers.append(gradient_layer(self.f_width, self.f_height, gradient))

    def activate_cell(self, x, y, gradient, output_layer):
        # update activated index to accelerates learning-related calculation
        index_map = self.activated_index[gradient]

        # log to index map
        if (x, y) in index_map:
            index_map[(x, y)] += 1
        else:
            index_map[(x, y)] = 1

        # activate weights
        self.gradient_layers[gradient].activate_cell(x, y, output_layer)

    def clear_activated_index(self):
        # clear and re-initialize the activated index
        del self.activated_index

        self.activated_index = list()
        for num in range(self.gradient_level):
            self.activated_index.append(dict())

    def weight_update(self, feedback_list, label, ffweight_sum):
        for item in feedback_list:
            output = item[0]
            difference = item[1]

            # scale the ffweight sum to the difference
            alpha = difference/ffweight_sum

            for gradient in range(len(self.activated_index)):
                index_map = self.activated_index[gradient]
                the_layer = self.gradient_layers[gradient]
                the_history = self.activated_history[gradient]

                for coor in index_map.keys():
                    # get frequency factor
                    x = coor[0]
                    y = coor[1]
                    ff = the_history.get_frequency_factor(x, y, label)
                    update_amount = ff*alpha

                    # weight updates
                    the_layer.weight_update(coor, update_amount, output)

    def collect_history(self, label):
        ffweight_sum = 0.0
        for gradient in range(self.gradient_level):
            index_map = self.activated_index[gradient]
            the_history_map = self.activated_history[gradient]

            # collect history for each entry
            for coor in index_map.keys():
                x = coor[0]
                y = coor[1]

                # sum up the activation weights
                ffweight_sum += index_map[coor]*the_history_map.update_and_get_ff(x, y, index_map[coor], label)

        # return the sum of frequency factor weight
        return ffweight_sum
