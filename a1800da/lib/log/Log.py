from lib.enums.LogLevel import LogLevel

CURRENT_LOG_LEVEL = LogLevel.INFO

def print_warning(content: str):
    if (CURRENT_LOG_LEVEL.value >= LogLevel.WARN.value):
        print("Warning: " + content)

def print_info(content: str):
    if (CURRENT_LOG_LEVEL.value >= LogLevel.INFO.value):
        print("Info: " + content)

def print_debug(content: str):
    if (CURRENT_LOG_LEVEL.value >= LogLevel.DEBUG.value):
        print("Debug: " + content)

def print_trace(content: str):
    if (CURRENT_LOG_LEVEL.value >= LogLevel.TRACE.value):
        print("Trace: " + content)

def print_ptr(name: str, ptr: int, content: int):
    print_info(f"Pointer '{name}' at '{ptr} (0x{ptr:x})' = '{content} (0x{content:x})'")