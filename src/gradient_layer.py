class gradient_layer:
    # filter width, height and gradient index
    def __init__(self, f_width, f_height, g_index):
        self.f_width = f_width
        self.f_height = f_height
        self.g_index = g_index

        # initialize gradient cell map
        self.gradient_cell_map = list()
        for i in range(2*f_width + 1):
            new_list = list()
            for j in range(f_height + 1):
                new_list.append(dict())

            self.gradient_cell_map.append(new_list)

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
