class matching_layer:
    # static variables related to the locality 
    gradient_locality = 1
    gradient_weight = 0.1

    spatial_locality = 1
    spatial_weight = 0.1

    img_depth = 1
    layer_depth = 1


    # initialize the static variables according to the brain profile
    def init(brain_profile):
        gradient_locality = brain_profile['gradient_locality']
        gradient_weight = brain_profile['gradient_weight']
        spatial_locality = brain_profile['spatial_locality']
        spatial_weight = brain_profile['spatial_weight']
        layer_depth = brain_profile['layer_depth']


    def set_img_depth(num):
        img_depth = num


    def __init__(self, depth, layer_width, layer_height):
        self.depth = depth
        self.layer_width = layer_width
        self.layer_height = layer_height
        self.next_layer = None

        # initialize the layer array
        self.active_cells = list()
        self.layer_array = list()
        for i in range(layer_width):
            new_list = list()
            for j in range(layer_height):
                new_list.append(list())
            self.layer_array.append(new_list)


    def add_matching_cell(self, x, y, cell, weight, output_layer):
        # fire towards the output layer
        for output in cell.output_weights.keys():
            if output in output_layer:
                output_layer[output] += the_cell.output_weights[output]
            else:
                output_layer[output] = the_cell.output_weights[output]

        # check if the matching cell already exist
        for item in self.layer_array[x][y]:
            if cell == item[0]:
                print("Matching cell hit. Let's remove this after checking this message pops up.")
                self.register_active_cell(cell, weight)
                item[1] += weight
                return

        # if not returned, the cell doesn't exist in this coordinates
        self.register_active_cell(cell, weight)
        self.layer_array[x][y].append([cell, weight])


    # add the active cell if it is not in the active_cells
    def register_active_cell(self, cell, weight):
        for item in self.active_cells:
            if cell == item[0]:
                item[1] += weight
                return

        # if not returned, the cell is unique
        self.active_cells.append([cell, weight])


    def get_active_cells(self):
        return self.active_cells


    def propagate_next(self, output_layer):
        weight_sum = 0.0

        self.next_layer = matching_layer(self.depth + 1, self.layer_width - 1, self.layer_height - 1)

        for x in range(self.layer_width - 1):
            for y in range(self.layer_height - 1):
                x2 = x + 1
                y2 = y + 1

                candidate_list = list()

                # add candidates to the list
                self.add_candidates(self.layer_array[x][y], candidate_list)

                # filter candidates with rest of 3 up links
                candidate_list = self.filter_candidates(self.layer_array[x2][y], candidate_list, 1, 0)
                candidate_list = self.filter_candidates(self.layer_array[x][y2], candidate_list, 0, 1)
                matching_cell_list = self.filter_candidates(self.layer_array[x2][y2], candidate_list, 1, 1)

                # spread the matching cells(spatial locality)
                weight_sum += self.matching_cell_spread(x, y, matching_cell_list, output_layer)

        # propagate deeper
        if img_depth > self.depth:
            weight_sum += self.next_layer.propagate_next(output_layer)

        return weight_sum


    # spread the matching cells(spatial locality)
    def matching_cell_spread(self, base_x, base_y, cell_list, output_layer):
        weight_sum = 0.0

        # determine the x range
        x_start = max(base_x - spatial_locality, 0)
        x_end = min(base_x + spatial_locality + 1, self.layer_width - 1)

        # determine the y range
        for x in range(x_start, x_end):
            # determine the locality diminishing rate
            x_local_rate = 1.0 - spatial_weight*max(x - base_x, base_x - x)
            if x_local_rate <= 0.0:
                continue

            # determine the y range
            y_start = max(base_y - spatial_locality, 0)
            y_end = min(base_y + spatial_locality + 1, self.layer_height - 1)

            for y in range(y_start, y_end):
                # determine the locality diminishing rate
                y_local_rate = 1.0 - spatial_weight*max(y - base_y, base_y - y)
                if y_local_rate <= 0.0:
                    continue

                # spatial locality weight
                s_local_rate = x_local_rate*y_local_rate

                #item[0]: cell
                #item[1]: weight
                for item in cell_list:
                    # add the matching cell to the matching layer
                    weight = item[1]*s_local_rate
                    wiehgt_sum += weight
                    self.next_layer.add_matching_cell(x, y, item[0], weight, output_layer)

        return weight_sum


    # generate upper-layer candidate cells with top-left up-links
    # of current layer cells
    def add_candidates(item_array, candidate_list):
        for item in item_array: # item[0]: gradient_cell, item[1]: weight
            for cell in item[0].get_up_links(0, 0):
                # add cell and weight
                candidate_list.append([cell, item[1]])


    # filter candidates with specified up-links
    # up_x : x value of up links
    # up_y : y value of up links
    def filter_candidates(item_array, candidate_list, up_x, up_y):
        new_candidate_list = list()

        for candidate in candidate_list:
            matching_target = candidate[0].get_child(up_x, up_y)

            for item in item_array:
                if matching_target == item[0]: # matched. pass the filter
                    new_weight = candidate[1]*item[1]
                    new_candidate_list.append([matching_target, new_weight])
                    break
        return new_candidate_list


    # initialize the new cell array of upper layer
    def detect_new_cells_ready(self):
        self.new_cell_array = list()
        for i in range(self.layer_width):
            new_list = list()
            for j in range(self.layer_height):
                new_list.append(None)
            self.new_cell_array.append(new_list)


    # detect new set of cells in the next layer
    def detect_new_cells_next(self, label, new_cells):
        new_cell_count = 0

        # initialize the new cell array of upper layer
        self.next_layer.detect_new_cells_ready()

        layer_new_cells = list()
        for x in range(layer_width - 1):
            for y in range(layer_height - 1):
                x2 = x + 1
                y2 = y + 1

                # check if next cell is a new cell
                is_cell_new = True
                upper_cell = None
                for cell in self.new_cell_array[x][y].get_up_links(0, 0):
                    if cell.get_child(1, 0) != self.new_cell_array[x2][y]:
                        continue
                    if cell.get_child(0, 1) != self.new_cell_array[x][y2]:
                        continue
                    if cell.get_child(1, 1) != self.new_cell_array[x2][y2]:
                        continue

                    upper_cell = cell
                    # check if the upper cell is in new_cells list
                    for item in layer_new_cells:
                        if upper_cell == item[0]: # this is new cell
                            # raise the count of new cell
                            item[1] += 1
                            new_cell_count += 1

                            # update the history
                            upper_cell.update_history(label, 1)

                    is_cell_new = False
                    break

                # generate new cell
                if is_cell_new:
                    top_left = self.new_cell_array[x][y]
                    top_right = self.new_cell_array[x2][y]
                    bottom_left = self.new_cell_array[x][y2]
                    bottom_right = self.new_cell_array[x2][y2]

                    # generate new matching cell
                    upper_cell = matching_cell(top_left, top_right, bottom_left, bottom_right)

                    # link new matching cell to the child
                    top_left.add_uplink(0, 0, upper_cell)
                    top_right.add_uplink(1, 0, upper_cell)
                    bottom_left.add_uplink(0, 1, upper_cell)
                    bottom_right.add_uplink(1, 1, upper_cell)

                    # update the history
                    upper_cell.update_history(label, 1)

                    layer_new_cells.append([upper_cell, 1])
                    new_cell_count += 1

                self.next_layer.update_new_cell_array(x, y, upper_cell)

        # add set of new cells to new_cells
        new_cells.append(layer_new_cells)

        # detect new cells in the next layer
        if img_depth > self.depth:
            new_cell_count += self.next_layer.detect_new_cells_next(new_cells)

        return new_cell_count


    def update_new_cell_array(self, x, y, cell):
        self.new_cell_array[x][y] = cell

    def update_history(label):
        # item[0]: cell
        # item[1]: cumulative weight
        for item in active_cells:
            item[0].update_history(label, item[1])

        if img_depth > self.depth:
            self.next_layer.update_history(label)
