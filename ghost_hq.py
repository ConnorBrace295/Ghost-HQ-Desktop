import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import random
import math
import os
import sys
import ctypes
from ctypes import wintypes

try:

    # Per-Monitor-V2 DPI awareness (best, Windows 10 1703+)
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

except Exception:

    try:

        # Fallback for older Windows versions
        ctypes.windll.user32.SetProcessDPIAware()

    except Exception:

        pass


# ============================================================
# CONFIG
# ============================================================

GHOST_WIDTH = 100
GHOST_HEIGHT = 100

FRAME_TIME = 16

SCREEN_MARGIN = 20

MIN_SPEED = 1.0
MAX_SPEED = 3.0

ARRIVAL_DISTANCE = 8


# ============================================================
# CONTROL PANEL THEME
# ============================================================

BG_COLOR = "#151225"
PANEL_BG = "#1e1a33"
BUTTON_BG = "#332c52"
BUTTON_ACTIVE_BG = "#463c6e"
ACCENT_COLOR = "#b18aff"
ACCENT_COLOR_DARK = "#241c3d"
ACCENT_COLOR_2 = "#59f2c4"
TEXT_COLOR = "#f2eefc"
MUTED_TEXT_COLOR = "#a89fc4"
DANGER_COLOR = "#ff5c72"
DANGER_ACTIVE_COLOR = "#ff7c8f"

# ============================================================
# MONITOR MODES
# ============================================================

MONITOR_1 = "Monitor 1"
MONITOR_2 = "Monitor 2"
BOTH_MONITORS = "Both Monitors"


# ============================================================
# FOLLOWER
# ============================================================

FOLLOWER_SPEED = 2.8
FOLLOWER_MOUSE_OFFSET_X = 0
FOLLOWER_MOUSE_OFFSET_Y = -65


# ============================================================
# SLEEPER
# ============================================================

SLEEP_CHANCE = 0.30

SLEEP_MIN_TIME = 3000
SLEEP_MAX_TIME = 8000

SLEEP_CHECK_MIN = 5000
SLEEP_CHECK_MAX = 15000


# ============================================================
# ZOOMER
# ============================================================

ZOOMER_NORMAL_SPEED = 1.5
ZOOMER_SPEED = 25

ZOOMER_CHANCE = 0.012

ZOOMER_MIN_TIME = 1000
ZOOMER_MAX_TIME = 3000


# ============================================================
# BUMPER
# ============================================================

BUMPER_NORMAL_SPEED = 2.0
BUMPER_CHASE_SPEED = 7.0

BUMPER_DETECTION_DISTANCE = 900

BUMPER_COLLISION_DISTANCE = 65

BUMPER_LAUNCH_DISTANCE = 250
BUMPER_LAUNCH_SPEED = 22

BUMPER_HIT_COOLDOWN = 700

BUMPER_HUNT_COOLDOWN_MIN = 2000
BUMPER_HUNT_COOLDOWN_MAX = 6000

BUMPER_MURDER_CHANCE = 0.01


# ============================================================
# MURDER
# ============================================================

MURDER_DARKEN_TIME = 1700
MURDER_BIG_SHAKE_TIME = 350
MURDER_SILENCE_TIME = 1700

MURDER_SMALL_SHAKE_AMOUNT = 2
MURDER_BIG_SHAKE_AMOUNT = 12

BUMPER_MURDER_START_SPEED = 8.0
BUMPER_MURDER_MAX_SPEED = 30.0
BUMPER_MURDER_ACCELERATION = 0.035

BUMPER_MURDER_COLLISION_DISTANCE = 60


# ============================================================
# FLEEING
# ============================================================

WANDERER_FLEE_SPEED = 7.0
FOLLOWER_FLEE_SPEED = 8.0
SLEEPER_FLEE_SPEED = 6.5
ZOOMER_FLEE_SPEED = 14.0

FLEE_BUMPER_WEIGHT = 7.0
FLEE_EDGE_WEIGHT = 8.0
FLEE_GHOST_SEPARATION_WEIGHT = 2.0
FLEE_RANDOM_WEIGHT = 1.8

EDGE_AVOID_DISTANCE = 220

FLEE_RANDOM_CHANGE_TIME = 350

FLEE_DIRECTION_SMOOTHING = 0.70



# ============================================================
# UNICORN
# ============================================================

UNICORN_SPEED = 2.2

UNICORN_TELEPORT_MIN_TIME = 4000
UNICORN_TELEPORT_MAX_TIME = 9000

UNICORN_FLASH_TIME = 220
UNICORN_FLASH_BRIGHTEN_AMOUNT = 0.55

# Subtle shimmer (replaces the old full rainbow color-cycling)
UNICORN_SHIMMER_UPDATE_TIME = 140
UNICORN_SHIMMER_STEP = 0.12
UNICORN_SHIMMER_STRENGTH = 0.14


# ============================================================
# UNIGHOST TELEPORT RAINBOW POOF
# ============================================================

TELEPORT_SMOKE_SIZE = 180
TELEPORT_SMOKE_DURATION = 1100
TELEPORT_SMOKE_FRAME_TIME = 40
TELEPORT_SMOKE_PUFF_COUNT = 11

def create_teleport_smoke_image(
    size,
    progress,
    num_puffs=TELEPORT_SMOKE_PUFF_COUNT
):

    img = Image.new(
        "RGBA",
        (size, size),
        (0, 0, 0, 0)
    )

    draw = ImageDraw.Draw(img)

    cx = size / 2
    cy = size / 2

    # --------------------------------------------------------
    # ANIMATION CURVES
    # --------------------------------------------------------

    # Fast "POOF" expansion at the beginning.
    if progress < 0.22:

        expansion_progress = (
            progress / 0.22
        )

        # Overshoot slightly to make it feel punchy.
        expansion = (
            1.15 *
            math.sin(
                expansion_progress *
                math.pi / 2
            )
        )

    else:

        expansion = 1.0

    # Fade mostly near the end rather than immediately.
    if progress < 0.55:

        alpha_multiplier = 1.0

    else:

        alpha_multiplier = max(
            0.0,
            1.0 -
            (
                (progress - 0.55) /
                0.45
            )
        )

    # --------------------------------------------------------
    # RAINBOW PALETTE
    #
    # Intentionally pastel/cartoon rather than a smooth HSV
    # gradient. This makes individual smoke blobs readable.
    # --------------------------------------------------------

    colours = [

        (255, 105, 140),   # pink
        (255, 145, 100),   # orange
        (255, 220, 105),   # yellow
        (125, 235, 155),   # green
        (100, 205, 255),   # blue
        (150, 135, 255),   # indigo
        (220, 125, 255),   # purple

    ]

    # --------------------------------------------------------
    # MAIN CLOUD PUFFS
    # --------------------------------------------------------

    for i in range(num_puffs):

        angle = (
            (math.pi * 2 / num_puffs) * i
            +
            0.35
        )

        # Different puff sizes create the irregular cartoon
        # cloud silhouette.
        size_variation = (
            0.82 +
            ((i * 37) % 100) / 250
        )

        # Initial cloud sits tightly around the ghost.
        base_distance = (
            size * 0.12
        )

        # Smoke pieces separate as animation progresses.
        outward_distance = (
            progress *
            size *
            0.22
        )

        distance = (
            base_distance * expansion +
            outward_distance
        )

        # Smoke rises as it dissipates.
        rise = (
            progress *
            size *
            0.14
        )

        # Gentle cartoon wobble.
        wobble_x = (
            math.sin(
                progress * 8 +
                i * 1.7
            )
            *
            size *
            0.018
        )

        wobble_y = (
            math.cos(
                progress * 7 +
                i * 1.3
            )
            *
            size *
            0.012
        )

        px = (
            cx +
            math.cos(angle) * distance +
            wobble_x
        )

        py = (
            cy +
            math.sin(angle) * distance -
            rise +
            wobble_y
        )

        # ----------------------------------------------------
        # PUFF SIZE
        # ----------------------------------------------------

        radius = (
            size *
            0.145 *
            size_variation *
            expansion
        )

        # Slight shrinking as individual pieces drift away.
        radius *= (
            1.0 -
            progress * 0.22
        )

        radius = max(
            1,
            radius
        )

        colour = colours[
            i % len(colours)
        ]

        alpha = int(
            235 *
            alpha_multiplier
        )

        # ----------------------------------------------------
        # DARKER OUTLINE / BACK LAYER
        #
        # Gives the smoke that 2D animated/cartoon shape
        # instead of looking like blurred circles.
        # ----------------------------------------------------

        outline_colour = (

            int(colour[0] * 0.72),
            int(colour[1] * 0.72),
            int(colour[2] * 0.72),
            int(alpha * 0.75)

        )

        outline_radius = (
            radius * 1.08
        )

        draw.ellipse(

            [
                px - outline_radius,
                py - outline_radius,
                px + outline_radius,
                py + outline_radius
            ],

            fill=outline_colour

        )

        # ----------------------------------------------------
        # MAIN COLOURED PUFF
        # ----------------------------------------------------

        draw.ellipse(

            [
                px - radius,
                py - radius,
                px + radius,
                py + radius
            ],

            fill=(
                colour[0],
                colour[1],
                colour[2],
                alpha
            )

        )

        # ----------------------------------------------------
        # WHITE / LIGHT HIGHLIGHT
        #
        # Small highlight gives each puff some volume while
        # keeping the whole thing very 2D/cartoon.
        # ----------------------------------------------------

        highlight_radius = (
            radius * 0.32
        )

        highlight_x = (
            px -
            radius * 0.30
        )

        highlight_y = (
            py -
            radius * 0.30
        )

        draw.ellipse(

            [
                highlight_x - highlight_radius,
                highlight_y - highlight_radius,
                highlight_x + highlight_radius,
                highlight_y + highlight_radius
            ],

            fill=(
                255,
                255,
                255,
                int(
                    105 *
                    alpha_multiplier
                )
            )

        )

    # --------------------------------------------------------
    # CENTRAL WHITE MAGICAL POOF
    #
    # Strongest right after teleporting, then disappears
    # quickly so the coloured smoke takes over.
    # --------------------------------------------------------

    if progress < 0.38:

        center_progress = (
            progress / 0.38
        )

        center_alpha = int(
            210 *
            (1.0 - center_progress)
        )

        center_radius = (
            size *
            0.19 *
            expansion
        )

        draw.ellipse(

            [
                cx - center_radius,
                cy - center_radius,
                cx + center_radius,
                cy + center_radius
            ],

            fill=(
                255,
                250,
                255,
                center_alpha
            )

        )

    # --------------------------------------------------------
    # SMALL DETACHED SMOKE PUFFS
    #
    # These shoot slightly farther than the main cloud and
    # make the explosion feel much more animated.
    # --------------------------------------------------------

    small_puff_count = 7

    for i in range(small_puff_count):

        angle = (
            (math.pi * 2 / small_puff_count) * i
            +
            0.7
        )

        distance = (
            size *
            (
                0.16 +
                progress * 0.34
            )
        )

        px = (
            cx +
            math.cos(angle) *
            distance
        )

        py = (
            cy +
            math.sin(angle) *
            distance -
            progress *
            size *
            0.10
        )

        radius = (
            size *
            0.045 *
            expansion *
            (1.0 - progress * 0.35)
        )

        if radius <= 0:
            continue

        colour = colours[
            (i + 2) %
            len(colours)
        ]

        alpha = int(
            200 *
            alpha_multiplier
        )

        draw.ellipse(

            [
                px - radius,
                py - radius,
                px + radius,
                py + radius
            ],

            fill=(
                colour[0],
                colour[1],
                colour[2],
                alpha
            )

        )

    # --------------------------------------------------------
    # MAGICAL SPARKLES
    # --------------------------------------------------------

    sparkle_count = 8

    for i in range(sparkle_count):

        angle = (
            (math.pi * 2 / sparkle_count) * i
            +
            progress * 1.5
        )

        distance = (
            size *
            (
                0.18 +
                progress * 0.30
            )
        )

        sx = (
            cx +
            math.cos(angle) *
            distance
        )

        sy = (
            cy +
            math.sin(angle) *
            distance -
            progress *
            size *
            0.08
        )

        sparkle_size = (
            size *
            0.025 *
            (
                0.65 +
                0.35 *
                math.sin(
                    progress * 15 +
                    i
                )
            )
        )

        sparkle_alpha = int(
            230 *
            alpha_multiplier
        )

        # Four-point sparkle.
        draw.polygon(

            [
                (
                    sx,
                    sy - sparkle_size * 1.8
                ),
                (
                    sx + sparkle_size * 0.35,
                    sy - sparkle_size * 0.35
                ),
                (
                    sx + sparkle_size * 1.8,
                    sy
                ),
                (
                    sx + sparkle_size * 0.35,
                    sy + sparkle_size * 0.35
                ),
                (
                    sx,
                    sy + sparkle_size * 1.8
                ),
                (
                    sx - sparkle_size * 0.35,
                    sy + sparkle_size * 0.35
                ),
                (
                    sx - sparkle_size * 1.8,
                    sy
                ),
                (
                    sx - sparkle_size * 0.35,
                    sy - sparkle_size * 0.35
                )
            ],

            fill=(
                255,
                255,
                255,
                sparkle_alpha
            )

        )

    return img


# ============================================================
# SPAWN BUTTON ICONS
#
# Which loaded image each personality's spawn button should
# show instead of a plain emoji.
# ============================================================

BUTTON_ICON_SOURCE = {
    "Wanderer": "Wanderer",
    "Follower": "Follower",
    "Sleeper": "Sleeper_awake",
    "Zoomer": "Zoomer",
    "Bumper": "Bumper",
    "Unicorn": "Unicorn"
}

BUTTON_ICON_SIZE = 32


# ============================================================
# PERSONALITIES
# ============================================================

PERSONALITIES = {
    "Wanderer": "🚶",
    "Follower": "🖱️",
    "Sleeper": "😴",
    "Zoomer": "💨",
    "Bumper": "💥",
    "Unicorn": "🦄"
}


# ============================================================
# IMAGE FILES
# ============================================================

IMAGE_FILES = {
    "Wanderer": "wanderer.PNG",
    "Follower": "follower.PNG",

    "Sleeper_awake": "sleeper_awake.PNG",
    "Sleeper_sleeping": "sleeper_sleeping.PNG",

    "Zoomer": "zoomer.PNG",
    "Zoomer_zooming": "zoomer_zooming.PNG",

    "Bumper": "bumper.PNG",
    "Bumper_cooldown": "bumper_cooldown.PNG",
    "Bumper_murderous": "bumper_everyone_is_fucked.PNG",

    "Unicorn": "unighost.PNG"
}


# ============================================================
# RESOURCE PATH
# ============================================================

def resource_path(filename):

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(
            sys._MEIPASS,
            filename
        )

    return os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        filename
    )


# ============================================================
# LOAD IMAGES
# ============================================================

loaded_images = {}

for image_name, filename in IMAGE_FILES.items():

    path = resource_path(filename)

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"Could not find required image:\n\n{path}"
        )

    image = Image.open(
        path
    ).convert("RGBA")

    image = image.resize(
        (
            GHOST_WIDTH,
            GHOST_HEIGHT
        ),
        Image.Resampling.LANCZOS
    )

    loaded_images[image_name] = image


# ============================================================
# DARKEN IMAGE
# ============================================================

def create_darkened_image(
    image,
    darkness
):

    darkness = max(
        0.0,
        min(
            1.0,
            darkness
        )
    )

    result = image.copy()

    pixels = result.load()

    multiplier = 1.0 - darkness

    for x in range(image.width):

        for y in range(image.height):

            r, g, b, a = pixels[x, y]

            pixels[x, y] = (
                int(r * multiplier),
                int(g * multiplier),
                int(b * multiplier),
                a
            )

    return result


# ============================================================
# SHIMMER IMAGE (subtle brightness pulse used by the Unicorn
# instead of the old full rainbow color-cycling)
# ============================================================

def create_shimmer_image(
    image,
    phase,
    strength=UNICORN_SHIMMER_STRENGTH
):

    multiplier = 1.0 + strength * math.sin(phase)

    result = image.copy()

    pixels = result.load()

    for x in range(image.width):

        for y in range(image.height):

            r, g, b, a = pixels[x, y]

            if a == 0:
                continue

            pixels[x, y] = (
                max(0, min(255, int(r * multiplier))),
                max(0, min(255, int(g * multiplier))),
                max(0, min(255, int(b * multiplier))),
                a
            )

    return result


# ============================================================
# BRIGHTENED IMAGE (used for the Unicorn's teleport sparkle
# flash)
# ============================================================

def create_brightened_image(
    image,
    amount
):

    amount = max(
        0.0,
        min(
            1.0,
            amount
        )
    )

    result = image.copy()

    pixels = result.load()

    for x in range(image.width):

        for y in range(image.height):

            r, g, b, a = pixels[x, y]

            if a == 0:
                continue

            pixels[x, y] = (
                int(r + (255 - r) * amount),
                int(g + (255 - g) * amount),
                int(b + (255 - b) * amount),
                a
            )

    return result


# ============================================================
# WINDOWS MONITOR DETECTION
# ============================================================

def get_monitors():

    monitors = []

    user32 = ctypes.windll.user32

    class MONITORINFO(ctypes.Structure):

        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("rcMonitor", wintypes.RECT),
            ("rcWork", wintypes.RECT),
            ("dwFlags", wintypes.DWORD)
        ]

    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HANDLE,
        wintypes.HDC,
        ctypes.POINTER(wintypes.RECT),
        wintypes.LPARAM
    )

    def callback(
        hMonitor,
        hdcMonitor,
        lprcMonitor,
        dwData
    ):

        info = MONITORINFO()

        info.cbSize = ctypes.sizeof(
            MONITORINFO
        )

        user32.GetMonitorInfoW(
            hMonitor,
            ctypes.byref(info)
        )

        rect = info.rcMonitor

        monitors.append(
            {
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,

                "width":
                    rect.right - rect.left,

                "height":
                    rect.bottom - rect.top,

                "primary":
                    bool(
                        info.dwFlags & 1
                    )
            }
        )

        return True

    callback_function = MONITORENUMPROC(
        callback
    )

    user32.EnumDisplayMonitors(
        None,
        None,
        callback_function,
        0
    )

    # --------------------------------------------------------
    # Put primary monitor first.
    # Then sort remaining monitors left-to-right.
    # --------------------------------------------------------

    primary = [
        monitor
        for monitor in monitors
        if monitor["primary"]
    ]

    secondary = [
        monitor
        for monitor in monitors
        if not monitor["primary"]
    ]

    secondary.sort(
        key=lambda monitor: (
            monitor["left"],
            monitor["top"]
        )
    )

    ordered = []

    if primary:
        ordered.append(
            primary[0]
        )

    ordered.extend(
        secondary
    )

    return ordered


# ============================================================
# GHOST
# ============================================================

class Ghost:

    def __init__(
        self,
        manager,
        personality,
        monitor_mode
    ):

        self.manager = manager

        self.personality = personality

        # This is locked when the ghost is spawned.
        self.monitor_mode = monitor_mode

        # ----------------------------------------------------
        # Actual monitor rectangles this ghost is allowed to use
        # ----------------------------------------------------

        self.allowed_monitors = (
            manager.get_allowed_monitors(
                monitor_mode
            )
        )

        # ----------------------------------------------------
        # Virtual bounds
        # ----------------------------------------------------

        self.virtual_bounds = (
            manager.virtual_bounds.copy()
        )

        # ----------------------------------------------------
        # Current physical monitor
        # ----------------------------------------------------

        self.current_monitor = None

        # ----------------------------------------------------
        # Personality traits
        # ----------------------------------------------------

        self.bravery = random.random()
        self.aggression = random.random()
        self.curiosity = random.random()
        self.energy = random.random()

        # ----------------------------------------------------
        # Basic state
        # ----------------------------------------------------

        self.alive = True
        self.window_destroyed = False

        self.display_state = "calm"


        # ----------------------------------------------------
        # Sleeper
        # ----------------------------------------------------

        self.sleeping = False

        # ----------------------------------------------------
        # Zoomer
        # ----------------------------------------------------

        self.zooming = False
        self.zoom_timer = 0

        # ----------------------------------------------------
        # Bumper
        # ----------------------------------------------------

        self.bumper_target = None
        self.bumper_hunt_cooldown = 0
        self.bumper_hit_cooldown = 0

        # ----------------------------------------------------
        # Murder
        # ----------------------------------------------------

        self.murderous = False
        self.murder_target = None
        self.murder_speed = (
            BUMPER_MURDER_START_SPEED
        )

        # ----------------------------------------------------
        # Unicorn
        # ----------------------------------------------------

        self.unicorn_shimmer_phase = random.uniform(0, math.pi * 2)
        self.unicorn_shimmer_timer = 0
        self.unicorn_teleport_timer = random.randint(
            UNICORN_TELEPORT_MIN_TIME,
            UNICORN_TELEPORT_MAX_TIME
        )
        self.unicorn_flashing = False
        self.unicorn_flash_timer = 0

        # ----------------------------------------------------
        # Flee
        # ----------------------------------------------------

        self.fleeing = False

        self.flee_dx = 0
        self.flee_dy = 0

        self.flee_random_dx = random.uniform(
            -1,
            1
        )

        self.flee_random_dy = random.uniform(
            -1,
            1
        )

        self.flee_timer = random.randint(
            0,
            FLEE_RANDOM_CHANGE_TIME
        )

        # ----------------------------------------------------
        # Knockback
        # ----------------------------------------------------

        self.knockback_active = False

        self.knockback_dx = 0
        self.knockback_dy = 0

        self.knockback_remaining = 0

        # ----------------------------------------------------
        # Name
        # ----------------------------------------------------

        self.name = self.generate_name()

        # ----------------------------------------------------
        # Window
        # ----------------------------------------------------

        self.window = tk.Toplevel(
            manager.root
        )

        self.window.overrideredirect(
            True
        )

        self.window.attributes(
            "-topmost",
            True
        )

        # ----------------------------------------------------
        # Transparency
        # ----------------------------------------------------

        self.transparent_colour = "#123456"

        self.window.configure(
            bg=self.transparent_colour
        )

        try:

            self.window.attributes(
                "-transparentcolor",
                self.transparent_colour
            )

        except tk.TclError:

            pass

        # ----------------------------------------------------
        # Label
        # ----------------------------------------------------

        self.label = tk.Label(
            self.window,
            bg=self.transparent_colour,
            borderwidth=0,
            highlightthickness=0
        )

        self.label.pack()

        # ----------------------------------------------------
        # Position
        # ----------------------------------------------------

        self.x, self.y = (
            self.random_position()
        )

        # ----------------------------------------------------
        # Target
        # ----------------------------------------------------

        self.target_x = self.x
        self.target_y = self.y

        # ----------------------------------------------------
        # Speed
        # ----------------------------------------------------

        self.speed = random.uniform(
            MIN_SPEED,
            MAX_SPEED
        )

        if personality == "Unicorn":

            self.speed = UNICORN_SPEED

        # ----------------------------------------------------
        # Image
        # ----------------------------------------------------

        self.current_image_name = None
        self.photo = None
        self.murder_transition_image = None

        self.set_image()

        # ----------------------------------------------------
        # Initial destination
        # ----------------------------------------------------

        if personality == "Follower":

            self.choose_mouse_destination()

        else:

            self.choose_destination()

        # ----------------------------------------------------
        # Sleeper timer
        # ----------------------------------------------------

        if personality == "Sleeper":

            self.schedule_sleep_check()

        # ----------------------------------------------------
        # Mouse controls
        # ----------------------------------------------------

        self.label.bind(
            "<Button-1>",
            self.clicked
        )

        self.label.bind(
            "<Button-3>",
            self.right_clicked
        )

        self.update_window()

    # ========================================================
    # NAME
    # ========================================================

    def generate_name(self):

        first_parts = [
            "Boo", "Spook", "Wisp", "Phantom", "Wraith",
            "Spectre", "Shade", "Ecto", "Ghoul", "Mist"
        ]

        second_parts = [
            "y", "ington", "sworth", "ie", "o",
            "ster", "kins", "elle", "us", "ina"
        ]

        return (
            random.choice(first_parts)
            +
            random.choice(second_parts)
        )

    # ========================================================
    # RANDOM POSITION ON AN ACTUAL MONITOR
    # ========================================================

    def random_position(self):

        monitor = random.choice(
            self.allowed_monitors
        )

        self.current_monitor = monitor

        min_x = (
            monitor["left"]
            +
            SCREEN_MARGIN
        )

        max_x = (
            monitor["right"]
            -
            GHOST_WIDTH
            -
            SCREEN_MARGIN
        )

        min_y = (
            monitor["top"]
            +
            SCREEN_MARGIN
        )

        max_y = (
            monitor["bottom"]
            -
            GHOST_HEIGHT
            -
            SCREEN_MARGIN
        )

        return (
            random.uniform(
                min_x,
                max_x
            ),
            random.uniform(
                min_y,
                max_y
            )
        )

    # ========================================================
    # FIND MONITOR CONTAINING GHOST
    # ========================================================

    def monitor_containing_point(
        self,
        x,
        y
    ):

        center_x = (
            x +
            GHOST_WIDTH / 2
        )

        center_y = (
            y +
            GHOST_HEIGHT / 2
        )

        for monitor in self.allowed_monitors:

            if (
                monitor["left"]
                <=
                center_x
                <
                monitor["right"]
                and
                monitor["top"]
                <=
                center_y
                <
                monitor["bottom"]
            ):

                return monitor

        return None

    # ========================================================
    # DESTINATION ON A REAL MONITOR
    # ========================================================

    def choose_destination(
        self,
        preferred_monitor=None
    ):

        # ----------------------------------------------------
        # If a preferred monitor was supplied, use it.
        # ----------------------------------------------------

        if preferred_monitor is not None:

            candidates = [
                preferred_monitor
            ]

        else:

            candidates = (
                self.allowed_monitors
            )

        monitor = random.choice(
            candidates
        )

        self.current_monitor = monitor

        self.target_x = random.uniform(
            monitor["left"]
            +
            SCREEN_MARGIN,

            monitor["right"]
            -
            GHOST_WIDTH
            -
            SCREEN_MARGIN
        )

        self.target_y = random.uniform(
            monitor["top"]
            +
            SCREEN_MARGIN,

            monitor["bottom"]
            -
            GHOST_HEIGHT
            -
            SCREEN_MARGIN
        )

    # ========================================================
    # FOLLOW MOUSE
    # ========================================================

    def choose_mouse_destination(self):

        mouse_x = (
            self.manager.root.winfo_pointerx()
        )

        mouse_y = (
            self.manager.root.winfo_pointery()
        )

        self.target_x = (
            mouse_x
            -
            GHOST_WIDTH / 2
            +
            FOLLOWER_MOUSE_OFFSET_X
        )

        self.target_y = (
            mouse_y
            -
            GHOST_HEIGHT / 2
            +
            FOLLOWER_MOUSE_OFFSET_Y
        )

        # ----------------------------------------------------
        # If following on both monitors, mouse coordinates
        # already use Windows virtual-desktop coordinates.
        # We therefore DON'T clamp to Monitor 1.
        # ----------------------------------------------------

        if self.monitor_mode == BOTH_MONITORS:

            monitor = (
                self.monitor_containing_point(
                    self.target_x,
                    self.target_y
                )
            )

            if monitor is not None:

                self.current_monitor = monitor

            return

        # ----------------------------------------------------
        # Single-monitor follower
        # ----------------------------------------------------

        monitor = self.allowed_monitors[0]

        self.target_x = max(
            monitor["left"]
            +
            SCREEN_MARGIN,

            min(
                self.target_x,

                monitor["right"]
                -
                GHOST_WIDTH
                -
                SCREEN_MARGIN
            )
        )

        self.target_y = max(
            monitor["top"]
            +
            SCREEN_MARGIN,

            min(
                self.target_y,

                monitor["bottom"]
                -
                GHOST_HEIGHT
                -
                SCREEN_MARGIN
            )
        )

    # ========================================================
    # MOVE
    # ========================================================

    def move_towards_target(self):

        dx = (
            self.target_x -
            self.x
        )

        dy = (
            self.target_y -
            self.y
        )

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        if distance <= ARRIVAL_DISTANCE:

            self.x = self.target_x
            self.y = self.target_y

            self.current_monitor = (
                self.monitor_containing_point(
                    self.x,
                    self.y
                )
                or
                self.current_monitor
            )

            return True

        if distance <= 0:

            return True

        direction_x = (
            dx / distance
        )

        direction_y = (
            dy / distance
        )

        movement = min(
            self.speed,
            distance
        )

        self.x += (
            direction_x *
            movement
        )

        self.y += (
            direction_y *
            movement
        )

        self.current_monitor = (
            self.monitor_containing_point(
                self.x,
                self.y
            )
            or
            self.current_monitor
        )

        return False

    # ========================================================
    # OTHER GHOSTS
    # ========================================================

    def other_ghosts(self):

        return [
            ghost
            for ghost in self.manager.ghosts
            if (
                ghost is not self
                and
                ghost.alive
            )
        ]

    # ========================================================
    # NEAREST GHOST
    # ========================================================

    def find_nearest_ghost(self):

        nearest = None
        nearest_distance = float("inf")

        for other in self.manager.ghosts:

            if other is self:
                continue

            if not other.alive:
                continue

            dx = (
                other.x -
                self.x
            )

            dy = (
                other.y -
                self.y
            )

            distance = math.sqrt(
                dx * dx +
                dy * dy
            )

            if distance < nearest_distance:

                nearest = other
                nearest_distance = distance

        return (
            nearest,
            nearest_distance
        )

    # ========================================================
    # SLEEP
    # ========================================================

    def schedule_sleep_check(self):

        if not self.alive:
            return

        delay = random.randint(
            SLEEP_CHECK_MIN,
            SLEEP_CHECK_MAX
        )

        self.manager.root.after(
            delay,
            self.sleep_check
        )

    def sleep_check(self):

        if not self.alive:
            return

        if (
            not self.fleeing
            and
            not self.murderous
            and
            not self.manager.murder_event_active
        ):

            if random.random() < SLEEP_CHANCE:

                self.sleep()

        self.schedule_sleep_check()

    def sleep(self):

        if not self.alive:
            return

        self.sleeping = True

        self.set_image()

        delay = random.randint(
            SLEEP_MIN_TIME,
            SLEEP_MAX_TIME
        )

        self.manager.root.after(
            delay,
            self.wake_up
        )

        self.manager.update_ghost_list()

    def wake_up(self):

        if not self.alive:
            return

        self.sleeping = False

        self.set_image()

        self.choose_destination()

        self.manager.update_ghost_list()

    # ========================================================
    # ZOOMIES
    # ========================================================

    def start_zoomies(self):

        if not self.alive:
            return

        self.zooming = True

        self.zoom_timer = random.randint(
            ZOOMER_MIN_TIME,
            ZOOMER_MAX_TIME
        )

        self.set_image()

        self.choose_destination()

        self.manager.update_ghost_list()

    # ========================================================
    # UNICORN
    # ========================================================

    def update_unicorn_shimmer(self):

        self.unicorn_shimmer_timer -= FRAME_TIME

        if self.unicorn_shimmer_timer > 0:
            return

        self.unicorn_shimmer_timer = (
            UNICORN_SHIMMER_UPDATE_TIME
        )

        self.unicorn_shimmer_phase = (
            self.unicorn_shimmer_phase +
            UNICORN_SHIMMER_STEP
        ) % (math.pi * 2)

        if self.unicorn_flashing:
            return

        shimmering = create_shimmer_image(
            loaded_images["Unicorn"],
            self.unicorn_shimmer_phase
        )

        self.set_image(
            shimmering
        )

    def update_unicorn_teleport(self):

        if self.unicorn_flashing:

            self.unicorn_flash_timer -= FRAME_TIME

            if self.unicorn_flash_timer <= 0:

                self.unicorn_flashing = False

                self.random_position_teleport()

            return

        self.unicorn_teleport_timer -= FRAME_TIME

        if self.unicorn_teleport_timer <= 0:

            self.unicorn_teleport_timer = random.randint(
                UNICORN_TELEPORT_MIN_TIME,
                UNICORN_TELEPORT_MAX_TIME
            )

            self.start_unicorn_teleport()

    def start_unicorn_teleport(self):

        if not self.alive:
            return

        self.unicorn_flashing = True

        self.unicorn_flash_timer = UNICORN_FLASH_TIME

        # Bright sparkle flash right before vanishing.
        flash_image = create_brightened_image(
            loaded_images["Unicorn"],
            UNICORN_FLASH_BRIGHTEN_AMOUNT
        )

        self.set_image(
            flash_image
        )

    def random_position_teleport(self):

        if not self.alive:
            return

        # --------------------------------------------------------
        # Remember where the Unighost was BEFORE teleporting.
        # The smoke cloud belongs here, not at the destination.
        # --------------------------------------------------------

        old_x = self.x
        old_y = self.y

        # Spawn the teleport poof at the OLD position.
        self.manager.spawn_teleport_smoke(
            old_x,
            old_y
        )

        # --------------------------------------------------------
        # Teleport
        # --------------------------------------------------------

        self.x, self.y = (
            self.random_position()
        )

        self.target_x = self.x
        self.target_y = self.y

        self.choose_destination()

        # Sparkle flash on arrival.
        flash_image = create_brightened_image(
            loaded_images["Unicorn"],
            UNICORN_FLASH_BRIGHTEN_AMOUNT
        )

        self.set_image(
            flash_image
        )

        self.update_window()
        self.manager.update_ghost_list()

    # ========================================================
    # FLEEING
    # ========================================================

    def start_fleeing(self):

        if not self.alive:
            return

        self.fleeing = True

        self.sleeping = False

        self.set_image()

        self.flee_random_dx = random.uniform(
            -1,
            1
        )

        self.flee_random_dy = random.uniform(
            -1,
            1
        )

        self.flee_timer = random.randint(
            0,
            FLEE_RANDOM_CHANGE_TIME
        )

        self.calculate_flee_direction()

    # ========================================================
    # FLEE DIRECTION
    # ========================================================

    def calculate_flee_direction(self):

        bumper = (
            self.manager.murder_bumper
        )

        if (
            bumper is None
            or
            not bumper.alive
        ):

            return

        # ----------------------------------------------------
        # Run away from bumper
        # ----------------------------------------------------

        dx = (
            self.x -
            bumper.x
        )

        dy = (
            self.y -
            bumper.y
        )

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        if distance < 1:

            angle = random.uniform(
                0,
                math.pi * 2
            )

            away_x = math.cos(angle)
            away_y = math.sin(angle)

        else:

            away_x = dx / distance
            away_y = dy / distance

        # ----------------------------------------------------
        # Edge avoidance
        #
        # IMPORTANT:
        #
        # For BOTH MONITORS, edge avoidance happens at the
        # actual outer edges of each physical monitor.
        #
        # This means the ghost can still cross the seam
        # between monitors.
        # ----------------------------------------------------

        edge_x = 0
        edge_y = 0

        monitor = (
            self.current_monitor
        )

        if monitor is None:

            monitor = (
                self.monitor_containing_point(
                    self.x,
                    self.y
                )
            )

        if monitor is not None:

            left_distance = (
                self.x -
                monitor["left"]
            )

            right_distance = (
                monitor["right"]
                -
                GHOST_WIDTH
                -
                self.x
            )

            top_distance = (
                self.y -
                monitor["top"]
            )

            bottom_distance = (
                monitor["bottom"]
                -
                GHOST_HEIGHT
                -
                self.y
            )

            if left_distance < EDGE_AVOID_DISTANCE:

                edge_x += (
                    (
                        EDGE_AVOID_DISTANCE
                        -
                        left_distance
                    )
                    /
                    EDGE_AVOID_DISTANCE
                )

            if right_distance < EDGE_AVOID_DISTANCE:

                edge_x -= (
                    (
                        EDGE_AVOID_DISTANCE
                        -
                        right_distance
                    )
                    /
                    EDGE_AVOID_DISTANCE
                )

            if top_distance < EDGE_AVOID_DISTANCE:

                edge_y += (
                    (
                        EDGE_AVOID_DISTANCE
                        -
                        top_distance
                    )
                    /
                    EDGE_AVOID_DISTANCE
                )

            if bottom_distance < EDGE_AVOID_DISTANCE:

                edge_y -= (
                    (
                        EDGE_AVOID_DISTANCE
                        -
                        bottom_distance
                    )
                    /
                    EDGE_AVOID_DISTANCE
                )

        # ----------------------------------------------------
        # Separation
        # ----------------------------------------------------

        separation_x = 0
        separation_y = 0

        for other in self.manager.ghosts:

            if other is self:
                continue

            if not other.alive:
                continue

            if other is bumper:
                continue

            dx = (
                self.x -
                other.x
            )

            dy = (
                self.y -
                other.y
            )

            distance = math.sqrt(
                dx * dx +
                dy * dy
            )

            if (
                distance > 0
                and
                distance < 130
            ):

                force = (
                    130 -
                    distance
                ) / 130

                separation_x += (
                    dx /
                    distance *
                    force
                )

                separation_y += (
                    dy /
                    distance *
                    force
                )

        # ----------------------------------------------------
        # Random panic
        # ----------------------------------------------------

        final_x = (
            away_x *
            FLEE_BUMPER_WEIGHT
            +
            edge_x *
            FLEE_EDGE_WEIGHT
            +
            separation_x *
            FLEE_GHOST_SEPARATION_WEIGHT
            +
            self.flee_random_dx *
            FLEE_RANDOM_WEIGHT
        )

        final_y = (
            away_y *
            FLEE_BUMPER_WEIGHT
            +
            edge_y *
            FLEE_EDGE_WEIGHT
            +
            separation_y *
            FLEE_GHOST_SEPARATION_WEIGHT
            +
            self.flee_random_dy *
            FLEE_RANDOM_WEIGHT
        )

        magnitude = math.sqrt(
            final_x * final_x +
            final_y * final_y
        )

        if magnitude < 0.001:

            angle = random.uniform(
                0,
                math.pi * 2
            )

            final_x = math.cos(angle)
            final_y = math.sin(angle)

            magnitude = 1

        final_x /= magnitude
        final_y /= magnitude

        self.flee_dx = (
            self.flee_dx *
            FLEE_DIRECTION_SMOOTHING
            +
            final_x *
            (
                1 -
                FLEE_DIRECTION_SMOOTHING
            )
        )

        self.flee_dy = (
            self.flee_dy *
            FLEE_DIRECTION_SMOOTHING
            +
            final_y *
            (
                1 -
                FLEE_DIRECTION_SMOOTHING
            )
        )

        magnitude = math.sqrt(
            self.flee_dx *
            self.flee_dx +
            self.flee_dy *
            self.flee_dy
        )

        if magnitude > 0:

            self.flee_dx /= magnitude
            self.flee_dy /= magnitude

    # ========================================================
    # UPDATE FLEEING
    # ========================================================

    def update_fleeing(self):

        if not self.fleeing:
            return

        self.flee_timer -= FRAME_TIME

        if self.flee_timer <= 0:

            self.flee_timer = random.randint(
                200,
                FLEE_RANDOM_CHANGE_TIME
            )

            self.flee_random_dx = random.uniform(
                -1,
                1
            )

            self.flee_random_dy = random.uniform(
                -1,
                1
            )

        self.calculate_flee_direction()

        if self.personality == "Zoomer":

            speed = ZOOMER_FLEE_SPEED

        elif self.personality == "Follower":

            speed = FOLLOWER_FLEE_SPEED

        elif self.personality == "Sleeper":

            speed = SLEEPER_FLEE_SPEED

        else:

            speed = WANDERER_FLEE_SPEED

        self.x += (
            self.flee_dx *
            speed
        )

        self.y += (
            self.flee_dy *
            speed
        )

        self.keep_on_screen()


    def launch_away_from(
        self,
        source,
        distance,
        speed
    ):

        dx = (
            self.x -
            source.x
        )

        dy = (
            self.y -
            source.y
        )

        magnitude = math.sqrt(
            dx * dx +
            dy * dy
        )

        if magnitude < 0.1:

            angle = random.uniform(
                0,
                math.pi * 2
            )

            dx = math.cos(angle)
            dy = math.sin(angle)

            magnitude = 1

        self.knockback_active = True

        self.knockback_dx = (
            dx / magnitude
        )

        self.knockback_dy = (
            dy / magnitude
        )

        self.knockback_remaining = distance


    # ========================================================
    # BUMPER TARGET
    # ========================================================

    def update_bumper_target(self):

        if not self.other_ghosts():

            self.bumper_target = None

            self.speed = (
                BUMPER_NORMAL_SPEED
            )

            return

        if self.bumper_hunt_cooldown > 0:

            self.bumper_target = None

            self.speed = (
                BUMPER_NORMAL_SPEED
            )

            return

        if (
            self.bumper_target is not None
            and
            self.bumper_target.alive
        ):

            self.target_x = (
                self.bumper_target.x
            )

            self.target_y = (
                self.bumper_target.y
            )

            self.speed = (
                BUMPER_CHASE_SPEED
            )

            return

        target, distance = (
            self.find_nearest_ghost()
        )

        if target is None:
            return

        if (
            distance <=
            BUMPER_DETECTION_DISTANCE
        ):

            self.bumper_target = target

            self.target_x = target.x
            self.target_y = target.y

            self.speed = (
                BUMPER_CHASE_SPEED
            )

        else:

            self.bumper_target = None

            self.speed = (
                BUMPER_NORMAL_SPEED
            )

            self.choose_destination()

    # ========================================================
    # BUMPER LAUNCH
    # ========================================================

    def launch_ghost(
        self,
        other
    ):

        if (
            not self.alive
            or
            not other.alive
        ):

            return

        dx = (
            other.x -
            self.x
        )

        dy = (
            other.y -
            self.y
        )

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        if distance < 0.1:

            angle = random.uniform(
                0,
                math.pi * 2
            )

            dx = math.cos(angle)
            dy = math.sin(angle)

            distance = 1

        other.knockback_active = True

        other.knockback_dx = (
            dx / distance
        )

        other.knockback_dy = (
            dy / distance
        )

        other.knockback_remaining = (
            BUMPER_LAUNCH_DISTANCE
        )

        self.bumper_target = None

        self.bumper_hunt_cooldown = random.randint(
            BUMPER_HUNT_COOLDOWN_MIN,
            BUMPER_HUNT_COOLDOWN_MAX
        )

        self.bumper_hit_cooldown = (
            BUMPER_HIT_COOLDOWN
        )

        self.speed = (
            BUMPER_NORMAL_SPEED
        )

        self.choose_destination()

        if (
            random.random()
            <
            BUMPER_MURDER_CHANCE
        ):

            self.manager.start_murder_event(
                self
            )

        self.set_image()

        self.manager.update_ghost_list()

    # ========================================================
    # KNOCKBACK
    # ========================================================

    def update_knockback(self):

        if not self.knockback_active:
            return

        movement = min(
            BUMPER_LAUNCH_SPEED,
            self.knockback_remaining
        )

        self.x += (
            self.knockback_dx *
            movement
        )

        self.y += (
            self.knockback_dy *
            movement
        )

        self.knockback_remaining -= movement

        if self.knockback_remaining <= 0:

            self.knockback_active = False

        self.keep_on_screen()

    # ========================================================
    # BUMPER COLLISION
    # ========================================================

    def check_bumper_collision(self):

        if self.bumper_hit_cooldown > 0:
            return

        for other in list(
            self.manager.ghosts
        ):

            if other is self:
                continue

            if not other.alive:
                continue

            dx = (
                other.x -
                self.x
            )

            dy = (
                other.y -
                self.y
            )

            distance = math.sqrt(
                dx * dx +
                dy * dy
            )

            if (
                distance <=
                BUMPER_COLLISION_DISTANCE
            ):

                self.launch_ghost(
                    other
                )

                return

    # ========================================================
    # MURDER
    # ========================================================

    def become_murderous(self):

        self.murderous = True

        self.murder_target = None

        self.murder_speed = (
            BUMPER_MURDER_START_SPEED
        )

        self.bumper_target = None

        self.bumper_hunt_cooldown = 0

        self.bumper_hit_cooldown = 0

        self.set_image(
            loaded_images[
                "Bumper_murderous"
            ]
        )

        for ghost in list(
            self.manager.ghosts
        ):

            if ghost is self:
                continue

            if not ghost.alive:
                continue

            ghost.start_fleeing()

        self.murder_target, _ = (
            self.find_nearest_ghost()
        )

        self.manager.update_ghost_list()

    def update_murderous(self):

        victims = self.other_ghosts()

        if not victims:

            self.finish_murder_spree()

            return

        if (
            self.murder_target is None
            or
            not self.murder_target.alive
            or
            self.murder_target not in self.manager.ghosts
        ):

            self.murder_target, _ = (
                self.find_nearest_ghost()
            )

        if self.murder_target is None:
            return

        self.murder_speed += (
            BUMPER_MURDER_ACCELERATION
        )

        self.murder_speed = min(
            self.murder_speed,
            BUMPER_MURDER_MAX_SPEED
        )

        self.speed = (
            self.murder_speed
        )

        self.target_x = (
            self.murder_target.x
        )

        self.target_y = (
            self.murder_target.y
        )

        self.move_towards_target()

        dx = (
            self.murder_target.x -
            self.x
        )

        dy = (
            self.murder_target.y -
            self.y
        )

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        if (
            distance <=
            BUMPER_MURDER_COLLISION_DISTANCE
        ):

            victim = self.murder_target

            self.manager.remove_ghost(
                victim
            )

            self.murder_target = None

            if self.other_ghosts():

                self.murder_target, _ = (
                    self.find_nearest_ghost()
                )

            else:

                self.finish_murder_spree()

    def finish_murder_spree(self):

        self.murderous = False

        self.murder_target = None

        self.fleeing = False

        self.murder_speed = (
            BUMPER_MURDER_START_SPEED
        )

        self.speed = (
            BUMPER_NORMAL_SPEED
        )

        self.bumper_target = None

        self.bumper_hunt_cooldown = random.randint(
            BUMPER_HUNT_COOLDOWN_MIN,
            BUMPER_HUNT_COOLDOWN_MAX
        )

        self.bumper_hit_cooldown = (
            BUMPER_HIT_COOLDOWN
        )

        self.choose_destination()

        self.set_image()

        self.manager.murder_bumper = None

        self.manager.update_ghost_list()

    # ========================================================
    # KEEP GHOST ON ITS ALLOWED MONITORS
    # ========================================================

    def keep_on_screen(self):

        # ----------------------------------------------------
        # Single monitor
        # ----------------------------------------------------

        if len(
            self.allowed_monitors
        ) == 1:

            monitor = (
                self.allowed_monitors[0]
            )

            self.x = max(
                monitor["left"]
                +
                SCREEN_MARGIN,

                min(
                    self.x,

                    monitor["right"]
                    -
                    GHOST_WIDTH
                    -
                    SCREEN_MARGIN
                )
            )

            self.y = max(
                monitor["top"]
                +
                SCREEN_MARGIN,

                min(
                    self.y,

                    monitor["bottom"]
                    -
                    GHOST_HEIGHT
                    -
                    SCREEN_MARGIN
                )
            )

            self.current_monitor = monitor

            return

        # ----------------------------------------------------
        # BOTH MONITORS
        #
        # We DON'T clamp to the giant virtual rectangle.
        #
        # Instead:
        #
        # - If we're on a monitor, leave us alone.
        # - If we're outside both monitors, put us onto the
        #   nearest point of the closest physical monitor.
        #
        # This prevents the ghost from getting trapped by
        # the virtual-desktop bounding rectangle.
        # ----------------------------------------------------

        monitor = (
            self.monitor_containing_point(
                self.x,
                self.y
            )
        )

        if monitor is not None:

            self.current_monitor = monitor

            return

        # ----------------------------------------------------
        # Find closest monitor
        # ----------------------------------------------------

        best_monitor = None
        best_distance = float("inf")

        center_x = (
            self.x +
            GHOST_WIDTH / 2
        )

        center_y = (
            self.y +
            GHOST_HEIGHT / 2
        )

        for monitor in self.allowed_monitors:

            closest_x = max(
                monitor["left"],
                min(
                    center_x,
                    monitor["right"]
                )
            )

            closest_y = max(
                monitor["top"],
                min(
                    center_y,
                    monitor["bottom"]
                )
            )

            dx = (
                center_x -
                closest_x
            )

            dy = (
                center_y -
                closest_y
            )

            distance = math.sqrt(
                dx * dx +
                dy * dy
            )

            if distance < best_distance:

                best_distance = distance

                best_monitor = monitor

        if best_monitor is None:
            return

        self.current_monitor = (
            best_monitor
        )

        # ----------------------------------------------------
        # Put ghost back onto physical monitor.
        # ----------------------------------------------------

        self.x = max(
            best_monitor["left"]
            +
            SCREEN_MARGIN,

            min(
                self.x,

                best_monitor["right"]
                -
                GHOST_WIDTH
                -
                SCREEN_MARGIN
            )
        )

        self.y = max(
            best_monitor["top"]
            +
            SCREEN_MARGIN,

            min(
                self.y,

                best_monitor["bottom"]
                -
                GHOST_HEIGHT
                -
                SCREEN_MARGIN
            )
        )

    # ========================================================
    # IMAGE
    # ========================================================

    def set_image(
        self,
        custom_image=None
    ):

        if not self.alive:
            return

        if custom_image is not None:

            self.photo = ImageTk.PhotoImage(
                custom_image
            )

            self.label.configure(
                image=self.photo
            )

            return

        if self.personality == "Wanderer":

            image_name = "Wanderer"

        elif self.personality == "Follower":

            image_name = "Follower"

        elif self.personality == "Sleeper":

            image_name = (
                "Sleeper_sleeping"
                if self.sleeping
                else
                "Sleeper_awake"
            )

        elif self.personality == "Zoomer":

            image_name = (
                "Zoomer_zooming"
                if self.zooming
                else
                "Zoomer"
            )

        elif self.personality == "Unicorn":

            image_name = "Unicorn"

        elif self.personality == "Bumper":

            if self.murderous:
                image_name = "Bumper_murderous"
            elif self.bumper_hunt_cooldown > 0:
                image_name = "Bumper_cooldown"
            else:
                image_name = "Bumper"

        else:

            image_name = "Wanderer"

        if image_name == self.current_image_name:
            return

        self.current_image_name = image_name

        self.photo = ImageTk.PhotoImage(
            loaded_images[image_name]
        )

        self.label.configure(
            image=self.photo
        )

    # ========================================================
    # MURDER TRANSITION IMAGE
    # ========================================================

    def update_murder_transition_image(
        self,
        progress
    ):

        base = loaded_images[
            "Bumper_cooldown"
        ]

        darkness = (
            progress ** 1.7
        )

        image = create_darkened_image(
            base,
            darkness
        )

        angle = (
            progress *
            180
        )

        rotated = image.rotate(
            angle,
            resample=Image.Resampling.BICUBIC,
            expand=False
        )

        self.murder_transition_image = (
            rotated
        )

        self.set_image(
            rotated
        )

    # ========================================================
    # WINDOW
    # ========================================================

    def update_window(self):

        if not self.alive:
            return

        if self.window_destroyed:
            return

        try:

            self.window.geometry(
                f"{GHOST_WIDTH}x{GHOST_HEIGHT}+"
                f"{int(self.x)}+{int(self.y)}"
            )

        except tk.TclError:

            self.alive = False
            self.window_destroyed = True

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self):

        if not self.alive:
            return

        if self.manager.murder_event_active:
            return

        if self.knockback_active:
            self.update_knockback()
            self.update_window()
            return

        if self.murderous:
            self.update_murderous()
            self.keep_on_screen()
            self.update_window()
            return

        if (
            self.fleeing
            and
            self.manager.murder_bumper is not None
        ):
            self.update_fleeing()
            self.update_window()
            return

        if self.sleeping:
            return

        # Bumper cooldowns
        if self.bumper_hunt_cooldown > 0:
            self.bumper_hunt_cooldown -= FRAME_TIME
            if self.bumper_hunt_cooldown < 0:
                self.bumper_hunt_cooldown = 0
            if self.personality == "Bumper":
                self.set_image()

        if self.bumper_hit_cooldown > 0:
            self.bumper_hit_cooldown -= FRAME_TIME
            if self.bumper_hit_cooldown < 0:
                self.bumper_hit_cooldown = 0

        if self.personality == "Follower":
            self.speed = FOLLOWER_SPEED
            self.choose_mouse_destination()
            self.move_towards_target()

        elif self.personality == "Zoomer":
            if not self.zooming:
                self.speed = ZOOMER_NORMAL_SPEED
                if random.random() < ZOOMER_CHANCE:
                    self.start_zoomies()
            else:
                self.speed = ZOOMER_SPEED
                self.zoom_timer -= FRAME_TIME
                if self.zoom_timer <= 0:
                    self.zooming = False
                    self.speed = ZOOMER_NORMAL_SPEED
                    self.set_image()

            arrived = self.move_towards_target()
            if arrived:
                self.choose_destination()

        elif self.personality == "Unicorn":
            self.update_unicorn_teleport()
            self.update_unicorn_shimmer()

            if not self.unicorn_flashing:
                self.speed = UNICORN_SPEED
                arrived = self.move_towards_target()
                if arrived:
                    self.choose_destination()

        elif self.personality == "Bumper":
            if not self.other_ghosts():
                self.bumper_target = None
                self.speed = BUMPER_NORMAL_SPEED
                arrived = self.move_towards_target()
                if arrived:
                    self.choose_destination()

            elif self.bumper_hunt_cooldown > 0:
                self.bumper_target = None
                self.speed = BUMPER_NORMAL_SPEED
                arrived = self.move_towards_target()
                if arrived:
                    self.choose_destination()

            else:
                self.update_bumper_target()
                self.move_towards_target()
                self.check_bumper_collision()

        else:
            arrived = self.move_towards_target()
            if arrived:
                self.choose_destination()

        self.keep_on_screen()
        self.update_window()

    # ========================================================
    # CLICK
    # ========================================================

    def clicked(
        self,
        event=None
    ):

        if not self.alive:
            return

        if self.personality == "Follower":

            self.speed = 5

        elif self.personality == "Zoomer":

            self.start_zoomies()

        elif self.personality == "Sleeper":

            if self.sleeping:

                self.wake_up()

            else:

                self.sleep()

        elif self.personality == "Unicorn":

            if not self.unicorn_flashing:

                self.unicorn_teleport_timer = 0

        else:

            self.choose_destination()

    # ========================================================
    # RIGHT CLICK
    # ========================================================

    def right_clicked(
        self,
        event=None
    ):

        if not self.alive:
            return

        self.manager.remove_ghost(
            self
        )

    # ========================================================
    # DESTROY
    # ========================================================

    def destroy(self):

        if self.window_destroyed:
            return

        self.alive = False

        self.window_destroyed = True

        try:

            self.window.destroy()

        except tk.TclError:

            pass


# ============================================================
# GHOST MANAGER
# ============================================================

class GhostManager:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title(
            "👻 Ghost HQ"
        )

        self.root.geometry(
            "465x1040"
        )

        self.root.resizable(
            False,
            False
        )

        # ====================================================
        # DETECT MONITORS
        # ====================================================

        self.monitors = get_monitors()

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        if not self.monitors:

            width = (
                self.root.winfo_screenwidth()
            )

            height = (
                self.root.winfo_screenheight()
            )

            self.monitors = [
                {
                    "left": 0,
                    "top": 0,
                    "right": width,
                    "bottom": height,
                    "width": width,
                    "height": height,
                    "primary": True
                }
            ]

        # ====================================================
        # We only need the first two monitors for the selector.
        #
        # Extra monitors are still detected but the UI's
        # Monitor 1 / Monitor 2 / Both selector refers to the
        # first two.
        # ====================================================

        self.monitor_1 = (
            self.monitors[0]
        )

        if len(self.monitors) >= 2:

            self.monitor_2 = (
                self.monitors[1]
            )

        else:

            # If only one monitor exists,
            # Monitor 2 simply mirrors Monitor 1.

            self.monitor_2 = (
                self.monitor_1.copy()
            )

        # ====================================================
        # ACTUAL VIRTUAL DESKTOP
        # ====================================================

        self.virtual_left = min(
            monitor["left"]
            for monitor in self.monitors
        )

        self.virtual_top = min(
            monitor["top"]
            for monitor in self.monitors
        )

        self.virtual_right = max(
            monitor["right"]
            for monitor in self.monitors
        )

        self.virtual_bottom = max(
            monitor["bottom"]
            for monitor in self.monitors
        )

        self.virtual_bounds = {
            "left": self.virtual_left,
            "top": self.virtual_top,
            "right": self.virtual_right,
            "bottom": self.virtual_bottom
        }

        # ====================================================
        # GHOSTS
        # ====================================================

        self.ghosts = []

        # This mirrors, row-for-row, whatever is currently in
        # self.ghost_list (the Listbox). Used so we can figure
        # out which ghost was selected before a rebuild and
        # re-select it afterwards.
        self.ghost_list_ghosts = []

        # ====================================================
        # DEFAULT
        # ====================================================

        self.selected_monitor_mode = (
            BOTH_MONITORS
        )

        # ====================================================
        # MURDER
        # ====================================================

        self.murder_event_active = False

        self.murder_bumper = None

        self.murder_event_phase = "none"

        self.murder_original_positions = {}

        # ====================================================
        # UI
        # ====================================================

        self.create_interface()

        # ====================================================
        # LOOP
        # ====================================================

        self.root.after(
            FRAME_TIME,
            self.game_loop
        )

        self.root.mainloop()

    # ========================================================
    # ALLOWED MONITORS
    # ========================================================

    def get_allowed_monitors(
        self,
        mode
    ):

        if mode == MONITOR_1:

            return [
                self.monitor_1
            ]

        if mode == MONITOR_2:

            return [
                self.monitor_2
            ]

        # ----------------------------------------------------
        # BOTH
        #
        # IMPORTANT:
        #
        # Return the actual physical rectangles.
        # Do NOT return one giant rectangle.
        # ----------------------------------------------------

        return [
            self.monitor_1,
            self.monitor_2
        ]

    # ========================================================
    # CREATE INTERFACE
    # ========================================================

    def create_interface(self):

        self.root.configure(
            bg=BG_COLOR
        )

        # ----------------------------------------------------
        # Everything below is built inside a scrollable canvas
        # rather than directly on self.root. The window is a
        # fixed size, and this control panel has grown a lot
        # over time (all the spawn buttons, monitor buttons,
        # ghost list, etc). Without scrolling, widgets near
        # the bottom (like "KILL ALL GHOSTS") can end up
        # pushed off the visible window on some screens/DPI
        # settings with no way to reach them. A scrollbar
        # guarantees every control stays reachable.
        # ----------------------------------------------------

        container = tk.Frame(
            self.root,
            bg=PANEL_BG
        )

        container.pack(
            fill="both",
            expand=True
        )

        canvas = tk.Canvas(
            container,
            highlightthickness=0,
            bg=PANEL_BG
        )

        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )

        content_frame = tk.Frame(
            canvas,
            bg=PANEL_BG
        )

        content_frame.bind(
            "<Configure>",
            lambda event:
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0, 0),
            window=content_frame,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        def on_mousewheel(event):

            content_height = content_frame.winfo_reqheight()
            canvas_height = canvas.winfo_height()

            if content_height > canvas_height + 10:

                canvas.yview_scroll(
                    int(-1 * (event.delta / 120)),
                    "units"
        )

        canvas.bind_all(
            "<MouseWheel>",
            on_mousewheel
        )

        # Everything else in this method is parented to
        # content_frame instead of self.root.
        self.content_frame = content_frame

        # ----------------------------------------------------
        # Small sprite icons used on the spawn buttons instead
        # of plain emoji.
        # ----------------------------------------------------

        self.load_button_icons()

        # ====================================================
        # TITLE
        # ====================================================

        title = tk.Label(
            self.content_frame,
            text="👻 GHOST HQ 👻",
            font=(
                "Segoe UI",
                24,
                "bold"
            ),
            bg=PANEL_BG,
            fg=ACCENT_COLOR
        )

        title.pack(
            pady=(18, 3)
        )

        subtitle = tk.Label(
            self.content_frame,
            text=(
                "Your personal desktop "
                "ghost laboratory"
            ),
            font=(
                "Segoe UI",
                10,
                "italic"
            ),
            bg=PANEL_BG,
            fg=MUTED_TEXT_COLOR
        )

        subtitle.pack(
            pady=(0, 14)
        )

        # ====================================================
        # MONITOR SECTION (moved above the spawn buttons)
        # ====================================================

        self.make_section_header(
            "🖥️  Ghost Monitor"
        )

        self.monitor_status_label = tk.Label(
            self.content_frame,
            text="Selected: Both Monitors",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=PANEL_BG,
            fg=ACCENT_COLOR_2
        )

        self.monitor_status_label.pack(
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # Monitor 1 / Monitor 2 / Both, all in a single row.
        # ----------------------------------------------------

        monitor_row = tk.Frame(
            self.content_frame,
            bg=PANEL_BG
        )

        monitor_row.pack(
            fill="x",
            padx=40,
            pady=2
        )

        self.monitor_1_button = tk.Button(
            monitor_row,
            text="🖥️  Monitor 1",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda:
            self.select_monitor(
                MONITOR_1
            )
        )

        self.monitor_1_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 3),
            ipady=7
        )

        self.monitor_2_button = tk.Button(
            monitor_row,
            text="🖥️  Monitor 2",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda:
            self.select_monitor(
                MONITOR_2
            )
        )

        self.monitor_2_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=3,
            ipady=7
        )

        self.both_monitors_button = tk.Button(
            monitor_row,
            text="🖥️🖥️  Both",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=lambda:
            self.select_monitor(
                BOTH_MONITORS
            )
        )

        self.both_monitors_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(3, 0),
            ipady=7
        )

        monitor_text = (
            f"Detected {len(self.monitors)} "
            f"monitor(s)"
        )

        monitor_info = tk.Label(
            self.content_frame,
            text=monitor_text,
            font=(
                "Segoe UI",
                9
            ),
            bg=PANEL_BG,
            fg=MUTED_TEXT_COLOR
        )

        monitor_info.pack(
            pady=(8, 4)
        )

        self.make_separator()

        # ====================================================
        # SPAWN SECTION
        # ====================================================

        self.make_section_header(
            "👻  Spawn a Ghost"
        )

        random_button = tk.Button(
            self.content_frame,
            text="🎲  Spawn Random Ghost",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            bg=ACCENT_COLOR,
            fg=ACCENT_COLOR_DARK,
            activebackground=ACCENT_COLOR_2,
            activeforeground=ACCENT_COLOR_DARK,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.spawn_random,
            height=2
        )

        random_button.pack(
            fill="x",
            padx=40,
            pady=(2, 8)
        )

        for personality in (
            "Wanderer",
            "Follower",
            "Sleeper",
            "Zoomer",
            "Bumper",
            "Unicorn"
        ):

            self.create_spawn_button(
                personality
            )

        self.make_separator()

        # ====================================================
        # POPULATION
        # ====================================================

        self.population_label = tk.Label(
            self.content_frame,
            text="Active Ghosts: 0",
            font=(
                "Segoe UI",
                13,
                "bold"
            ),
            bg=PANEL_BG,
            fg=TEXT_COLOR
        )

        self.population_label.pack(
            pady=2
        )

        # ====================================================
        # GHOST LIST
        # ====================================================

        self.ghost_list = tk.Listbox(
            self.content_frame,
            height=7,
            font=(
                "Segoe UI",
                10
            ),
            exportselection=False,
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            selectbackground=ACCENT_COLOR,
            selectforeground=ACCENT_COLOR_DARK,
            highlightthickness=0,
            relief="flat",
            bd=0
        )

        self.ghost_list.pack(
            fill="both",
            padx=40,
            pady=6
        )

        # ====================================================
        # REMOVE SELECTED
        # ====================================================

        remove_button = tk.Button(
            self.content_frame,
            text="🗑️  Remove Selected Ghost",
            font=(
                "Segoe UI",
                10
            ),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.remove_selected
        )

        remove_button.pack(
            fill="x",
            padx=40,
            pady=3
        )

        # ====================================================
        # KILL ALL
        # ====================================================

        kill_button = tk.Button(
            self.content_frame,
            text="💀  KILL ALL GHOSTS",
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            bg=DANGER_COLOR,
            fg="#1c1730",
            activebackground=DANGER_ACTIVE_COLOR,
            activeforeground="#1c1730",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.remove_all,
            height=2
        )

        kill_button.pack(
            fill="x",
            padx=40,
            pady=(6, 18)
        )

        self.update_monitor_buttons()

    # ========================================================
    # SECTION HEADER / SEPARATOR (nav board styling helpers)
    # ========================================================

    def make_section_header(
        self,
        text
    ):

        label = tk.Label(
            self.content_frame,
            text=text,
            font=(
                "Segoe UI",
                13,
                "bold"
            ),
            bg=PANEL_BG,
            fg=ACCENT_COLOR
        )

        label.pack(
            pady=(4, 2)
        )

        underline = tk.Frame(
            self.content_frame,
            bg=ACCENT_COLOR,
            height=2
        )

        underline.pack(
            fill="x",
            padx=110,
            pady=(0, 8)
        )

        return label

    def make_separator(self):

        separator = tk.Frame(
            self.content_frame,
            bg=BUTTON_BG,
            height=2
        )

        separator.pack(
            fill="x",
            padx=40,
            pady=12
        )

    # ========================================================
    # BUTTON ICONS
    # ========================================================

    def load_button_icons(self):

        self.button_icons = {}

        for personality, image_key in (
            BUTTON_ICON_SOURCE.items()
        ):

            thumbnail = loaded_images[
                image_key
            ].resize(
                (
                    BUTTON_ICON_SIZE,
                    BUTTON_ICON_SIZE
                ),
                Image.Resampling.LANCZOS
            )

            self.button_icons[personality] = (
                ImageTk.PhotoImage(
                    thumbnail
                )
            )

    # ========================================================
    # SPAWN BUTTON
    # ========================================================

    def create_spawn_button(
        self,
        personality
    ):

        icon = self.button_icons.get(
            personality
        )

        button = tk.Button(
            self.content_frame,
            text=f"  Spawn {personality}",
            image=icon,
            compound="left",
            anchor="w",
            font=(
                "Segoe UI",
                11
            ),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground=BUTTON_ACTIVE_BG,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=4,
            command=lambda:
            self.spawn(
                personality
            )
        )

        # Keep a reference so the icon isn't garbage collected.
        button.image = icon

        button.pack(
            fill="x",
            padx=40,
            pady=2
        )

    # ========================================================
    # SELECT MONITOR
    # ========================================================

    def select_monitor(
        self,
        mode
    ):

        self.selected_monitor_mode = (
            mode
        )

        self.update_monitor_buttons()

    # ========================================================
    # MONITOR BUTTON VISUALS
    # ========================================================

    def update_monitor_buttons(self):

        self.monitor_status_label.config(
            text=(
                "Selected: "
                +
                self.selected_monitor_mode
            )
        )

        for button in (
            self.monitor_1_button,
            self.monitor_2_button,
            self.both_monitors_button
        ):

            button.config(
                bg=BUTTON_BG,
                fg=TEXT_COLOR
            )

        if (
            self.selected_monitor_mode
            ==
            MONITOR_1
        ):

            self.monitor_1_button.config(
                bg=ACCENT_COLOR,
                fg=ACCENT_COLOR_DARK
            )

        elif (
            self.selected_monitor_mode
            ==
            MONITOR_2
        ):

            self.monitor_2_button.config(
                bg=ACCENT_COLOR,
                fg=ACCENT_COLOR_DARK
            )

        else:

            self.both_monitors_button.config(
                bg=ACCENT_COLOR,
                fg=ACCENT_COLOR_DARK
            )

    # ========================================================
    # SPAWN
    # ========================================================

    def spawn(
        self,
        personality
    ):

        ghost = Ghost(
            self,
            personality,
            self.selected_monitor_mode
        )

        self.ghosts.append(
            ghost
        )

        self.update_ghost_list()

    # ========================================================
    # RANDOM
    # ========================================================

    def spawn_random(self):

        personality = random.choice(
            list(
                PERSONALITIES.keys()
            )
        )

        self.spawn(
            personality
        )

    # ========================================================
    # START MURDER EVENT
    # ========================================================

    def start_murder_event(
        self,
        bumper
    ):

        if self.murder_event_active:
            return

        if not bumper.alive:
            return

        if len(self.ghosts) <= 1:
            return

        self.murder_event_active = True

        self.murder_bumper = bumper

        self.murder_event_phase = (
            "darkening"
        )

        self.murder_original_positions = {}

        for ghost in self.ghosts:

            if ghost.alive:

                self.murder_original_positions[
                    ghost
                ] = (
                    ghost.x,
                    ghost.y
                )

        self.run_murder_darkening(
            0
        )

    # ========================================================
    # MURDER DARKENING
    # ========================================================

    def run_murder_darkening(
        self,
        elapsed
    ):

        if not self.murder_event_active:
            return

        bumper = self.murder_bumper

        if (
            bumper is None
            or
            not bumper.alive
        ):

            self.cancel_murder_event()

            return

        progress = (
            elapsed /
            MURDER_DARKEN_TIME
        )

        progress = max(
            0,
            min(
                1,
                progress
            )
        )

        bumper.update_murder_transition_image(
            progress
        )

        self.apply_shake(
            MURDER_SMALL_SHAKE_AMOUNT *
            progress
        )

        if progress < 1:

            self.root.after(
                40,
                lambda:
                self.run_murder_darkening(
                    elapsed + 40
                )
            )

            return

        self.run_murder_big_shake(
            0
        )

    # ========================================================
    # MURDER BIG SHAKE
    # ========================================================

    def run_murder_big_shake(
        self,
        elapsed
    ):

        if not self.murder_event_active:
            return

        if elapsed < MURDER_BIG_SHAKE_TIME:

            self.apply_shake(
                MURDER_BIG_SHAKE_AMOUNT
            )

            self.root.after(
                25,
                lambda:
                self.run_murder_big_shake(
                    elapsed + 25
                )
            )

            return

        bumper = self.murder_bumper

        if (
            bumper is None
            or
            not bumper.alive
        ):

            self.cancel_murder_event()

            return

        bumper.set_image(
            loaded_images[
                "Bumper_murderous"
            ]
        )

        self.root.after(
            MURDER_SILENCE_TIME,
            self.finish_murder_transition
        )

    # ========================================================
    # SHAKE
    # ========================================================

    def apply_shake(
        self,
        amount
    ):

        for ghost in list(
            self.ghosts
        ):

            if not ghost.alive:
                continue

            original = (
                self.murder_original_positions.get(
                    ghost
                )
            )

            if original is None:
                continue

            ghost.x = (
                original[0]
                +
                random.uniform(
                    -amount,
                    amount
                )
            )

            ghost.y = (
                original[1]
                +
                random.uniform(
                    -amount,
                    amount
                )
            )

            ghost.update_window()

    # ========================================================
    # FINISH MURDER TRANSITION
    # ========================================================

    def finish_murder_transition(self):

        if not self.murder_event_active:
            return

        bumper = self.murder_bumper

        if (
            bumper is None
            or
            not bumper.alive
        ):

            self.cancel_murder_event()

            return

        for ghost, position in list(
            self.murder_original_positions.items()
        ):

            if not ghost.alive:
                continue

            ghost.x = position[0]
            ghost.y = position[1]

            ghost.keep_on_screen()

        self.murder_event_active = False

        self.murder_event_phase = "none"

        bumper.become_murderous()

        self.murder_original_positions.clear()

        self.update_ghost_list()

    # ========================================================
    # CANCEL MURDER
    # ========================================================

    def cancel_murder_event(self):

        self.murder_event_active = False

        self.murder_event_phase = "none"

        self.murder_bumper = None

        self.murder_original_positions.clear()

    # ========================================================
    # REMOVE GHOST
    # ========================================================

    def remove_ghost(
        self,
        ghost
    ):

        if ghost not in self.ghosts:
            return

        if ghost is self.murder_bumper:

            self.cancel_murder_event()

        self.ghosts.remove(
            ghost
        )

        ghost.destroy()

        self.update_ghost_list()

    # ========================================================
    # REMOVE SELECTED
    # ========================================================

    def remove_selected(self):

        selection = (
            self.ghost_list.curselection()
        )

        if not selection:
            return

        index = selection[0]

        if index < len(
            self.ghost_list_ghosts
        ):

            self.remove_ghost(
                self.ghost_list_ghosts[index]
            )

    # ========================================================
    # REMOVE ALL
    # ========================================================

    def remove_all(self):

        self.cancel_murder_event()

        for ghost in list(
            self.ghosts
        ):

            ghost.destroy()

        self.ghosts.clear()

        self.update_ghost_list()

    # ========================================================
    # UNICORN TELEPORT SMOKE CLOUD
    # ========================================================

    def spawn_teleport_smoke(
        self,
        ghost_x,
        ghost_y
    ):

        center_x = ghost_x + GHOST_WIDTH / 2
        center_y = ghost_y + GHOST_HEIGHT / 2

        window = tk.Toplevel(
            self.root
        )

        window.overrideredirect(
            True
        )

        window.attributes(
            "-topmost",
            True
        )

        transparent_colour = "#123456"

        window.configure(
            bg=transparent_colour
        )

        try:

            window.attributes(
                "-transparentcolor",
                transparent_colour
            )

        except tk.TclError:

            pass

        label = tk.Label(
            window,
            bg=transparent_colour,
            borderwidth=0,
            highlightthickness=0
        )

        label.pack()

        smoke_x = int(
            center_x - TELEPORT_SMOKE_SIZE / 2
        )
        smoke_y = int(
            center_y - TELEPORT_SMOKE_SIZE / 2
        )

        # Signed coordinates are important for monitors positioned
        # left of or above the primary display.
        window.geometry(
            f"{TELEPORT_SMOKE_SIZE}x{TELEPORT_SMOKE_SIZE}"
            f"{smoke_x:+d}{smoke_y:+d}"
        )

        self.animate_teleport_smoke(
            window,
            label,
            0
        )

    def animate_teleport_smoke(
        self,
        window,
        label,
        elapsed
    ):

        try:

            if not window.winfo_exists():
                return

        except tk.TclError:

            return

        progress = elapsed / TELEPORT_SMOKE_DURATION

        if progress >= 1:

            try:

                window.destroy()

            except tk.TclError:

                pass

            return

        frame = create_teleport_smoke_image(
            TELEPORT_SMOKE_SIZE,
            progress
        )

        photo = ImageTk.PhotoImage(
            frame
        )

        # Keep a reference so it isn't garbage collected.
        label.image = photo

        label.configure(
            image=photo
        )

        self.root.after(
            TELEPORT_SMOKE_FRAME_TIME,
            lambda:
            self.animate_teleport_smoke(
                window,
                label,
                elapsed + TELEPORT_SMOKE_FRAME_TIME
            )
        )

    # ========================================================
    # GHOST LIST
    # ========================================================

    def update_ghost_list(self):

        # ----------------------------------------------------
        # Remember which ghost (not just which index) is
        # currently selected, so we can re-select it after
        # the list is rebuilt below.
        # ----------------------------------------------------

        selected_ghost = None

        selection = (
            self.ghost_list.curselection()
        )

        if selection:

            previous_index = selection[0]

            if previous_index < len(
                self.ghost_list_ghosts
            ):

                selected_ghost = (
                    self.ghost_list_ghosts[
                        previous_index
                    ]
                )

        self.population_label.config(
            text=(
                f"Active Ghosts: "
                f"{len(self.ghosts)}"
            )
        )

        self.ghost_list.delete(
            0,
            tk.END
        )

        self.ghost_list_ghosts = []

        for ghost in self.ghosts:

            if not ghost.alive:
                continue

            icon = PERSONALITIES[
                ghost.personality
            ]

            status = ""

            if ghost.murderous:

                status = (
                    " — ☠️ MURDEROUS"
                )

            elif ghost.sleeping:

                status = (
                    " — sleeping"
                )

            elif ghost.zooming:

                status = (
                    " — ZOOMING"
                )

            elif (
                ghost.personality == "Unicorn"
                and
                ghost.unicorn_flashing
            ):

                status = (
                    " — ✨ teleporting"
                )

            elif (
                ghost.personality == "Bumper"
                and
                ghost.bumper_hunt_cooldown > 0
            ):

                status = (
                    " — cooling down"
                )

            elif (
                ghost.personality == "Bumper"
                and
                ghost.bumper_target is not None
            ):

                status = (
                    " — hunting"
                )


            self.ghost_list.insert(
                tk.END,
                f"{icon} "
                f"{ghost.name} "
                f"({ghost.personality})"
                f"{status}"
            )

            self.ghost_list_ghosts.append(
                ghost
            )

        # ----------------------------------------------------
        # Re-select the same ghost as before, if it's still
        # in the list.
        # ----------------------------------------------------

        if (
            selected_ghost is not None
            and
            selected_ghost in self.ghost_list_ghosts
        ):

            new_index = (
                self.ghost_list_ghosts.index(
                    selected_ghost
                )
            )

            self.ghost_list.selection_set(
                new_index
            )

            self.ghost_list.activate(
                new_index
            )

            self.ghost_list.see(
                new_index
            )

    # ========================================================
    # GAME LOOP
    # ========================================================

    def game_loop(self):

        for ghost in list(
            self.ghosts
        ):

            if not ghost.alive:
                continue

            if ghost not in self.ghosts:
                continue

            ghost.update()

        self.root.after(
            FRAME_TIME,
            self.game_loop
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    GhostManager()
