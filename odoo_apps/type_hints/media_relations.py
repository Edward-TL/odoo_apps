"""
MEDIA RELATIONS Types
"""
from typing import Literal

AvatarsDisplay = Literal[
    'hide',
    'show'
]

Privacy = Literal[
    'public',
    'private',
    'confidential'
]

ShowAs = Literal[
    'busy',
    'free'
]
