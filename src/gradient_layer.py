from cells import cells
from gradient_map import gradient_map
from matching_layer import matching_layer
from matching_cell import matching_cell

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
    @classmethod
    def init(gl, brain_profile):
        # locality related variables
        gl.gradient_locality = brain_profile['gradient_locality']
        gl.gradient_weight = brain_profile['gradient_weight']
        gl.spatial_locality = brain_profile['spatial_locality']
        gl.spatial_weight = brain_profile['spatial_weight']

        gl.gradient_level = brain_profile['gradient_level']
        gl.gradient_step = 256//gl.gradient_level
        gl.layer_depth = brain_profile['layer_depth']


    # analyze gradient of each pixels and get data
    @classmethod
    def process_img(gl, img, output_layer):
        print("Entered process_img")
        img_data = list(img.getdata())
        img_width = img.width
        img_height = img.height

        # configure the image depth
        gl.img_depth = min(img_width - 1, img_height - 1, gl.layer_depth)
        matching_layer.set_img_depth(gl.img_depth)

        gl.layer_width = img_width - 1
        gl.layer_height = img_height - 1

        # initialize the lists
        gl.active_cells = list()
        gl.layer_array = list()
        for x in range(gl.layer_width):
            new_list = list()
            for y in range(gl.layer_height):
                new_list.append(list())
            gl.layer_array.append(new_list)

        # process the image and get gradient information
        for x in range(gl.layer_width):
            for y in range(gl.layer_height):
                x2 = x + 1
                y2 = y + 1

                # extract x gradient
                left = img_data[img_width*x + y] + img_data[img_width*x + y2]
                right = img_data[img_width*x2 + y] + img_data[img_width*x2 + y2]
                x_gradient = (left - right)//(2*gl.gradient_step)

                # extract y gradient
                top = img_data[img_width*x + y] + img_data[img_width*x2 + y]
                bottom = img_data[img_width*x + y2] + img_data[img_width*x2 + y2]
                y_gradient = (top - bottom)//(2*gl.gradient_step)

                # shift gradient values to make them fit into the map index
                x_gradient = x_gradient + 8
                y_gradient = y_gradient + 8

                # spread the processed gradient
                gl.spread_wide(x, y, x_gradient, y_gradient, output_layer)

        # propagate to the matching layer with depth 2
        if gl.img_depth > 1:
            gl.propagate_next(output_layer)


    # spread the processed gradient to the nearest
    @classmethod
    def spread_wide(gl, base_x, base_y, base_xg, base_yg, output_layer):
        # determine the x range
        x_start = max(base_x - gl.spatial_locality, 0)
        x_end = min(base_x + gl.spatial_locality + 1, gl.layer_width)

        for x in range(x_start, x_end):
            # determine the locality diminishing rate
            x_local_rate = 1.0 - gl.spatial_weight*max(x - base_x, base_x - x)
            if x_local_rate <= 0.0:
                continue

            # determine the y range
            y_start = max(base_y - gl.spatial_locality, 0)
            y_end = min(base_y + gl.spatial_locality + 1, gl.layer_height)

            for y in range(y_start, y_end):
                # determine the locality diminishing rate
                y_local_rate = 1.0 - gl.spatial_weight*max(y - base_y, base_y - y)
                if y_local_rate <= 0.0:
                    continue

                # spread gradient-wide
                s_rate = x_local_rate*y_local_rate

                gl.spread_gradient_wide(x, y, s_rate, base_xg, base_yg, output_layer)


    # spread the gradient information gradient-wide
    # s_rate: spatial locality diminishing rate
    @classmethod
    def spread_gradient_wide(gl, x, y, s_rate, base_xg, base_yg, output_layer):
        gradient_depth = 2*gl.gradient_level + 1

        # determine the x_gradient range
        # xg: x_gradient
        xg_start = max(base_xg - gl.gradient_locality, 0)
        xg_end = min(base_xg + gl.gradient_locality + 1, gradient_depth)

        for xg in range(xg_start, xg_end):
            # determine the locality diminishing rate
            xg_local_rate = 1.0 - gl.gradient_weight*max(xg - base_xg, base_xg - xg)
            if xg_local_rate <= 0.0:
                continue

            # determine the y_gradient range
            # yg: y_gradient
            yg_start = max(base_yg - gl.gradient_locality, 0)
            yg_end = min(base_yg + gl.gradient_locality + 1, gradient_depth)

            for yg in range(yg_start, yg_end):
                # determine the locality diminishing rate
                yg_local_rate = 1.0 - gl.gradient_weight*max(yg - base_yg, base_yg - yg)
                if yg_local_rate <= 0.0:
                    continue

                weight = s_rate*xg_local_rate*yg_local_rate

                # add the gradient information to the layer array
                gl.add_gradient_cell(x, y, xg, yg, weight, output_layer)


    # add the active cell if it is not in the active_cells
    @classmethod
    def register_active_cell(gl, cell, weight):
        for item in gl.active_cells:
            if cell == item[0]:
                item[1] += weight
                return

        # if not returned, the cell is unique
        gl.active_cells.append([cell, weight])


    @classmethod
    def get_active_cells(gl):
        return gl.active_cells


    # add gradient cell to the target coordinates
    # xg: x_gradient
    # yg: y_gradient
    @classmethod
    def add_gradient_cell(gl, x, y, xg, yg, weight, output_layer):
        the_cell = gradient_map.get_cell(xg, yg)

        # fire towards the output layer
        the_cell.propagate_output(weight, output_layer)

        # check if the gradient cell already exist
        for item in gl.layer_array[x][y]:
            if the_cell == item[0]:
                gl.register_active_cell(the_cell, weight)
                item[1] += weight
                return

        # if not returned, the cell doesn't exist in this coordinates
        gl.register_active_cell(the_cell, weight)
        gl.layer_array[x][y].append([the_cell, weight])


    # propagate to the matching layer with depth 2
    @classmethod
    def propagate_next(gl, output_layer):
        gl.base_matching_layer = matching_layer(2, gl.layer_width - 1, gl.layer_height - 1)

        for x in range(gl.layer_width - 1):
            for y in range(gl.layer_height - 1):
                x2 = x + 1
                y2 = y + 1

                upper_cell_list = list()

                # tl: top_left
                for tl in gl.layer_array[x][y]:
                    # tr: top_right
                    for tr in gl.layer_array[x2][y]:
                        # bl: bottom_left
                        for bl in gl.layer_array[x][y2]:
                            # br: bottom_right
                            for br in gl.layer_array[x2][y2]:
                                ret = cells.get_upper_link(tl[0], tr[0], bl[0], br[0])
                                if ret != None:
                                    weight = tl[1]*tr[1]*bl[1]*br[1]
                                    upper_cell_list.append([ret, weight])


                # spread the matching cells(spatial locality)
                gl.matching_cell_spread(x, y, upper_cell_list, output_layer)

        # propagate deeper
        if gl.img_depth > 2:
            gl.base_matching_layer.propagate_next(output_layer)


    # spread the matching cells(spatial locality)
    @classmethod
    def matching_cell_spread(gl, base_x, base_y, cell_list, output_layer):
        # determine the x range
        x_start = max(base_x - gl.spatial_locality, 0)
        x_end = min(base_x + gl.spatial_locality + 1, gl.layer_width - 1)

        # determine the y range
        for x in range(x_start, x_end):
            # determine the locality diminishing rate
            x_local_rate = 1.0 - gl.spatial_weight*max(x - base_x, base_x - x)
            if x_local_rate <= 0.0:
                continue

            # determine the y range
            y_start = max(base_y - gl.spatial_locality, 0)
            y_end = min(base_y + gl.spatial_locality + 1, gl.layer_height - 1)

            for y in range(y_start, y_end):
                # determine the locality diminishing rate
                y_local_rate = 1.0 - gl.spatial_weight*max(y - base_y, base_y - y)
                if y_local_rate <= 0.0:
                    continue

                # spatial locality weight
                s_rate = x_local_rate*y_local_rate

                #item[0]: cell
                #item[1]: weight
                for item in cell_list:
                    # add the matching cell to the matching layer
                    weight = item[1]*s_rate
                    gl.base_matching_layer.add_matching_cell(x, y, item[0], weight, output_layer)


    # detect the new cells candidate
    @classmethod
    def detect_new_cells(gl, img, label, new_cells):
        new_cell_count = 0

        img_data = list(img.getdata())
        img_width = img.width
        img_height = img.height

        # initialize the array
        gl.new_cell_array = list()
        for x in range(gl.layer_width):
            gl.new_cell_array.append(list())

        # process the image and get gradient information
        for x in range(gl.layer_width):
            for y in range(gl.layer_height):
                x2 = x + 1
                y2 = y + 1

                # extract x gradient
                left = img_data[img_width*x + y] + img_data[img_width*x + y2]
                right = img_data[img_width*x2 + y] + img_data[img_width*x2 + y2]
                x_gradient = (left - right)//(2*gl.gradient_step)

                # extract y gradient
                top = img_data[img_width*x + y] + img_data[img_width*x2 + y]
                bottom = img_data[img_width*x + y2] + img_data[img_width*x2 + y2]
                y_gradient = (top - bottom)//(2*gl.gradient_step)

                # shift gradient values to make them fit into the map index
                x_gradient = x_gradient + 8
                y_gradient = y_gradient + 8
                the_cell = gradient_map.get_cell(x_gradient, y_gradient)

                # add the gradient cell into the new cell array
                gl.new_cell_array[x].append(the_cell)

        if gl.img_depth > 1:
            new_cell_count += gl.detect_new_cells_next(label, new_cells)

        return new_cell_count

    @classmethod
    def detect_new_cells_next(gl, label, new_cells):
        new_cell_count = 0

        # initialize the new cell array of upper layer
        gl.base_matching_layer.detect_new_cells_ready()

        layer_new_cells = list()
        for x in range(gl.layer_width - 1):
            for y in range(gl.layer_height - 1):
                x2 = x + 1
                y2 = y + 1

                # check if next cell is a new cell
                #tl: top-left
                #tr: top-right
                #bl: bottom-left
                #br: bottom-right
                tl = gl.new_cell_array[x][y]
                tr = gl.new_cell_array[x2][y]
                bl = gl.new_cell_array[x][y2]
                br = gl.new_cell_array[x2][y2]
                upper_cell = cells.get_upper_link(tl, tr, bl, br)

                # this is new cell
                if upper_cell == None:
                    # generate new matching cell
                    upper_cell = matching_cell(tl, tr, bl, br)

                    # link new matching cell to the child
                    tl.add_uplink(0, 0, upper_cell)
                    tr.add_uplink(1, 0, upper_cell)
                    bl.add_uplink(0, 1, upper_cell)
                    br.add_uplink(1, 1, upper_cell)

                    # register the upper link
                    cells.register_upper_link(upper_cell, tl, tr, bl, br)

                    # update the history
                    upper_cell.update_history(label, 1)

                    layer_new_cells.append(upper_cell)
                    new_cell_count += 1
                else:
                    # check if the upper cell is in new_cells list
                    for item in layer_new_cells:
                        if upper_cell == item: # this is new cell
                            # raise the new cell count
                            new_cell_count += 1

                            # update the history
                            upper_cell.update_history(label, 1)

                gl.base_matching_layer.update_new_cell_array(x, y, upper_cell)

        # add set of new cells to new_cells
        new_cells.append(layer_new_cells)

        # detect new cells in the next layer
        if gl.img_depth > 2:
            new_cell_count += gl.base_matching_layer.detect_new_cells_next(label, new_cells)

        return new_cell_count


    @classmethod
    def update_history(gl, label):
        weight_sum = 0.0

        # item[0]: cell
        # item[1]: cumulative weight
        for item in gl.active_cells:
            item[0].update_history(label, item[1])
            weight_sum += item[1]*item[0].get_frequency_factor(label)

        if gl.img_depth > 2:
            weight_sum += gl.base_matching_layer.update_history(label)

        return weight_sum


    # ffw: frequency-factor weight
    @classmethod
    def active_cells_feedback(gl, output, ffw):
        for item in gl.active_cells:
            item[0].feedback(output, ffw*item[0].get_frequency_factor(output))

        if gl.img_depth > 2:
            gl.base_matching_layer.active_cells_feedback(output, ffw)
