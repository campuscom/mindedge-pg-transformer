
def to_float(float_value):
    try:
        val = 0.0 if not float_value else float(float_value)
    except Exception as e:
        # logger.error(str(e))
        val = 0.0
    return val


def to_integer(int_value):

    try:
        val = 0 if not int_value else int(int_value)
    except Exception as e:
        # logger.error(str(e))
        val = 0
    return val
