from enum import IntFlag

class BlockFlags(IntFlag):
    NONE = 0
    COMPRESSED = 1
    ENCRYPTED = 2
    MEMORY_RESISTENT = 4
    DELETED = 8