"""
CALENDAR type hints
"""

from typing import Literal

Frequency = Literal[
    'daily',
    'weekly',
    'monthly',
    'yearly'
    ]

AlarmType = Literal[
    'notification',
    'email',
    'sms'
]

Interval = Literal[
    'minutes',
    'hours',
    'days'
    ]
