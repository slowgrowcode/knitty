from math import gcd

class Measurement:
    def __init__(
        self,
        cm,
        gauge,
        *,
        is_width=True,
        divisible_by=None,
        rounding="nearest"
    ):
        self.cm = cm
        self.gauge = gauge
        self.is_width = is_width
        self.divisible_by = divisible_by or []
        self.rounding = rounding

    def to_stitches(self):
        """
        Convert length measurement to stitch count based on constraint options.
        """
        raw = self._raw_stitches()
        return self._apply_constraints(raw)

    
    def _raw_stitches(self):
        """
        Convert with row or column gauge as required.
        """
        if self.is_width:
            return self.cm * self.gauge.stitches_per_cm()
        return self.cm * self.gauge.rows_per_cm()
    
    def _apply_constraints(self, value):
        """
        Apply rounding constraint options.
        """
        if not self.divisible_by:
            return round(value)

        step = self._lcm(self.divisible_by)

        up = int(value + (step - value % step))
        down = int(value - (value % step))

        if self.rounding == "up":
            return up
        elif self.rounding == "down":
            return down
        else:
            return self._closest(value, up, down)

    def _closest(self, target, up, down):
        return up if abs(up - target) < abs(down - target) else down

    def _lcm(self, nums):
        """
        If we need a divisor, get as close as possible.
        """
        lcm = 1
        for n in nums:
            lcm = lcm * n // gcd(lcm, n)
        return lcm
    
    def error_percent(self):
        """
        Expose error due to applying constraints.
        """
        actual_stitches = self.to_stitches()
        actual_cm = (
            actual_stitches / self.gauge.stitches_per_cm()
            if self.is_width
            else actual_stitches / self.gauge.rows_per_cm()
        )
        return abs(actual_cm - self.cm) / self.cm * 100
    
    def true_measurement(self):
        """
        Expose true measurement after applying constraints.
        """
        actual_stitches = self.to_stitches()
        actual_cm = (
            actual_stitches / self.gauge.stitches_per_cm()
            if self.is_width
            else actual_stitches / self.gauge.rows_per_cm()
        )
        return actual_cm