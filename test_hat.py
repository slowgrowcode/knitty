from dsl.Operations import *
from sizing.Gauge import Gauge
from sizing.Measurement import Measurement

def basic_hat(gauge, head_circ_cm, length_cm):
    """
    Define the hat pattern.
    """

    circ_sts = Measurement(
        head_circ_cm,
        gauge,
        is_width=True,
        divisible_by=[4]
    ).to_stitches()

    return Pattern(
        Section("Brim",
            CastOn(circ_sts),
            WorkUntilLength(Ribbing(2,2), 8)
        ),
        Section("Body",
            WorkUntilLength(Ribbing(2,2), length_cm - 8)
        ),
        Section("Crown",
            SimpleCrown(circ_sts)
        )
    )


# --- generate a pattern ---

# Hat Sizing Parameters
gauge = Gauge(rows=21, stitches=13)
circumference = 56
length = 28

# Run
pattern = basic_hat(gauge, circumference, length)
print(pattern.render())