from enum import Enum
import decimal
from decimal import Decimal


def convert_serializable_special_cases(o):
    """
    Convert an object to a type that is fairly generally serializable (e.g. json serializable).
    This only handles the cases that need converting.  The json module handles all the rest.
    For JSON, with json.dump or json.dumps with argument default=convert_serializable.
    Example:
    json.dumps(my_animal, indent=4, default=convert_serializable)
    :param o: object to be converted to a type that is serializable
    :return: a serializable representation
    """

    if isinstance(o, Enum):
        serializable_representation = o.name
    elif isinstance(o, Decimal):
        try:
            is_int = o % 1 == 0  # doesn't work for numbers greater than decimal.MAX_EMAX
        except decimal.InvalidOperation:
            is_int = False  # numbers larger than decimal.MAX_EMAX will get a decimal.DivisionImpossible, so we'll just have to represent those as a float

        if is_int:
            # if representable with an integer, use an integer
            serializable_representation = int(o)
        else:
            # not representable with an integer so use a float
            serializable_representation = float(o)
    elif isinstance(o, bytes) or isinstance(o, bytearray):
        serializable_representation = str(o)
    elif hasattr(o, "value"):
        serializable_representation = str(o.value)
    else:
        serializable_representation = str(o)
        # raise NotImplementedError(f"can not serialize {o} since type={type(o)}")
    return serializable_representation
