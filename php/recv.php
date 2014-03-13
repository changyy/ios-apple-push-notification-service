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
		if(strlen($data) == 6)
		{
			$debug_raw .= $data;

			// http://php.net/manual/en/function.pack.php
			$timestamp = unpack("n*", substr($data, 0, 4));
			$token_length = unpack("n", substr($data, 4, 2));
			$data = fread($fp, $token_length);
			$token_hex = unpack("H*", $data);
			echo "Timestamp: $timestamp\nToken_length: $token_length\nToken: $token_hex\n";

			$debug_raw .= $data;
		}
	}
	if(!empty($debug_raw))
		file_put_contents('/tmp/apns_feedback_raw_debug', $debug_raw);
	echo "Done\n";
	fclose($fp);
}
