class Gauge:
    def __init__(self, rows, stitches):
        self.rows_per_10cm = rows
        self.stitches_per_10cm = stitches

    def stitches_per_cm(self):
        return self.stitches_per_10cm / 10

    def rows_per_cm(self):
        return self.rows_per_10cm / 10