Commands = [
    ["Wake Up", [72, 77, 79, 84, 72, 77, 79, 84]],
    ["Call", [72, 74, 76, 77, 79]],
    ["Play", [72, 79, 72, 79, 72, 84, 72]]
]

question = [
    [[0x90, 64, 127], 0],
    [[0x80, 64, 127], 120],

    [[0x90, 68, 127], 120],
    [[0x80, 68, 127], 240],

    [[0x90, 71, 127], 240],
    [[0x80, 71, 127], 360],

    [[0x90, 74, 127], 360],
    [[0x80, 74, 127], 960],

    [[0x90, 75, 127], 960],
    [[0x80, 75, 127], 1000],

    [[0x90, 76, 127], 1000],
    [[0x80, 76, 127], 1200],
]

angry = [
    [[0x90, 73, 127], 0],
    [[0x90, 76, 127], 0],
    [[0x90, 79, 127], 0],
    [[0x90, 82, 127], 0],
    [[0x80, 73, 127], 1000],
    [[0x80, 76, 127], 1000],
    [[0x80, 79, 127], 1000],
    [[0x80, 82, 127], 1000],
]

snore = [
    [[0x90, 45,127], 0],
    [[0x80, 45,127], 1500],

    [[0x90, 56,127], 0],
    [[0x80, 56,127], 1500],
]

wakeup = [
    [[0x90, 73,127], 0],
    [[0x80, 73,127], 120],

    [[0x90, 89,127], 0],
    [[0x80, 89,127], 120],

    [[0x90, 73,127], 0],
    [[0x80, 73,127], 120],

    [[0x90, 89,127], 0],
    [[0x80, 89,127], 120],
]
