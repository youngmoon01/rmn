from gradient_cell import gradient_cell

class gradient_map:
    # static variables
    gradient_level = 0
    gradient_depth = 0
    map_array = None

    @classmethod
    def init(gm, gradient_level):
        gm.gradient_level = gradient_level
        gm.gradient_depth = 2*gradient_level + 1

        # x-index: left to right
        # y-index: top to bottom
        gm.map_array = list()
        for i in range(gm.gradient_depth):
            new_list = list()
            for j in range(gm.gradient_depth):
                new_list.append(gradient_cell())
            gm.map_array.append(new_list)

    # return the cell with specified x, y gradient
    @classmethod
    def get_cell(gm, x_gradient, y_gradient):
        return gm.map_array[x_gradient][y_gradient]
