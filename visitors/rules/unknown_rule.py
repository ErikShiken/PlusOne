from unknown_exception import UnknownException

def unknown_rule(set_of_unknowns):
    num_unknowns = len(set_of_unknowns)
    if num_unknowns > 1:
        raise UnknownException(num_unknowns, set_of_unknowns)