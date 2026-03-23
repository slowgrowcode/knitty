# dsl/operations.py

import math

# ---------- Base Classes ----------

class Instruction:
    def render(self, ctx):
        raise NotImplementedError()


class Section:
    def __init__(self, name, *steps):
        self.name = name
        self.steps = steps

    def render(self, ctx):
        lines = [f"\n{self.name.upper()}"]
        for step in self.steps:
            lines.extend(step.render(ctx))
        return lines


class Pattern:
    def __init__(self, *sections):
        self.sections = sections

    def render(self):
        ctx = {}  # placeholder for future sizing context
        lines = []
        for section in self.sections:
            lines.extend(section.render(ctx))
        return "\n".join(lines)

# --- Value wrappers ---

class StitchValue:
    def __init__(self, value):
        self.value = value  # int OR list[int]

    def is_multi(self):
        return isinstance(self.value, list)

    def as_list(self):
        return self.value if self.is_multi() else [self.value]

    def __str__(self):
        if self.is_multi():
            return "{" + ", ".join(str(v) for v in self.value) + "}"
        return str(self.value)


class LengthValue:
    def __init__(self, value):
        self.value = value  # int/float OR list

    def is_multi(self):
        return isinstance(self.value, list)

    def __str__(self):
        if self.is_multi():
            return "{" + ", ".join(str(v) for v in self.value) + "}"
        return str(self.value)

# ---------- Basic Instructions ----------

class CastOn(Instruction):
    def __init__(self, stitches):
        self.stitches = StitchValue(stitches)

    def render(self, ctx):
        return [f"CO {self.stitches} stitches."]


class Knit(Instruction):
    def render(self, ctx):
        return ["Knit all stitches."]


class Ribbing(Instruction):
    def __init__(self, k, p):
        self.k = k
        self.p = p

    def render(self, ctx):
        return [f"K{self.k}, P{self.p} in the round"]


class Decrease(Instruction):
    def __init__(self, method, remaining=None):
        self.method = method
        self.remaining = remaining

    def render(self, ctx):
        if self.remaining:
            return [f"{self.method} ({self.remaining} stitches)."]
        return [self.method]

# ---------- Compound Instructions ----------

class WorkUntilLength(Instruction):
    def __init__(self, instruction, length_cm):
        self.instruction = instruction
        self.length = LengthValue(length_cm)

    def render(self, ctx):
        inner_lines = self.instruction.render(ctx)

        # assume 1-line instructions for now (we’ll generalize later)
        inner = inner_lines[0]

        return [
            f"{inner} until piece measures {self.length} cm."
        ]


class DecreaseRound(Instruction):
    def __init__(self, description, remaining=None):
        self.description = description
        self.remaining = StitchValue(remaining) if remaining else None

    def render(self, ctx):
        if self.remaining:
            return [f"{self.description} ({self.remaining} stitches)."]
        return [self.description]


class CrownDecrease(Instruction):
    def __init__(self, circ_sts, crown_length_sts):
        self.circ_stitches = StitchValue(circ_sts)
        self.crown_rows = StitchValue(crown_length_sts)
    
    def _build_crown(self, crown_row_count):
        knit_rows = crown_row_count - 4
        if knit_rows > 0:
            return knit_rows
        else:
            return 0
    
    def _build_final_round(self, circ_stitches):
        if circ_stitches % 3 == 0:
            return [3] * (circ_stitches // 3)

        elif circ_stitches % 3 == 1:
            seq = [3] * (circ_stitches // 3 - 1)
            seq.insert(0, 2)
            seq.insert(math.ceil(len(seq)/2), 2)
            return seq

        elif circ_stitches % 3 == 2:
            seq = [3] * (circ_stitches // 3)
            seq.insert(len(seq)//2, 2)
            return seq

    def render(self, ctx):
        s_list = self.circ_stitches.as_list()

        dec1 = [int(s * 3/4) for s in s_list]
        dec2 = [int(s * 2/3 * 3/4) for s in s_list]
        dec3 = [int(s * 1/2 * 2/3 * 3/4) for s in s_list]
        
        knit_rows = [self._build_crown(x) for x in self.crown_rows.as_list()]
        knit1 = [math.ceil(x / 2) for x in knit_rows]
        knit2 = [math.floor(x / 2) for x in knit_rows]

        lines = [
            f"Decrease rnd 1: P2tog, K2 ({StitchValue(dec1)} stitches)",
            f"Work {StitchValue(knit1)} rounds even",
            f"Decrease rnd 2: P, K2tog ({StitchValue(dec2)} stitches)",
            f"Work {StitchValue(knit2)} rounds even",
            f"Decrease rnd 3: K2tog ({StitchValue(dec3)} stitches)",
        ]

        # --- final round per size ---
        final_lines = self._render_final_rounds(dec3)

        lines.extend(final_lines)

        lines.append(
            "Cut yarn, thread through remaining stitches, pull tight."
        )

        return lines
    
    def _render_final_rounds(self, dec3_list):
        cases_same = []
        cases_mixed = []

        sequences = [self._build_final_round(s) for s in dec3_list]

        for i, seq in enumerate(sequences):
            if len(set(seq)) == 1:
                cases_same.append((i+1, len(seq), seq[0]))
            else:
                cases_mixed.append((i+1, seq))

        lines = []

        # Case 1: uniform sequences
        if cases_same:
            sizes = [i for i, _, _ in cases_same]
            stitches = [n for _, n, _ in cases_same]
            k_val = cases_same[0][2]

            lines.append(
                f"For sizes {StitchValue(sizes)} only - "
                f"Decrease rnd 4: K{k_val}tog ({StitchValue(stitches)} stitches)"
            )

        # Case 2: custom per size
        for size_idx, seq in cases_mixed:
            seq_str = ", ".join(f"K{x}tog" for x in seq)
            lines.append(
                f"For size {size_idx} - Decrease rnd 4: {seq_str} ({len(seq)} stitches)"
            )

        return lines


# ---------- Composition ----------

class Repeat(Instruction):
    def __init__(self, instruction, times=None, until=None):
        self.instruction = instruction
        self.times = times
        self.until = until

    def render(self, ctx):
        if self.times:
            return [f"Repeat {self.times} times:"] + [
                f"  - {line}" for line in self.instruction.render(ctx)
            ]
        elif self.until:
            return [f"Repeat until {self.until}:"] + [
                f"  - {line}" for line in self.instruction.render(ctx)
            ]
        else:
            return self.instruction.render(ctx)


class Sequence(Instruction):
    """Run multiple steps in order"""
    def __init__(self, *steps):
        self.steps = steps

    def render(self, ctx):
        lines = []
        for step in self.steps:
            lines.extend(step.render(ctx))
        return lines

# ---------- Simple Helpers ----------

class Length:
    def __init__(self, cm):
        self.cm = cm

    def __str__(self):
        return f"{self.cm} cm"