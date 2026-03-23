from dsl.Operations import *
from sizing.Gauge import Gauge
from sizing.Measurement import Measurement

def ribbed_hat(gauge, head_circ_cm, length_cm, crown_cm):
    """
    Define ribbed hat pattern.
    """

    circ_sts = [
        Measurement(cm, gauge, is_width=True, divisible_by=[4], rounding="up").to_stitches()
        for cm in head_circ_cm
    ]
    
    crown_length_sts = [
        Measurement(cm, gauge, is_width=False).to_stitches()
        for cm in crown_cm
    ]
    
    error = [
        Measurement(cm, gauge, is_width=True, divisible_by=[4]).error_percent()
        for cm in head_circ_cm
    ]
    
    measure = [
        Measurement(cm, gauge, is_width=True, divisible_by=[4]).true_measurement()
        for cm in head_circ_cm
    ]
    
    #print(error)
    #print(measure)
    #print(head_circ_cm)

    return Pattern(
        Section("Brim",
            CastOn(circ_sts),
            WorkUntilLength(Ribbing(2,2), length_cm)
        ),
        Section("Crown",
            CrownDecrease(circ_sts, crown_length_sts)
        )
    )

# --- define sizing ---

# Adult S
circumference = 56
length = 28
crown_length = 4.75

head_circ_cm=[30, 36, 43, 46, 48, 51, 53, 56, 59, 62]
length_cm=[11, 15, 18, 19, 20, 22, 25, 28, 28, 29]
crown_cm=[crown_length for _ in range(10)]

""" dim_names = ["circumference", "length"]
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
] """

# --- generate large gauge pattern ---

# Gauge: Malabrigo worsted held double, 6.5mm needles
gauge1 = Gauge(rows=21, stitches=13)

# Run
pattern = ribbed_hat(
    gauge1,
    head_circ_cm=head_circ_cm,
    length_cm=length_cm,
    crown_cm=crown_cm
)

# Print
print("--- Large Gauge Version ---")
print(f"Gauge: {gauge1.render()}")
print(pattern.render())
print()

# --- generate small gauge pattern ---

# Gauge: Malabrigo worsted held single, 3.75mm needles
gauge2 = Gauge(rows=30, stitches=21)

# Run
pattern = ribbed_hat(
    gauge2,
    head_circ_cm=head_circ_cm,
    length_cm=length_cm,
    crown_cm=crown_cm
)

# Print
print("--- Small Gauge Version ---")
print(f"Gauge: {gauge2.render()}")
print(pattern.render())