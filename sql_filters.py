import string


def filtr(username, password, ):
    if len(str(username.replace(" ", ''))) > 16 or len(str(password).replace(" ", '')) > 20:
        return None
    else:
        username_ = "".join(str(chars).replace(" ", '') for chars in username if chars not in string.punctuation)
        password_ = "".join(str(chars).replace(" ", '') for chars in password if chars not in ["%", "-", "'",
                                                                                               '"', '`', '(',
                                                                                               ')', '[', ']'])

        return username_, password_,


def copyPasswordFiltr(copypassword):
    if len(str(copypassword).replace(" ", '')) > 20:
        return None
    else:
        copypassword_ = "".join(str(chars).replace(" ", '') for chars in copypassword if chars not in ["%", "-", "'",
                                                                                                       '"', '`', '(',
                                                                                                       ')', '[', ']'])
        return copypassword_
