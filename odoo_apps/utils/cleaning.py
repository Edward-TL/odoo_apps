"""
TODO:
* Crear las tablas para valores unicos de atributos y categorias
* Diseñar las funciones para la concatenacion de las columnas correspondientes
"""
from copy import copy
from inspect import getmembers

from typing import Literal, Optional
import weakref

# import numpy as np
import pandas as pd

from .operators import Operator

def flat_list(nested_list: list) -> list:
    """Flats a double list matrix"""
    flat_list = [item for sublist in nested_list for item in sublist]
    return flat_list

def generate_dict(data_obj) -> dict:
    """
    Generate a dictionary of modules from the class attributes.
    :param data_obj: Data Class to generate the dictionary from.
    :return: Dictionary of modules.
    """
    return {
        module[0]:module[1] for module in getmembers(
            weakref.ref(data_obj)
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

# def replace_values(old_val, new_val, array: list) -> None:
#     if old_val in array:
#         name_idx = array.index(old_val)
#         array[name_idx] = new_val

def transform_dict_array_to_dict(
        dict_array: list[dict],
        key_ref: Literal['name', 'display_name'] = 'name',
        key_val: str = 'id') -> dict:
    """
    From a list of dictionaries, transform it to a single dictionary.

    Args:
        dict_array: list[dict] F.E. [{'id':1, 'name':'foo'}, {'id':2, 'name':'bar'}]
        key_ref: str. FE: 'name'
        key_val: str. FE: 'id'

    Returns:
        dict. FE: {'foo':1, 'bar':2}
    """
    
    return {
        value[key_ref]: value[key_val] for value in dict_array
        }

def merge_dictionaries(
        parent:dict, child: list[dict],
        parent_ref: str = 'attribute_id',
        p_idx: Optional[int] = 1,
        child_key: str = 'name',
        child_val: str = 'id') -> dict:
    """
    Generates a tree dict with the followed structure:
    {
    'parent': {
        'child_key': child_val
    }

    Args:
        - parent [dict]: a Dictionary with root values. FE: Attributes.
        {'foo': 1, 'bar':2}
        - child [list[dict]]: A list of dictionaries, that stores
        data related to the parents. FE: values of the attributes.
        [
            {'id': 1, 'name': 'val_1', 'attribute_id': [1, 'foo']},
            {'id': 2, 'name': 'val_2', 'attribute_id': [2, 'bar']}
        ]
        - parent_ref [str]: Reference in child to get the reference of the parent.
        
        - p_idx Optional[int]: If parent_ref is stored in a list (as the example), will
        use the idx call. If not, it's omitted when generated.
        - child_key [str]: Is the key that calls the child's key that will vall the value
        stored in child's dict. In this example: 'name'.
        - child_val [str]: Is the key that calls the value stored in child's dict.
            In this example: 'id'.
        
    Returns:
        dict

    In this example:
    {
        'foo': {
            'val_1': 1
        },
        'bar': {
            'val_2: 2
        }
    }
    
    """

    # ORIGINAL:
    # self.att_values = {att: {} for att in self.attributes.keys()}
    
    # for val_data in vals:
    #     self.att_values[
    #         val_data['attribute_id'][1]
    #         ][val_data['name']] = val_data['id']
    tree_dict = {att: {} for att in parent.keys()}

    if p_idx is not None:
        for val_data in child:
            tree_dict[
                # Parent reference. 
                val_data[parent_ref][p_idx]
                ][
                    # Consider when created, tree_dict stored an empty set
                    # or dictionary ('{}'). So this turns into the new key
                    val_data[child_key]
                        # The new value
                    ] = val_data[child_val]

        return tree_dict

    for val_data in child:
        tree_dict[
            # Parent reference. 
            val_data[parent_ref]
            ][
                # Consider when created, tree_dict stored an empty set
                # or dictionary ('{}'). So this turns into the new key
                val_data[child_key]
                    # The new value
                ] = val_data[child_val]

        return tree_dict

def gen_matrix(raw_data: list[dict]) -> dict[str, list]:
    """
    From a list of dictionaries, creates a dictionary that stores all values in list.
    """
    
    matrix = {
        key: [None]*len(raw_data) for key in raw_data[0].keys()
    }

    for n, data in enumerate(raw_data):
        for k,v in data.items():
            matrix[k][n] = v

    return matrix

def split_id_pair(matrix: dict[str, list]) -> dict[str, list]:
    """
    Transforms keys ending with `_id` that stores [id: int, name: str] into two
    separated keys
    """
    clean_matrix = copy(matrix)

    for k, vals in matrix.items():
        key = copy(k)
        if key.endswith('_id'):
            # there are values that are optional (like categories). And if the user
            # doesn't give a value, will appear as False, instead of a list like [False, False],
            # creating an error if this is not considerated
            clean_matrix[key] = [v[0] if isinstance(v, list) else False for v in vals]
            clean_matrix[key.replace('_id','_name')] = [v[1] if isinstance(v, list) else False for v in vals]

    return clean_matrix

def extract_cell_value(df: pd.DataFrame, col_ref: str, val_ref:str | int | float | list | dict, val_col: str):
    """
    return df[df[col_ref] == val_ref][val_col].values[0]
    """
    return df[df[col_ref] == val_ref][val_col].values[0]
