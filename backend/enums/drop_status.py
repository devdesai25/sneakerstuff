from enum import Enum

class DropStatus(str, Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    ENTRY_OPEN = "ENTRY_OPEN"
    ENTRY_CLOSED = "ENTRY_CLOSED"
    SELECTING = "SELECTING"
    CLAIMING = "CLAIMING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"

CANCELLABLE_STATES = frozenset({
    DropStatus.DRAFT,
    DropStatus.SCHEDULED,
    DropStatus.ENTRY_OPEN,
    DropStatus.ENTRY_CLOSED,
})

STOCK_RESERVED_STATES = frozenset({
    DropStatus.SCHEDULED,
    DropStatus.ENTRY_OPEN,
    DropStatus.ENTRY_CLOSED,
})

UPDATABLE_STATES = frozenset({
    DropStatus.DRAFT,
})

PUBLISHABLE_STATES = frozenset({
    DropStatus.DRAFT,
})

DELETABLE_STATES = frozenset({
    DropStatus.DRAFT,
})
