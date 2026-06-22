"""
Stores the dataclasses that define CRM records:
    a) A pipeline Stage (`crm.stage`)
    b) A Tag (`crm.tag`)
    c) A Lead / Opportunity (`crm.lead`)

They follow the same pattern as `odoo_apps.mrp.objects`: every object builds a
`self.domain` (used for idempotent create) on `__post_init__`, keeps `domain` in
sync when `id` is assigned, and exposes `export_to_dict()`.
"""

from dataclasses import dataclass
from typing import Literal, Optional

from odoo_apps.utils.cleaning import sort_dict

LeadType = Literal['lead', 'opportunity']
# Priority: '0' Low, '1' Medium, '2' High, '3' Very High
Priority = Literal['0', '1', '2', '3']


@dataclass
class Stage:
    """
    `crm.stage` representation (a column of the sales pipeline).

    `name`: [char] Stage Name
    `sequence`: [integer] Used to order stages. Lower is first.
    `is_won`: [boolean] If checked, the opportunities reaching this stage are won.
    `team_id`: [many2one] Sales Team. If False the stage is shared by all teams.
    """
    name: str
    sequence: int = 10
    is_won: bool = False
    team_id: Optional[int | bool] = False
    fold: bool = False
    id: Optional[int] = None

    def __post_init__(self):
        self.domain = [
            ['name', '=', self.name]
        ]

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == 'id' and value is not None:
            self.domain = [
                ['id', '=', self.id]
            ]

    def export_to_dict(self, drop: Optional[tuple] = ('domain', 'id', 'studio_fields')) -> dict:
        """
        Returns the dictionary version of the class
        """
        data = self.__dict__.copy()
        if drop is not None:
            for field in drop:
                if field in data:
                    del data[field]
        return sort_dict(data)


@dataclass
class Tag:
    """
    `crm.tag` representation (a label that can be assigned to leads).

    `name`: [char] Tag Name
    `color`: [integer] Color Index
    """
    name: str
    color: int = 0
    id: Optional[int] = None

    def __post_init__(self):
        self.domain = [
            ['name', '=', self.name]
        ]

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == 'id' and value is not None:
            self.domain = [
                ['id', '=', self.id]
            ]

    def export_to_dict(self, drop: Optional[tuple] = ('domain', 'id', 'studio_fields')) -> dict:
        """
        Returns the dictionary version of the class
        """
        data = self.__dict__.copy()
        if drop is not None:
            for field in drop:
                if field in data:
                    del data[field]
        return sort_dict(data)


@dataclass
class Lead:
    """
    `crm.lead` representation (a lead or an opportunity).

    `name`: [char] Opportunity title.
    `type`: [selection] 'lead' or 'opportunity'.
    `contact_name`: [char] Contact person name.
    `partner_name`: [char] Company name of the prospect.
    `email_from`: [char] Email.
    `phone`: [char] Phone.
    `expected_revenue`: [monetary] Expected revenue.
    `probability`: [float] Probability of winning (0-100).
    `stage_id`: [many2one] Pipeline stage.
    `partner_id`: [many2one] Linked `res.partner` (customer), if any.
    `user_id`: [many2one] Salesperson.
    `team_id`: [many2one] Sales Team.
    `tag_ids`: [many2many] List of `crm.tag` ids (stored as plain ints, converted
        to the Odoo `(6, 0, ids)` command on export).
    `priority`: [selection] '0'..'3'.
    `description`: [html/text] Internal notes.
    `date_deadline`: [date] Expected closing date.
    """
    name: str
    type: LeadType = 'opportunity'
    contact_name: Optional[str | bool] = False
    partner_name: Optional[str | bool] = False
    email_from: Optional[str | bool] = False
    phone: Optional[str | bool] = False
    expected_revenue: float = 0.0
    probability: Optional[float] = None
    stage_id: Optional[int] = None
    partner_id: Optional[int] = None
    user_id: Optional[int | bool] = None
    team_id: Optional[int] = None
    tag_ids: Optional[list[int]] = None
    priority: Priority = '0'
    description: Optional[str | bool] = False
    date_deadline: Optional[str] = None
    company_id: Optional[int] = None
    id: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.phone, int) and not isinstance(self.phone, bool):
            self.phone = str(self.phone)
        self.domain = [
            ['name', '=', self.name],
            ['type', '=', self.type],
        ]
        if self.contact_name:
            self.domain.append(['contact_name', '=', self.contact_name])

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == 'id' and value is not None:
            self.domain = [
                ['id', '=', self.id]
            ]

    def export_to_dict(self, drop: Optional[tuple] = ('domain', 'id', 'studio_fields')) -> dict:
        """
        Returns the dictionary version of the class. `tag_ids` is translated to the
        Odoo many2many `(6, 0, ids)` write command, and empty values are removed.
        """
        data = self.__dict__.copy()
        if drop is not None:
            for field in drop:
                if field in data:
                    del data[field]

        if data.get('tag_ids'):
            data['tag_ids'] = [(6, 0, list(data['tag_ids']))]

        data_ref = data.copy()
        for k, v in data_ref.items():
            if v is None or str(v) == 'nan':
                del data[k]

        return sort_dict(data)
