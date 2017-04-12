#!/usr/bin/python2.7

import sys, ssl
from socket import socket
from ssl import SSLContext


CHINTU_IP = '10.1.38.225'


class UsageError(Exception):
    def __init__(self):
        super(UsageError, self).__init__('client.py [-x] <server_host> <server_port> <method> <path>\n'
                                         'client.py --config <username|password> <value>')


def secure(message, username, password):
    if username is not None:
        return message + 'Username: {0}\nPassword: {1}\n'.format(username, password)
    else:
        return message


def get(connection, host, path, language='en-us', encoding='None', username=None, password=None):
    connection.send(secure(
        'GET {0} HTTP/1.1\r\n'
        'User-Agent: Customer1.0\r\n'
        'Host: {1}\r\n'
        'Accept-Language: {2}\r\n'
        'Accept-Encoding: {3}\r\n'
        'Connection: Keep-Alive\r\n'
        .format(path, host, language, encoding), username, password
    ))
    return connection.recv(1024)


def post(connection, host, path, language='en_us', encoding='None', username=None, password=None):
    '''Posts a username and password'''
    message = 'username={0}&password={1}'.format(raw_input('Username: '), raw_input('Password: '))
    connection.send(secure(
        'POST {0} HTTP/1.1\r\n'
        'User-Agent: Customer1.0\r\n'
        'Host: {1}\r\n'
        'Accept-Language: {2}\r\n'
        'Accept-Encoding: {3}\r\n'
        'Connection: Keep-Alive\r\n'
        '\n{4}'
        .format(path, host, language, encoding, message), username, password
    ))
    return connection.recv(1024)


def put(connection, host, path, language='en_us', encoding='None', username=None, password=None):
    message = 'username={0}&password={1}'.format(path.split('/')[-1], raw_input('Password: '))
    connection.send(secure(
        'PUT {0} HTTP/1.1\r\n'
        'User-Agent: Customer1.0\r\n'
        'Host: {1}\r\n'
        'Accept-Language: {2}\r\n'
        'Accept-Encoding: {3}\r\n'
        'Connection: Keep-Alive\r\n'
        '\n{4}'
        .format(path, host, language, encoding, message), username, password
    ))
    return connection.recv(1024)


request = {
    'GET': get,
    'get': get,
    'POST': post,
    'post': post,
    'PUT': put,
    'put': put,
}


if __name__ == '__main__':
    print len(sys.argv)

    def get_ssl_context(protocol, verify_mode, check_hostname):
        context = ssl.SSLContext(protocol)
        context.verify_mode = verify_mode
        context.check_hostname = check_hostname
        context.load_default_certs()
        return context

    if sys.argv[1] == '--config' and len(sys.argv) == 4:
        if sys.argv[2] in ['username', 'password']:
            f = open(sys.argv[2])
            f.write(sys.argv[3])
            f.close()
        else:
            raise UsageError()

    elif len(sys.argv) == 5:
        server_host, server_port, method, path = sys.argv[1:]

        connection = socket()
        connection.connect((server_host, int(server_port)))

        print request[method](connection, server_host, path)

    # TODO: HTTPS
    elif len(sys.argv) == 6:
        if sys.argv[1] == '-x':
            server_host, server_port, method, path = sys.argv[2:]

            # connection = get_ssl_context(ssl.PROTOCOL_TLSv1, ssl.CERT_REQUIRED, True)\
            #     .wrap_socket(socket(), server_hostname=server_host)
            # connection.connect((server_host, int(server_port)))
            connection = socket()
            connection.connect((server_host, int(server_port)))

            f = open('username', 'r')
            username = f.read(1024)
            f.close()

            f = open('password', 'r')
            password = f.read(1024)
            f.close()

            print request[method](connection, server_host, path, username, password)

        else:
            raise UsageError()

    else:
        raise UsageError()