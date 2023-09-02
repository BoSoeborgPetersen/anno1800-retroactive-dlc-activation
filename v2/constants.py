
from enum import Enum

class DLC(Enum):
    THE_ANARCHIST = 2861514240  # 0xaa8f3e00
    S1_SUNKEN_TREASURES = 3091269120  # 0xb8410600
    S1_BOTANICA = 3108046336  # 0xb9410600
    S1_THE_PASSAGE = 3124823552  # 0xba410600
    S2_SEAT_OF_POWER = 3410036224  # 0xcb410600
    S2_BRIGHT_HARVEST = 3594585600  # 0xd6410600
    S2_LAND_OF_LIONS = 3611362816  # 0xd7410600
    S3_DOCKLANDS = 3812689408  # 0xe3410600
    S3_TOURIST_SEASON = 3829466624  # 0xe4410600
    S3_HIGH_LIFE = 3846243840  # 0xe5410600
    S4_SEEDS_OF_CHANGE = 2170617856  # 0x81610000
    S4_EMPIRE_OF_THE_SKIES = 2187395072  # 0x82610000
    S4_NEW_WORLD_RISING = 2204172288  # 0x83610000


# Path to the savefile, relative to this script file
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v2/Autosave.a7s"
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v2/Autosave 2915.a7s"
SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v2/Clean.a7s"
SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v2/Clean.a7s"
GAME_SETUP_FILE_NAME = 'gamesetup.a7s'
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v2/Clean1.a7s"
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v2/Werner Schnitzel2.a7s"
# SAVE_GAME_PATH = "c:/git/anno1800-retroactive-dlc-activation/v2/Clean1_dlc_activated.a7s"

# Insert the DLCs to add to the save game
DLCS_TO_ADD = [DLC.S1_SUNKEN_TREASURES]