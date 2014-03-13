import json
import socket
import struct 
import binascii
import OpenSSL

import argparse
parser = argparse.ArgumentParser(description='Apple Push Notification Simple Command')
parser.add_argument('--cert', required=True, metavar='Certificate', type=str, help='Path for Certificate.pem')
parser.add_argument('--key', required=True, metavar='Privete Key', type=str, help='Path for PriveteKey.pem')

args = parser.parse_args()


try:
	ssl_ctx = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv3_METHOD)
	ssl_ctx.use_certificate(
		OpenSSL.crypto.load_certificate(
			OpenSSL.crypto.FILETYPE_PEM,
			open(args.cert).read()
		)
	)
	ssl_ctx.use_privatekey(
		OpenSSL.crypto.load_privatekey(
			OpenSSL.crypto.FILETYPE_PEM,
			open(args.key).read()
		)
	)

	connection = OpenSSL.SSL.Connection(ssl_ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM) )
	connection.connect(("feedback.sandbox.push.apple.com", 2196))

	connection.do_handshake()
	connection.setblocking(1)

	# The Feedback Service
	# https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/CommunicatingWIthAPS.html#//apple_ref/doc/uid/TP40008194-CH101-SW3
	# content: timestamp, token length, token
	# bytes  :         4,            2,     n

	# http://docs.python.org/2/library/struct.html#format-characters

	while True:
		data = connection.recv(4+2)
		if not data:
			break

		timestamp = None
		token_length = 0
		token = None
		token_hex = None
		if len(data) == 6:
			timestamp = struct.unpack('>I', data[0:4])
			token_length = struct.unpack('>H', data[4:2])
			token = connection.recv(token_length)
			if token_length == len(token):
				toke_hex = binascii.b2a_hex(token)
			print "Timestamp:", timestamp, "Token Length:", token_length, "Token Hex:", token_hex
	print "Done"
#except OpenSSL.SSL.Error, e:
except Exception, e:
	print "Exception:", e
	print "Debug: $ openssl s_client -connect feedback.sandbox.push.apple.com:2196 -cert", args.cert, "-key", args.key

connection.close()
