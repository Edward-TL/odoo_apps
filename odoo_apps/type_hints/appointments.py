"""
Odoo hint values for appointments operators
"""

from typing import Literal

ActivityExceptionDecorator = Literal[
    'warning',
    'danger'
]

ActivityState = Literal[
    'overdue',
    'today',
    'planned'
]

AppointmentCategory = Literal[
    'recurring', # Regular
    'punctual', # Punctual
    'custom', # Specific Slots
    'anytime' # Shared Calendar'
]

AssignMethod = Literal[
    'resource_time', #'Pick User/Resource then Time
    'time_resource', #'Select Time then User/Resource
    'time_auto_assign' #'Select Time then auto-assign
]
# apps/objects/appointment.py
# Definiciones de tipos literales si son necesarios para campos específicos
# (Aunque para appointment.appointment, muchos campos son IDs o strings/datetimes)


EventVideocallSource = Literal[
    'discuss', #Discuss is Odoo Discuss
    'google_meet'
    ]

CategoryTimeDisplay = Literal[
    'recurring_fields', # Available now
    'punctual_fields', # Withina a date range
]

RecurreceRuleType = Literal[
    'daily',
    'weekly',
    'monthly',
    'yearly'
]
