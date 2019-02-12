import numpy
from matching_cell import matching_cell

class matching_layer:
    # static variables related to the locality 
    gradient_locality = 1
    gradient_weight = 0.1

    spatial_locality = 1
    spatial_weight = 0.1

    img_depth = 1
    layer_depth = 1


    # initialize the static variables according to the brain profile
    @classmethod
    def init(ml, brain_profile):
        ml.gradient_locality = brain_profile['gradient_locality']
        ml.gradient_weight = brain_profile['gradient_weight']
        ml.spatial_locality = brain_profile['spatial_locality']
        ml.spatial_weight = brain_profile['spatial_weight']
        ml.layer_depth = brain_profile['layer_depth']


    @classmethod
    def set_img_depth(ml, num):
        ml.img_depth = num


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
        cell.propagate_output(weight, output_layer)

        # check if the matching cell already exist
        for item in self.layer_array[x][y]:
            if cell == item[0]:
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
        print("Entered propagate_next: " + str(self.depth))

        self.next_layer = matching_layer(self.depth + 1, self.layer_width - 1, self.layer_height - 1)

        for x in range(self.layer_width - 1):
            for y in range(self.layer_height - 1):
                x2 = x + 1
                y2 = y + 1

                upper_cell_list = list()

                # tl: top_left
                for tl in self.layer_array[x][y]:
                    # tr: top_right
                    for tr in self.layer_array[x2][y]:
                        # bl: bottom_left
                        for bl in self.layer_array[x][y2]:
                            # br: bottom_right
                            for br in self.layer_array[x2][y2]:
                                ret = cells.get_upper_link(tl[0], tr[0], bl[0], br[0])
                                if ret != None:
                                    weight = tl[1]*tr[1]*bl[1]*br[1]
                                    upper_cell_list.append([ret, weight])

                # spread the matching cells(spatial locality)
                self.matching_cell_spread(x, y, upper_cell_list, output_layer)

        # propagate deeper
        if self.img_depth > self.depth:
            self.next_layer.propagate_next(output_layer)


    # spread the matching cells(spatial locality)
    def matching_cell_spread(self, base_x, base_y, cell_list, output_layer):
        # determine the x range
        x_start = max(base_x - self.spatial_locality, 0)
        x_end = min(base_x + self.spatial_locality + 1, self.layer_width - 1)

        # determine the y range
        for x in range(x_start, x_end):
            # determine the locality diminishing rate
            x_local_rate = 1.0 - self.spatial_weight*max(x - base_x, base_x - x)
            if x_local_rate <= 0.0:
                continue

            # determine the y range
            y_start = max(base_y - self.spatial_locality, 0)
            y_end = min(base_y + self.spatial_locality + 1, self.layer_height - 1)

            for y in range(y_start, y_end):
                # determine the locality diminishing rate
                y_local_rate = 1.0 - self.spatial_weight*max(y - base_y, base_y - y)
                if y_local_rate <= 0.0:
                    continue

                # spatial locality weight
                s_local_rate = x_local_rate*y_local_rate

                #item[0]: cell
                #item[1]: weight
                for item in cell_list:
                    # add the matching cell to the matching layer
                    weight = item[1]*s_local_rate
                    self.next_layer.add_matching_cell(x, y, item[0], weight, output_layer)


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
        for x in range(self.layer_width - 1):
            for y in range(self.layer_height - 1):
                x2 = x + 1
                y2 = y + 1

                # check if next cell is a new cell
                #tl: top-left
                #tr: top-right
                #bl: bottom-left
                #br: bottom-right
                tl = self.new_cell_array[x][y]
                tr = self.new_cell_array[x2][y]
                bl = self.new_cell_array[x][y2]
                br = self.new_cell_array[x2][y2]
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

                self.next_layer.update_new_cell_array(x, y, upper_cell)

        # add set of new cells to new_cells
        new_cells.append(layer_new_cells)

        # detect new cells in the next layer
        if self.img_depth > self.depth:
            new_cell_count += self.next_layer.detect_new_cells_next(label, new_cells)

        return new_cell_count


    def update_new_cell_array(self, x, y, cell):
        self.new_cell_array[x][y] = cell


    def update_history(self, label):
        weight_sum = 0.0

        # item[0]: cell
        # item[1]: cumulative weight
        for item in self.active_cells:
            item[0].update_history(label, item[1])
            weight_sum += item[1]*item[0].get_frequency_factor(label)

        if self.img_depth > self.depth:
            weight_sum += self.next_layer.update_history(label)

        return weight_sum


    def active_cells_feedback(self, output, ffw):
        for item in self.active_cells:
            item[0].feedback(output, ffw*item[0].get_frequency_factor(output))

        if self.img_depth > self.depth:
            self.next_layer.active_cells_feedback(output, ffw)
