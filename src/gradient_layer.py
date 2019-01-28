from gradient_map import gradient_map

class gradient_layer:
    # static variables
    gradient_locality = 0
    gradient_weight = 0.1
    spatial_locality = 0
    spatial_weight = 0.1

    gradient_level = 8
    gradient_step = 256//gradient_level

    # image specific depth
    img_depth = 1

    layer_depth = 1
    layer_width = 0
    layer_height = 0

    # the elements of layer array is a list in a form [gradient_cell, weight]
    layer_array = None

    # unique set of activated cells
    active_cells = None
    new_cell_array = None

    base_matching_layer = None


    # initialize the static variables
    def init(brain_profile):
        # locality related variables
        gradient_locality = brain_profile['gradient_locality']
        gradient_weight = brain_profile['gradient_weight']
        spatial_locality = brain_profile['spatial_locality']
        spatial_weight = brain_profile['spatial_weight']

        gradient_level = brain_profile['gradient_level']
        gradient_step = 256//gradient_level
        layer_depth = brain_profile['layer_depth']


    # analyze gradient of each pixels and get data
    def process_img(img, output_layer):
        weight_sum = 0.0

        img_data = list(img.getdata())
        img_width = img.width
        img_height = img.height

        # configure the image depth
        img_depth = min(img_width - 1, img_height - 1, layer_depth)
        matching_layer.set_img_depth(img_depth)

        layer_width = img_width - 1
        layer_height = img_height - 1

        # initialize the lists
        active_cells = list()
        layer_array = list()
        for x in range(layer_width):
            new_list = list()
            for y in range(layer_height):
                new_list.append(list())
            layer_array.append(new_list)

        # process the image and get gradient information
        for x in range(layer_width):
            for y in range(layer_height):
                x2 = x + 1
                y2 = y + 1

                # extract x gradient
                left = img_data[img_width*x + y] + img_data[img_width*x + y2]
                right = img_data[img_width*x2 + y] + img_data[img_width*x2 + y2]
                x_gradient = (left - right)//(2*gradient_step)

                # extract y gradient
                top = img_data[img_width*x + y] + img_data[img_width*x2 + y]
                bottom = img_data[img_width*x + y2] + img_data[img_width*x2 + y2]
                y_gradient = (top - bottom)//(2*gradient_step)

                # shift gradient values to make them fit into the map index
                x_gradient = x_gradient + 8
                y_gradient = y_gradient + 8

                # spread the processed gradient
                weight_sum += spread_wide(x, y, x_gradient, y_gradient, output_layer)

        # propagate to the matching layer with depth 2
        if img_depth > 1:
            weight_sum += propagate_next(output_layer)

        return weight_sum


    # spread the processed gradient to the nearest
    def spread_wide(base_x, base_y, base_xg, base_yg, output_layer):
        weight_sum = 0.0

        # determine the x range
        x_start = max(base_x - spatial_locality, 0)
        x_end = min(base_x + spatial_locality + 1, layer_width)

        for x in range(x_start, x_end):
            # determine the locality diminishing rate
            x_local_rate = 1.0 - spatial_weight*max(x - base_x, base_x - x)
            if x_local_rate <= 0.0:
                continue

            # determine the y range
            y_start = max(base_y - spatial_locality, 0)
            y_end = min(base_y + spatial_locality + 1, layer_height)

            for y in range(y_start, y_end):
                # determine the locality diminishing rate
                y_local_rate = 1.0 - spatial_weight*max(y - base_y, base_y - y)
                if y_local_rate <= 0.0:
                    continue

                # spread gradient-wide
                s_rate = x_local_rate*y_local_rate

                weight_sum += spread_gradient_wide(x, y, s_rate, base_xg, base_yg, output_layer)

        return weight_sum


    # spread the gradient information gradient-wide
    # s_rate: spatial locality diminishing rate
    def spread_gradient_wide(x, y, s_rate, base_xg, base_yg, output_layer):
        weight_sum = 0.0

        gradient_depth = 2*gradient_level + 1

        # determine the x_gradient range
        # xg: x_gradient
        xg_start = max(base_xg - gradient_locality, 0)
        xg_end = min(base_xg + gradient_locality + 1, gradient_depth)

        for xg in range(xg_start, xg_end):
            # determine the locality diminishing rate
            xg_local_rate = 1.0 - gradient_weight*max(xg - base_xg, base_xg - xg)
            if xg_local_rate <= 0.0:
                continue

            # determine the y_gradient range
            # yg: y_gradient
            yg_start = max(base_yg - gradient_locality, 0)
            yg_end = min(base_yg + gradient_locality + 1, gradient_depth)

            for yg in range(yg_start, yg_end):
                # determine the locality diminishing rate
                yg_local_rate = 1.0 - gradient_weight*max(yg - base_yg, base_yg - yg)
                if yg_local_rate <= 0.0:
                    continue

                weight = s_rate*xg_local_rate*yg_local_rate
                weight_sum += weight

                # add the gradient information to the layer array
                add_gradient_cell(x, y, xg, yg, weight, output_layer)

        return weight_sum


    # add the active cell if it is not in the active_cells
    def register_active_cell(cell, weight):
        for item in active_cells:
            if cell == item[0]:
                item[1] += weight
                return

        # if not returned, the cell is unique
        active_cells.append([cell, weight])


    def get_active_cells():
        return active_cells


    # add gradient cell to the target coordinates
    # xg: x_gradient
    # yg: y_gradient
    def add_gradient_cell(x, y, xg, yg, weight, output_layer):
        the_cell = gradient_map.get_cell(xg, yg)

        # fire towards the output layer
        for output in the_cell.output_weights.keys():
            if output in output_layer:
                output_layer[output] += the_cell.output_weights[output]
            else:
                output_layer[output] = the_cell.output_weights[output]

        # check if the gradient cell already exist
        for item in layer_array[x][y]:
            if the_cell == item[0]:
                print("Gradient cell hit. Let's remove this after checking this message pops up.")
                register_active_cell(the_cell, weight)
                item[1] += weight
                return

        # if not returned, the cell doesn't exist in this coordinates
        register_active_cell(the_cell, weight)
        layer_array[x][y].append([the_cell, weight])


    # propagate to the matching layer with depth 2
    def propagate_next(output_layer):
        weight_sum = 0.0

        base_matching_layer = matching_layer(2, layer_width - 1, layer_height - 1)

        for x in range(layer_width - 1):
            for y in range(layer_height - 1):
                x2 = x + 1
                y2 = y + 1

                candidate_list = list()

                # add candidates to the list
                add_candidates(layer_array[x][y], candidate_list)

                # filter candidates with rest of 3 up links
                candidate_list = filter_candidates(layer_array[x2][y], candidate_list, 1, 0)
                candidate_list = filter_candidates(layer_array[x][y2], candidate_list, 0, 1)
                matching_cell_list = filter_candidates(layer_array[x2][y2], candidate_list, 1, 1)

                # spread the matching cells(spatial locality)
                weight_sum += matching_cell_spread(x, y, matching_cell_list, output_layer)

        # propagate deeper
        if img_depth > 2:
            weight_sum += base_matching_layer.propagate_next(output_layer)

        return weight_sum


    # spread the matching cells(spatial locality)
    def matching_cell_spread(base_x, base_y, cell_list, output_layer):
        weight_sum = 0.0

        # determine the x range
        x_start = max(base_x - spatial_locality, 0)
        x_end = min(base_x + spatial_locality + 1, layer_width - 1)

        # determine the y range
        for x in range(x_start, x_end):
            # determine the locality diminishing rate
            x_local_rate = 1.0 - spatial_weight*max(x - base_x, base_x - x)
            if x_local_rate <= 0.0:
                continue

            # determine the y range
            y_start = max(base_y - spatial_locality, 0)
            y_end = min(base_y + spatial_locality + 1, layer_height - 1)

            for y in range(y_start, y_end):
                # determine the locality diminishing rate
                y_local_rate = 1.0 - spatial_weight*max(y - base_y, base_y - y)
                if y_local_rate <= 0.0:
                    continue

                # spatial locality weight
                s_rate = x_local_rate*y_local_rate

                #item[0]: cell
                #item[1]: weight
                for item in cell_list:
                    # add the matching cell to the matching layer
                    weight = item[1]*s_rate
                    weight_sum += weight
                    base_matching_layer.add_matching_cell(x, y, item[0], weight, output_layer)

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


    # detect the new cells candidate
    def detect_new_cells(img, label, new_cells):
        img_data = list(img.getdata())
        img_width = img.width
        img_height = img.height

        # initialize the array
        new_cell_array = list()
        for x in range(layer_width):
            new_cell_array.append(list())

        # process the image and get gradient information
        for x in range(layer_width):
            for y in range(layer_height):
                x2 = x + 1
                y2 = y + 1

                # extract x gradient
                left = img_data[img_width*x + y] + img_data[img_width*x + y2]
                right = img_data[img_width*x2 + y] + img_data[img_width*x2 + y2]
                x_gradient = (left - right)//(2*gradient_step)

                # extract y gradient
                top = img_data[img_width*x + y] + img_data[img_width*x2 + y]
                bottom = img_data[img_width*x + y2] + img_data[img_width*x2 + y2]
                y_gradient = (top - bottom)//(2*gradient_step)

                # shift gradient values to make them fit into the map index
                x_gradient = x_gradient + 8
                y_gradient = y_gradient + 8
                the_cell = gradient_map.get_cell(x_gradient, y_gradient)

                # add the gradient cell into the new cell array
                new_cell_array[x].append(the_cell)

        if img_depth > 1:
            new_cell_count += detect_new_cells_next(label, new_cells)
        return new_cell_count

    def detect_new_cells_next(label, new_cells):
        new_cell_count = 0

        # initialize the new cell array of upper layer
        base_matching_layer.detect_new_cells_ready()

        layer_new_cells = list()
        for x in range(layer_width - 1):
            for y in range(layer_height - 1):
                x2 = x + 1
                y2 = y + 1

                # check if next cell is a new cell
                is_cell_new = True
                upper_cell = None
                for cell in new_cell_array[x][y].get_up_links(0, 0):
                    if cell.get_child(1, 0) != new_cell_array[x2][y]:
                        continue
                    if cell.get_child(0, 1) != new_cell_array[x][y2]:
                        continue
                    if cell.get_child(1, 1) != new_cell_array[x2][y2]:
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
                    top_left = new_cell_array[x][y]
                    top_right = new_cell_array[x2][y]
                    bottom_left = new_cell_array[x][y2]
                    bottom_right = new_cell_array[x2][y2]

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

                base_matching_layer.update_new_cell_array(x, y, upper_cell)

        # add set of new cells to new_cells
        new_cells.append(layer_new_cells)

        # detect new cells in the next layer
        if img_depth > 2:
            new_cell_count += base_matching_layer.detect_new_cells_next(new_cells)

        return new_cell_count


    def update_history(label):
        # item[0]: cell
        # item[1]: cumulative weight
        for item in active_cells:
            item[0].update_history(label, item[1])

        if img_depth > 2:
            base_matching_layer.update_history(label)




































    def activate_cell(self, x, y, output_layer):
        weights = self.gradient_cell_map[x][y]
        for output in weights.keys():
            if output in output_layer:
                output_layer[output] += weights[output]
            else:
                output_layer[output] = weights[output]

    def weight_update(self, coor, update_amount, output):
        x = coor[0]
        y = coor[1]

        if output in self.gradient_cell_map[x][y]:
            self.gradient_cell_map[x][y][output] += update_amount
        else:
            self.gradient_cell_map[x][y][output] = update_amount
