# dsl/operations.py

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
        ctx = {
            "gauge" : {},
            "measurements" : {}
        }  # placeholder for future sizing context
        lines = []
        for section in self.sections:
            lines.extend(section.render(ctx))
        return "\n".join(lines)

# --- Value wrapper (future multi-size ready) ---

class StitchValue:
    def __init__(self, value):
        self.value = value  # can be int or list later

    def __str__(self):
        if isinstance(self.value, list):
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
        return [f"K{self.k}, P{self.p} in the round."]


class Decrease(Instruction):
    def __init__(self, method, remaining=None):
        self.method = method
        self.remaining = remaining

    def render(self, ctx):
        if self.remaining:
            return [f"{self.method} ({self.remaining} stitches)."]
        return [self.method]


class WorkUntilLength(Instruction):
    def __init__(self, instruction, length_cm):
        self.instruction = instruction
        self.length_cm = length_cm

    def render(self, ctx):
        inner = self.instruction.render(ctx)[0]
        return [f"{inner} until piece measures {self.length_cm} cm."]


class DecreaseRound(Instruction):
    def __init__(self, description, remaining=None):
        self.description = description
        self.remaining = StitchValue(remaining) if remaining else None

    def render(self, ctx):
        if self.remaining:
            return [f"{self.description} ({self.remaining} stitches)."]
        return [self.description]


class SimpleCrown(Instruction):
    def __init__(self, start_stitches):
        self.start = start_stitches

    def render(self, ctx):
        s = self.start

        # mimic your reduction ratios
        dec1 = int(s * 3/4)
        dec2 = int(dec1 * 2/3)
        dec3 = int(dec2 * 1/2)

        return [
            f"Decrease rnd 1: P2tog, K2 ({dec1} sts)",
            "Work 3 rounds even",
            f"Decrease rnd 2: P, K2tog ({dec2} sts)",
            "Work 3 rounds even",
            f"Decrease rnd 3: K2tog ({dec3} sts)",
            "Cut yarn, thread through remaining stitches, pull tight."
        ]


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