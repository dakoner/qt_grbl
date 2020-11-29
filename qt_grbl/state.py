
from enum import Enum
class State(Enum):
    STATE_INIT=0
    STATE_READY=1
    STATE_SENDING_COMMAND=5
    STATE_ERROR=-1
