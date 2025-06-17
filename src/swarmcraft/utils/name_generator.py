import random

ADJECTIVES = [
    "magic",
    "vibrant",
    "funky",
    "cosmic",
    "electric",
    "mystic",
    "quantum",
    "stellar",
    "lunar",
    "solar",
    "fierce",
    "gentle",
    "wild",
    "clever",
    "swift",
    "bold",
    "zen",
    "epic",
    "ninja",
    "pixel",
    "cyber",
    "retro",
    "neon",
    "turbo",
    "super",
    "ultra",
    "crystal",
    "golden",
    "silver",
    "crimson",
    "azure",
    "emerald",
    "violet",
    "amber",
    "hyper",
    "agile",
    "chaotic",
    "magik",
]

ANIMALS = [
    "bat",
    "wolf",
    "fox",
    "owl",
    "hawk",
    "eagle",
    "shark",
    "dolphin",
    "whale",
    "octopus",
    "panther",
    "tiger",
    "lion",
    "bear",
    "deer",
    "rabbit",
    "squirrel",
    "otter",
    "penguin",
    "dragon",
    "phoenix",
    "griffin",
    "unicorn",
    "kraken",
    "sphinx",
    "chimera",
    "hydra",
    "gecko",
    "salamander",
    "chameleon",
    "mantis",
    "butterfly",
    "hummingbird",
    "flamingo",
    "crow",
    "mycelium",
    "firefly",
    "pterodactyl",
    "ant",
]


def generate_participant_name() -> str:
    """Generate a fun participant name like 'vibrant bat' or 'funky wolf'"""
    adjective = random.choice(ADJECTIVES)
    animal = random.choice(ANIMALS)
    number = random.randint(1, 99)
    return f"{adjective}-{animal}-{number}"


def generate_session_code() -> str:
    """Generate a 6-character session code"""
    import string

    chars = string.ascii_uppercase + string.digits
    # Avoid confusing characters
    chars = chars.replace("0", "").replace("O", "").replace("1", "").replace("I", "")
    return "".join(random.choice(chars) for _ in range(6))
