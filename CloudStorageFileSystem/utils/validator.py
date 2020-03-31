from jsonschema import Draft7Validator, validators, ValidationError


def check_types(validator, types, instance, schema):
    if not isinstance(instance, types):
        yield ValidationError(f"{instance} is not of type {types}")


Validator = validators.extend(Draft7Validator, {"type": check_types})
