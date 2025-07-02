class AdminNotFound(Exception):
    """raise when admin not found"""
    pass

class WrongPassword(Exception):
    """raise when password is wrong"""
    pass


class AdminAlredyExists(Exception):
    """raise when admin alredy exists"""
    pass


class NoActiveAdmin(Exception):
    """raise when not active admin"""
    pass
