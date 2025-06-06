"""
TODO:
* Crear las tablas para valores unicos de atributos y categorias
* Diseñar las funciones para la concatenacion de las columnas correspondientes
"""

from inspect import getmembers
from typing import Literal
from .operators import Operator


def generate_dict(data_obj) -> dict:
    """
    Generate a dictionary of modules from the class attributes.
    :param data_obj: Data Class to generate the dictionary from.
    :return: Dictionary of modules.
    """
    return {
        module[0]:module[1] for module in getmembers(
            data_obj
            ) if not module[0].startswith('__')
            }


def gen_domains_from_str(domain_check, domain_comp, vals):
    """
    Generate Odoo domain tuples from input values.
    Args:
        domain_check (str): The key to check in the input values.
        domain_comp (str): The comparison operator to use in the domain tuple (e.g., '=', '!=', 'in').
        vals (list or dict): The input values, either a list of dictionaries or a single dictionary.
    Returns:
        list: A list of domain tuples in the form (domain_check, domain_comp, value).
    Examples:
        >>> gen_domains_from_str('name', '=', [{'name': 'John'}, {'name': 'Jane'}])
        [('name', '=', 'John'), ('name', '=', 'Jane')]
        >>> gen_domains_from_str('age', '>', {'age': 30})
        [('age', '>', 30)]
    """
    domains = []
    if isinstance(vals, list):
        # print(f"Vals: {vals} are List")
        if isinstance(domain_check, str):
            for value in vals:
                for k, v in value.items():
                    if k == domain_check:
                        domains.append((domain_check, domain_comp, v))
                        break
    if isinstance(vals, dict):
        # print(f"Vals: {vals} are Dictionary")
        domains.append((domain_check, domain_comp, vals[domain_check]))

    return domains

def gen_domains_from_list(domain_fields, domain_operators, vals, printer=False):
    """
    Generates a list of Odoo domain tuples from provided domain field names, comparison operators, and values.
    Args:
        domain_check (list): List of field names to check in the domain.
        domain_comp (list): List of comparison operators corresponding to each field name.
        vals (list or dict): List of dictionaries or a single dictionary containing field-value pairs.
    Returns:
        list: A list of tuples, each representing a domain in the form (field, operator, value).
    Example:
        generate_domains_from_list(['name', 'age'], ['=', '>'], [{'name': 'John'}, {'age': 30}])
        # Returns: [('name', '=', 'John'), ('age', '>', 30)]
    """
    domains = []
    if isinstance(domain_fields, list):
        if printer:
            print('Domain Check is List')
        if isinstance(vals, list):
            for domain, comp in zip(domain_fields, domain_operators):
                for value in vals:
                    for k, v in value.items():
                        if k == domain:
                            domains.append((domain, comp, v))

        if isinstance(vals, dict):
            if printer:
                print('Just one dictionary values')
                print(domain_fields, domain_operators)
                print(vals)
            for domain, comp in zip(domain_fields, domain_operators):
                for k, v in vals.items():
                    if k == domain:
                        domains.append((domain, comp, v))

    return domains

def check_domains(
    domain_fields: str | list, domain_operators: Operator, vals: dict | list[dict]
    ) -> list[tuple]:
    """
    Generate the domains based on the data passed
    """

    if isinstance(domain_fields, str):
        return gen_domains_from_str(domain_fields, domain_operators, vals)

    if isinstance(domain_fields, list):
        return gen_domains_from_list(domain_fields, domain_operators, vals)

    return ([],[],[])

def replace_values(old_val, new_val, array: list) -> None:
    if old_val in array:
        name_idx = array.index(old_val)
        array[name_idx] = new_val