# -*- coding:utf-8 -*-

import better_exceptions
import better_exceptions.formatter
better_exceptions.hook()
better_exceptions.formatter.SECRETS.append("myS3cr\n3tP@ss!")

def connect_to_db(password):
    connection_string = "foo bar " + password + " baz"
    raise TimeoutError("tried to connect to " + repr(connection_string))

password = "myS3cr\n3tP@ss!"
connect_to_db(password)
