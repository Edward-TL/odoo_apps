# `odoo_apps.product` — Products, Categories, Attributes & Variants

The largest module of the library. Manages the full product catalog:
**categories** (internal, POS, eCommerce/public), **attributes and values**,
**product templates**, and **variant** resolution — including bulk operations
backed by pandas DataFrames.

## Files

| File | Purpose |
|------|---------|
| `manager.py` | `ProductManager` (~1,100 lines, uses `RPCHandlerMetaclass`). With `preload=True` it caches `{name: id}` maps of categories, attributes, and attribute values for fast lookups. |
| `objects.py` | `ProductTemplate` (name, category, price, attribute values…), `AttributeLine` (template ↔ attribute ↔ values link), `ColsReference` (column-name mapping for DataFrame imports). All with `export_to_dict()`. |
| `data_handlers.py` | DataFrame helpers: `fill_missing_unique_atts()`, `gen_attributes_values_dict()`. |

## Key `ProductManager` capabilities

- **Preload / lookup**: `get_all_categories`, `get_all_pos_categories`,
  `get_all_public_categories`, `get_all_attributes`, `get_all_attribute_values`,
  `get_ids_from`, `get_all_values`.
- **Catalog setup**: `create_category`, `create_pos_category`,
  `create_attribute`, `append_attribute_value`, `gen_attributes_values_ids`.
- **Templates & variants**: `create_product_template`,
  `append_product_template_attribute_line`, `get_att_vals_id`,
  `assign_attributes_values_to_products`, `update_product`, `archive_product`.
- **Bulk / analysis**: `look_for_missing_data`, `melt_product_df`,
  `unpivot_by_attribute`, `find_product`.

## Usage

```python
from odoo_apps.product.manager import ProductManager
from odoo_apps.product.objects import ProductTemplate

pm = ProductManager(client=client, preload=True)

template = ProductTemplate(
    name="Laptop Pro",
    categ_id=pm.categories["Electronics"],
    list_price=1299.99,
    attribute_values={"Color": ["Black", "Silver"], "Storage": ["256GB", "512GB"]},
    attribute_values_ids=pm.gen_attributes_values_ids(
        {"Color": ["Black", "Silver"], "Storage": ["256GB", "512GB"]}
    ),
)
response = pm.create_product_template(template)
```

## Notes

- Preloading does several `search_read` calls at init — reuse one
  `ProductManager` instance instead of recreating it per operation.
- The pandas-based methods expect catalog spreadsheets/CSVs; `ColsReference`
  maps your column names to the expected ones.
- Consumed by [`pos/`](../pos/README.md) and [`stock/`](../stock/README.md).
