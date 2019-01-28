class gradient_map:
    # static variables
    gradient_level = 0
    gradient_depth = 0
    map_array = None

    def init(gradient_level):
        gradient_level = gradient_level
        gradient_depth = 2*gradient_level + 1

        # x-index: left to right
        # y-index: top to bottom
        map_array = list()
        for i in range(gradient_depth):
            new_list = list()
            for j in range(gradient_depth):
                new_list.append(gradient_cell())
            map_array.append(new_list)

    # return the cell with specified x, y gradient
    def get_cell(x_gradient, y_gradient):
        return map_array[x_gradient][y_gradient]
