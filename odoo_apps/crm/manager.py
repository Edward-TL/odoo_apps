"""
CRM manager. Mirrors `odoo_apps.mrp.manager.Factory`: thin wrappers around
`client.create` that keep creation idempotent through each object's `domain`.
"""

from dataclasses import dataclass
from typing import Optional

from odoo_apps.client import OdooClient, RPCHandlerMetaclass
from odoo_apps.response import Response
from odoo_apps.models import CRM

from odoo_apps.crm.objects import Stage, Tag, Lead
from odoo_apps.utils.cleaning import transform_dict_array_to_dict


@dataclass
class CrmManager(metaclass=RPCHandlerMetaclass):
    """
    Manages CRM records (`crm.stage`, `crm.tag`, `crm.lead`) on the client's Odoo DB.

    With `preload=True` it caches `{name: id}` maps of the existing stages and tags
    so the loader can resolve them by name, the same way `ProductManager` caches
    categories.

    Args:
        - client: OdooClient.
    """
    client: OdooClient
    preload: bool = True
    stages: Optional[dict] = None
    tags: Optional[dict] = None

    def __post_init__(self):
        if self.preload:
            if self.stages is None:
                self.get_all_stages()
            if self.tags is None:
                self.get_all_tags()

    def get_all_stages(self) -> dict:
        """Caches `{stage_name: id}` from the client's DB."""
        self.stages = transform_dict_array_to_dict(
            self.client.search_read(
                CRM.STAGE,
                domain=[['id', '>', 0]],
                fields=['id', 'name']
            ),
            key_ref='name',
        )
        return self.stages

    def get_all_tags(self) -> dict:
        """Caches `{tag_name: id}` from the client's DB."""
        self.tags = transform_dict_array_to_dict(
            self.client.search_read(
                CRM.TAG,
                domain=[['id', '>', 0]],
                fields=['id', 'name']
            ),
            key_ref='name',
        )
        return self.tags

    def create_stage(self, stage: Stage, printer=False) -> Response:
        """Creates a pipeline stage and updates the local `stages` cache."""
        response = self.client.create(
            CRM.STAGE,
            vals=stage.export_to_dict(),
            domains=stage.domain,
            printer=printer
        )
        stage.id = response.object
        if self.stages is not None and response.status_code in [200, 201]:
            self.stages[stage.name] = response.object
        return response

    def create_tag(self, tag: Tag, printer=False) -> Response:
        """Creates a tag and updates the local `tags` cache."""
        response = self.client.create(
            CRM.TAG,
            vals=tag.export_to_dict(),
            domains=tag.domain,
            printer=printer
        )
        tag.id = response.object
        if self.tags is not None and response.status_code in [200, 201]:
            self.tags[tag.name] = response.object
        return response

    def create_lead(self, lead: Lead, printer=False) -> Response:
        """Creates a lead / opportunity."""
        response = self.client.create(
            CRM.LEAD,
            vals=lead.export_to_dict(),
            domains=lead.domain,
            printer=printer
        )
        lead.id = response.object
        return response
