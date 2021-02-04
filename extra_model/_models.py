from typing import Any, Optional, Tuple, Union


class ModelBase:
    def load_from_files(self):
        pass


class ExtraModelBase:
    pass


# NOTE: improve typehints!
def extra_factory(bases: Optional[Union[Any, Tuple[Any]]] = ModelBase) -> Any:
    """Factory for ExtraModel class types. Will dynamically create
    the class when called with the provided base classes

    :param bases: Base classes to be used when creating ExtraModel class
    :type bases: Class type or tuple of class types

    :return: ExtraModel class
    """

    if not isinstance(bases, tuple):
        bases = (bases,)
    bases = bases + (ExtraModelBase,)

    return type("ExtraModel", bases, {})
