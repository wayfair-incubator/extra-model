from typing import Any, Optional, Tuple, Union


class ModelBase:
    """ Base class that provides file loading functionality
    """
    
    def load_from_files(self):
        pass


class ExtraModelBase:
    """ Extra model class that provides an interface for 
    training and predicting
    """

    def __init__(self):
        pass
    
    def storage_metadata(self):
        pass
    
    def load_from_files(self):
        pass
    
    def train(self):
        pass
    
    def predict(self):
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
