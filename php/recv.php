<?php
if($argc < 2)
	die('Usage> '.basename(__FILE__). ' "/path/CertificateName.pem" '."\n");

$ssl_ctx = stream_context_create();
stream_context_set_option($ssl_ctx, 'ssl', 'local_cert', $argv[1]);
//stream_context_set_option($ssl_ctx, 'ssl', 'passphrase', '');

$deviceToken = $argv[2];
date_default_timezone_set('Asia/Taipei');

if( is_resource( $fp = stream_socket_client(
	'ssl://feedback.sandbox.push.apple.com:2196', 
	$err,
	$errstr, 
	60, 
	STREAM_CLIENT_CONNECT|STREAM_CLIENT_PERSISTENT, 
	$ssl_ctx
) ) ) {
	$debug_raw = '';
	while(!feof($fp))
	{
		$data = fread($fp, 4+2);
		echo "Read: ".strlen($data)."\n";
		if(strlen($data) == 6)
		{
			// The Feedback Service
			// https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/CommunicatingWIthAPS.html#//apple_ref/doc/uid/TP40008194-CH101-SW3
			// content: timestamp, token length, token
			// bytes  :         4,            2,     n

			// http://php.net/manual/en/function.pack.php

			// 4 bytes
			$timestamp = unpack("n*", substr($data, 0, 4));
			// 2 bytes
			$token_length = unpack("n", substr($data, 4, 2));

			// $token_length bytes
			$token = fread($fp, $token_length);
			echo "Read2: ".strlen($token)."\n";
			$token_hex = unpack("H*", $token);

			// result
			echo "Timestamp: $timestamp\nToken_length: $token_length\nToken: $token_hex\n";

			$debug_raw .= $data.$token;
		}
	}
	if(!empty($debug_raw))
		file_put_contents('/tmp/apns_feedback_raw_debug', $debug_raw);
	echo "Done\n";
	fclose($fp);
}
