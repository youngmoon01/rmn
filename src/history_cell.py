class history_cell:
    def __init__(self):
        self.history = dict()
        self.total = 0

    def update_and_get_ff(self, count, label):
        self.total += count

        if label in self.history.keys():
            self.history[label] += count
        else:
            self.history[label] = count

        return self.history[label]/self.total

    def get_frequency_factor(self, label):
        if self.total == 0:
            return 1
        if label not in self.history:
            return 0

        return self.history[label]/self.total
