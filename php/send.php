<?php
if($argc < 4)
	die('Usage> '.basename(__FILE__). ' "/path/CertificateName.pem" "DeviceToken" "Message" "BadgeCount" '."\n");

$ssl_ctx = stream_context_create();
stream_context_set_option($ssl_ctx, 'ssl', 'local_cert', $argv[1]);
//stream_context_set_option($ssl_ctx, 'ssl', 'passphrase', '');

$deviceToken = $argv[2];
date_default_timezone_set('Asia/Taipei');

if( is_resource( $fp = stream_socket_client(
	'ssl://gateway.sandbox.push.apple.com:2195', 
	$err,
	$errstr, 
	60, 
	STREAM_CLIENT_CONNECT|STREAM_CLIENT_PERSISTENT, 
	$ssl_ctx
) ) ) {
	$payload = json_encode(
		array(
			'aps' => array(
				'alert' => $argv[3].' @ '.date('Ymd H:i:s'),
				'sound' => 'default',
				'badge' => $argc > 4 ? (int)$argv[4]: 0
			)
		)
	);

	echo "Payload:\n$payload\n";

	// Simple Notification Format
	// https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/Chapters/LegacyFormat.html
	//
	// content: Command, Token length, deviceToken(binary), Payload length, Payload data
	// bytes  :       1,            2,                  32,              2,            n
	//
	$packed_data = 
		// Command (Simple Notification Format)
		chr(0)
		// device token
		. pack('n', 32) . pack('H*', $deviceToken)
		// payload
		. pack('n', strlen($payload)) . $payload;

	if( !fwrite($fp, $packed_data, strlen($packed_data)) )
		echo "Failed\n";
	else
		echo "Done\n";
	fclose($fp);
}
