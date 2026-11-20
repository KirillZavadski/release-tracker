from enum import Enum

class Status_variable(str, Enum):
    DRAFT = "Draft"
    TESTING = "Testing"
    DEPLOYED = "Deployed"
    DEPRECATED = "Deprecated"