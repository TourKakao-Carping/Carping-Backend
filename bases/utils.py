def check_data_key(key):
    if key == None:
        return False
    else:
        return True


def check_str_digit(numstr):
    if type(numstr) == str:
        if numstr.isdigit():
            return True
        else:
            return False
    elif type(numstr) == int:
        return True
    else:
        return False
