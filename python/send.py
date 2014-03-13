import json
import socket
import struct 
import binascii
import OpenSSL

import argparse
parser = argparse.ArgumentParser(description='Apple Push Notification Simple Command')
parser.add_argument('--cert', required=True, metavar='Certificate', type=str, help='Path for Certificate.pem')
parser.add_argument('--key', required=True, metavar='Privete Key', type=str, help='Path for PriveteKey.pem')
parser.add_argument('--device-token', required=True, metavar='Device Token', type=str, help='Device Token (32 Bytes HEX Format)')
parser.add_argument('--message', required=True, metavar='Message', type=str, help='Message')
parser.add_argument('--badge', metavar='Badge Count', type=int, help='Badge count')

args = parser.parse_args()

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
connection.connect(("gateway.sandbox.push.apple.com", 2195))

connection.do_handshake()
connection.setblocking(1)

try:
	payload = {
		"aps":{
			"alert": args.message ,
			"sound": "default",
			"badge": args.badge if args.badge > 0 else 0
		}
	}
	payload_data = json.dumps(payload)
	print "Payload:\n", payload_data, "\n"

	# Simple Notification Format
	# https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/LegacyFormat.html
	#
	# content: Command, Token length, deviceToken(binary), Payload length, Payload data
	# bytes  :       1,            2,                  32,              2,            n

	# http://docs.python.org/2/library/struct.html#format-characters

	token = binascii.a2b_hex(args.device_token)

	# Command(0): 1 byte
	chunk = struct.pack('>B', 0)
	# Token Length: 2 bytes
	chunk = chunk + struct.pack('>H', len(token)) 
	# Token: n bytes
	chunk = chunk + token
	# Payload length: 2 bytes
	chunk = chunk + struct.pack('>H', len(payload_data))
	# Payload: n bytes
	payload_pack_format = '>%ds' % len(payload_data)
	chunk = chunk + struct.pack( payload_pack_format, payload_data)

	connection.sendall(chunk)
	
	print "Done"
#except OpenSSL.SSL.Error, e:
except Exception, e:
	print "Exception:", e
	print "Debug:"
	print "$ openssl s_client -connect feedback.sandbox.push.apple.com:2196 -cert", args.cert, "-key", args.key
	print "$ openssl s_client -connect gateway.sandbox.push.apple.com:2195 -cert", args.cert, "-key", args.key

connection.close()
