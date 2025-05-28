"""
Oeprators object and guide for domain
"""
from typing import Literal
Operator = Literal[
    "=", "!=", "<", "<=", ">", ">=",

    # Unset or equals to. Returns `True` if `value` is either `None`
    # or `False`, otherwise behaves like `=`
    "=?", 

    # Matches `field_expr` against the `value` pattern. An underscore `_`
    # in the patter stands for (marches) any single character.
    # a percent sign `%` matches any string of zero or more characters.
    "=like",

    # Matches `field_expr` against the `%value%` pattern. Similiar to `=like`
    # but wraps `value` with percent signs `%` before matching.
    "like",

    # Doesn't match agains the `%value` pattern
    "not like",

    # Case insensitive `like`
    "ilike",

    # Case insensitive `not like`
    "not ilike",

    # Case insensitive `=like`
    "=ilike",

    # Is equal to any of the items from `value`m `value` should be a collection of items
    "in",

    # Is unequal to all of the items from value
    "not in",

    # Is a child (descendant) of a `value` record (value can be either one item or a list of items).
    # Takes the semantics of the model into account.
    # IE: Following the relationship field named by `_parent_name`).
    "child_of",

    # Is a parent (ascendant) of a `value` record
    # (value can be either one item or a list of items).
    # Takes the semantics of the model into account.
    # IE: Following the relationship field named by `_parent_name`).
    "parent_of",

    # Matches if any record in the relationship traversal through `field_expr`
    # (`Many2One`, `One2many`, or `Many2many`) satisfies the provided domain
    # `value`. The `field_expr` should be a field name.
    "any",

    # Matches if no record in the relationship traversal through `field_expr`
    # (`Many2One`, `One2many`, or `Many2many`) satisfies the provided value
    "not any"
]
