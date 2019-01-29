class cells:

    # global cell id
    cell_next_id = 0

    uplink_hash = dict()

    # return None if there is no upper link
    @classmethod
    def get_upper_link(c, top_left, top_right, bottom_left, bottom_right):
        try:
            return c.uplink_hash[top_left][top_right][bottom_left][bottom_right]
        except KeyError:
            return None

    @classmethod
    def register_upper_link(c, upper_cell, top_left, top_right, bottom_left, bottom_right):
        hashing = None
        try:
            hashing = c_uplink_hash[top_left.get_id()]
        except KeyError:
            c.uplink_hash[top_left.get_id()] = dict()
            hashing = c_uplink_hash[top_left.get_id()]

        try:
            hashing = hashing[top_right.get_id()]
        except KeyError:
            hashing[top_right.get_id()] = dict()
            hashing = hashing[top_right.get_id()]

        try:
            hashing = hashing[bottom_left.get_id()]
        except KeyError:
            hashing[bottom_left.get_id()] = dict()
            hashing = hashing[bottom_left.get_id()]

        if bottom_right.get_id() not in hashing:
            hashing[bottom_right.get_id()] = upper_cell
        else:
            print("The upper cell already registered. Debug this.")
        

    # increment the id and return the next cell id
    @classmethod
    def request_cell_id(c):
        ret = c.cell_next_id
        c.cell_next_id += 1
        return ret
