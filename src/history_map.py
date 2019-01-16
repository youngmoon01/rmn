from history_cell import history_cell

class history_map:
    def __init__(self, f_width, f_height):
        self.f_width = f_width
        self.f_height = f_height

        # initialize history map
        self.map = list()
        for i in range(2*f_width + 1):
            new_list = list()
            for j in range(f_height + 1):
                new_list.append(history_cell())

            self.map.append(new_list)

    # update and get the frequency factor
    def update_and_get_ff(self, x, y, count, label):
        self.map[x][y].update(count, label)

    def get_frequency_factor(self, x, y, label):
        return self.map([x][y].get_frequency_factor(label)
