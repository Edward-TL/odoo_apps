"""
General validators
"""
from typing import Optional
from .operators import Operator

def domain_validator(
        domain: Optional[list[str, str, str]],
        attribute: Optional[str], value: Optional[str | int | list],
        operator: Operator = '=') -> list[str, str, str]:
    """
    Validates if a domain is well formed
    """
    if domain is not None:
        return domain
    if all([attribute is not None, value is not None]):
        return [attribute, operator, value]

    val_err = "Missing domain[attribute, operator, value] or attribute, operator, value."
    val_err += "Check inputs: "
    val_err += f"{domain=}, {attribute=}, {operator=}, {value=}"
    raise ValueError(val_err)