from dsl.Operations import *
from sizing.Gauge import Gauge
from sizing.Measurement import Measurement

def ribbed_hat(gauge, head_circ_cm, length_cm):
    """
    Define ribbed hat pattern.
    """

    circ_sts = [
        Measurement(cm, gauge, is_width=True, divisible_by=[4], rounding="up").to_stitches()
        for cm in head_circ_cm
    ]
    
    error = [
        Measurement(cm, gauge, is_width=True, divisible_by=[4]).error_percent()
        for cm in head_circ_cm
    ]
    
    measure = [
        Measurement(cm, gauge, is_width=True, divisible_by=[4]).true_measurement()
        for cm in head_circ_cm
    ]
    
    print(error)
    print(measure)
    print(head_circ_cm)

    return Pattern(
        Section("Brim",
            CastOn(circ_sts),
            WorkUntilLength(Ribbing(2,2), length_cm)
        ),
        Section("Crown",
            CrownDecrease(circ_sts)
        )
    )


# --- generate a pattern ---

# Gauge: Malabrigo worsted held double
gauge = Gauge(rows=21, stitches=13)

# Adult S
circumference = 56
length = 28

dim_names = ["circumference", "length"]
size_chart = [
    (30, 11), #premie
    (36, 15), #newborn
    (43, 18), #3-6 mo
    (46, 19), #6-12 mo
    (48, 20), #toddler
    (51, 22), #child
    (53, 25), #teen
    (56, 28), #adult S
    (59, 28), #adult M
    (62, 29), #adult L
]

# Run
pattern = ribbed_hat(
    gauge,
    head_circ_cm=[30, 36, 43, 46, 48, 51, 53, 56, 59, 62],
    length_cm=[11, 15, 18, 19, 20, 22, 25, 28, 28, 29]
)
print(pattern.render())