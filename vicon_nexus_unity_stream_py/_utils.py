class ViconNexusUnityStreamPyException(Exception):
    pass


def process_return_value(ret_val, use_json=False):
    if use_json:
        return ret_val
    else:
        raise ViconNexusUnityStreamPyException("only json encoding supported.")

