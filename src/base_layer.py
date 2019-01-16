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

        # calculate derived parameters
        self.base_layer_depth = 2*self.gradient_level + 1

        # activated history to apply frequency weight
        self.activated_history = list()
        for gradient in range(self.base_layer_depth):
            self.activated_history.append(history_map(self.f_width, self.f_height))

        # activated_index accelerates learning-related calculation
        self.activated_count = 0
        self.activated_index = list()
        for num in range(self.base_layer_depth):
            self.activated_index.append(dict())

        # generate gradient layers
        self.gradient_layers = list()
        for gradient in range(-self.gradient_level, self.gradient_level + 1):
            self.gradient_layers.append(gradient_layer(self.f_width, self.f_height, gradient))

    def activate_cell(self, x, y, gradient, output_layer):
        # update activated index to accelerates learning-related calculation
        map_index = gradient + self.gradient_level
        index_map = self.activated_index[map_index]

        self.activated_count += 1

        # log to index map
        if (x, y) in index_map:
            index_map[(x, y)] += 1
        else:
            index_map[(x, y)] = 1

        # activate weights
        self.gradient_layers[map_index].activate_cell(x, y, output_layer)

    def clear_activated_index(self):
        # clear and re-initialize the activated index
        del self.activated_index

        self.activated_count = 0
        self.activated_index = list()
        for num in range(self.base_layer_depth):
            self.activated_index.append(dict())

    def weight_update(self, feedback_list, label):
        count = self.activated_count
        for item in feedback_list:
            output = item[0]
            difference = item[1]
            update_amount = difference/count

            for gradient in range(len(self.activated_index)):
                index_map = self.activated_index[gradient]
                the_layer = self.gradient_layers[gradient]

                for coor in index_map.keys():
                    # weight updates
                    the_layer.weight_update(coor, update_amount, output)

    def collect_history(self, label):
        weight_sum = 0.0
        for gradient in range(self.base_layer_depth):
            index_map = self.activated_index[gradient]
            the_history_map = self.activated_history[gradient]

            # collect history for each entry
            for coor in index_map.keys():
                x = coor[0]
                y = coor[1]
                # sum up the activation weights
                weight_sum += the_history_map.update_and_get_ff(x, y, index_map[coor], label)
