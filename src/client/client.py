#!/usr/bin/python2.7

import sys, ssl
from socket import socket
from ssl import SSLContext


class UsageError(Exception):
    def __init__(self):
        super(UsageError, self).__init__('client.py [-x] <server_host> <server_port> <method> <path>')


def secure(message, username, password):
    if username is not None:
        return message + 'Username: {0}\nPassword: {1}\n'.format(username, password)
    else:
        return message


def get(connection, host, path, language='en-us', encoding='None', username=None, password=None):
    connection.send(secure(
        'GET {0} HTTP/1.1\n'
        'User-Agent: Customer1.0\n'
        'Host: {1}\n'
        'Accept-Language: {2}\n'
        'Accept-Encoding: {3}\n'
        'Connection: Keep-Alive\n'
        .format(path, host, language, encoding), username, password
    ))
    return connection.recv(1024)

request = {
    'GET': get,
    'get': get,
}

if __name__ == '__main__':
    def get_ssl_context(protocol, verify_mode, check_hostname):
        context = ssl.SSLContext(protocol)
        context.verify_mode = verify_mode
        context.check_hostname = check_hostname
        context.load_default_certs()
        return context

    if len(sys.argv) == 5:
        server_host, server_port, method, path = sys.argv[1:]

        connection = socket()
        connection.connect((server_host, int(server_port)))

        print request[method](connection, server_host, path)

    # TODO: HTTPS
    if len(sys.argv) == 6:
        if sys.argv[1] == '-x':
            server_host, server_port, method, path = sys.argv[2:]

            connection = get_ssl_context(ssl.PROTOCOL_TLSv1, ssl.CERT_REQUIRED, True)\
                            .wrap_socket(socket(), server_hostname=server_host)
            connection.connect((server_host, int(server_port)))

            print request[method](connection, server_host, path)

        else:
            raise UsageError()

    else:
        raise UsageError()