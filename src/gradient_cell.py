class gradient_cell:
    def __init__(self):
        # links to upper matching layer
        # 2x2 array of lists
        self.up_links = list()
        for i in range(2):
            new_list = list()
            for j in range(2):
                new_list.append(list())
            self.up_links.append(new_list())

        # initialize history map
        self.history_map = dict()
        self.history_total = 0.0

        # initialize output weights
        self.output_weights = dict()


    def get_up_links(self, x, y):
        return self.up_links[x][y]


    def add_uplink(self, x, y, cell):
        self.up_links[x][y].append(cell)


    def get_frequency_factor(label):
        if label not in self.history_map:
            return 0.0
        else:
            return self.history_map[label]/self.history_total


    def update_history(self, label, weight):
        if label in self.history_map:
            self.history_map[label] += weight
        else:
            self.history_map[label] = weight

        self.history_total += weight
