"""
Stock type hints
"""

from typing import Literal

DisplayTypes = Literal["radio", "pills", "select", "color", "multi"]
# === FROM ODOO ===
# 'display_type': {'help': 'The display type used in the Product Configurator.',
#                   'selection': [['radio', 'Radio'],
#                                 ['pills', 'Pills'],
#                                 ['select', 'Select'],
#                                 ['color', 'Color'],
#                                 ['multi', 'Multi-checkbox']],
#                   'string': 'Display Type',



CreateVariants = Literal["always", "dynamic", "no_variant"]

# 'create_variant': {
#       'help': '- Instantly: All possible variants are created as '
            #     'soon as the attribute and its values are added to '
            #     'a product.\n'
            # '- Dynamically: Each variant is created '
            #     'only when its corresponding attributes and values '
            #     'are added to a sales order.\n'
            # '- Never: Variants are never created for '
            #     'the attribute.\n'
            # 'Note: this cannot be changed once the '
            #     'attribute is used on a product.',
# 'selection': [['always', 'Instantly'],
#                 ['dynamic', 'Dynamically'],
#                 ['no_variant', 'Never']],
# 'string': 'Variant Creation',
# 'type': 'selection'},