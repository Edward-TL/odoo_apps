This is extracted from website:

A domain can be a simple condition (field_expr, operator, value) where:

field_expr (str)
a field name of the current model, or a relationship traversal through a Many2one using dot-notation e.g. 'street' or 'partner_id.country'. If the field is a date(time) field, you can also specify a part of the date using 'field_name.granularity'. The supported granularities are 'year_number', 'quarter_number', 'month_number', 'iso_week_number', 'day_of_week', 'day_of_month', 'day_of_year', 'hour_number', 'minute_number', 'second_number'. They all use an integer as value.

operator (str)
an operator used to compare the field_expr with the value. Valid operators are:

=
equals to

!=
not equals to

>
greater than

>=
greater than or equal to

<
less than

<=
less than or equal to

=?
unset or equals to (returns true if value is either None or False, otherwise behaves like =)

=like
matches field_expr against the value pattern. An underscore _ in the pattern stands for (matches) any single character; a percent sign % matches any string of zero or more characters.

like
matches field_expr against the %value% pattern. Similar to =like but wraps value with ‘%’ before matching

not like
doesn’t match against the %value% pattern

ilike
case insensitive like

not ilike
case insensitive not like

=ilike
case insensitive =like

in
is equal to any of the items from value, value should be a collection of items

not in
is unequal to all of the items from value

child_of
is a child (descendant) of a value record (value can be either one item or a list of items).

Takes the semantics of the model into account (i.e following the relationship field named by _parent_name).

parent_of
is a parent (ascendant) of a value record (value can be either one item or a list of items).

Takes the semantics of the model into account (i.e following the relationship field named by _parent_name).

any
matches if any record in the relationship traversal through field_expr (Many2one, One2many, or Many2many) satisfies the provided domain value. The field_expr should be a field name.

not any
matches if no record in the relationship traversal through field_expr (Many2one, One2many, or Many2many) satisfies the provided domain value.