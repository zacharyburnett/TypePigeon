from enum import EnumMeta
from typing import Collection, Mapping, Any


def subscripted_type(generic_alias: Any) -> type:
    """
    convert an instance of a subscripted ``typing._GenericAlias`` to a subscripted type

    :param generic_alias: generic alias
    :return: simple type

    >>> from typing import List
    >>> subscripted_type(List[str])
    [str]

    >>> from typing import Dict
    >>> subscripted_type(Dict[str, float])
    {str: float}

    >>> from typing import Dict, Tuple
    >>> subscripted_type({str: (Dict[int, str], str)})
    {str: ({int: str}, str)}

    """

    if generic_alias.__origin__.__name__ == 'Union':
        raise NotImplementedError('Union subscription is not supported')

    if (
            hasattr(generic_alias, "__origin__")
            or isinstance(generic_alias, Collection)
            and not isinstance(generic_alias, (EnumMeta, str))
    ):
        if hasattr(generic_alias, "__origin__"):
            type_class = generic_alias.__origin__
            if hasattr(generic_alias, "__args__"):
                members = generic_alias.__args__
                if issubclass(type_class, Mapping):
                    members = [members]
            else:
                members = ()
        elif isinstance(generic_alias, Collection) and not isinstance(
                generic_alias, (EnumMeta, str)
        ):
            type_class = generic_alias.__class__
            if issubclass(type_class, Mapping):
                members = generic_alias.items()
            else:
                members = generic_alias

        members = [subscripted_type(member) for member in members]
        if type_class != generic_alias.__class__ or members != generic_alias:
            return type_class(members)
        else:
            return generic_alias
    else:
        return generic_alias
