<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
function reply(int $code,array $body): never { http_response_code($code); echo json_encode($body,JSON_UNESCAPED_SLASHES); exit; }
if ($_SERVER['REQUEST_METHOD']!=='POST') reply(405,['ok'=>false,'error'=>'POST only']);
if (!isset($_FILES['photo'])) reply(400,['ok'=>false,'error'=>'Choose an image first']);
$f=$_FILES['photo']; if ($f['error']!==UPLOAD_ERR_OK) reply(400,['ok'=>false,'error'=>'Upload error '.$f['error']]);
if ($f['size']<1 || $f['size']>10*1024*1024) reply(413,['ok'=>false,'error'=>'Image must be under 10 MB']);
$mime=(new finfo(FILEINFO_MIME_TYPE))->file($f['tmp_name']);
$allowed=['image/jpeg'=>'jpg','image/png'=>'png','image/webp'=>'webp','image/gif'=>'gif'];
if (!isset($allowed[$mime])) reply(415,['ok'=>false,'error'=>'Only JPG, PNG, WEBP, and GIF are allowed']);
$root=__DIR__; $up=$root.'/uploads/bmo'; $data=$root.'/data';
if (!is_dir($up)&&!mkdir($up,0750,true)) reply(500,['ok'=>false,'error'=>'Cannot create upload folder']);
if (!is_dir($data)&&!mkdir($data,0750,true)) reply(500,['ok'=>false,'error'=>'Cannot create data folder']);
$name=bin2hex(random_bytes(16)).'.'.$allowed[$mime]; $dest=$up.'/'.$name;
if (!move_uploaded_file($f['tmp_name'],$dest)) reply(500,['ok'=>false,'error'=>'Cannot save uploaded file']);
@chmod($dest,0640); $qf=$data.'/queue.json'; $fp=fopen($qf,'c+');
if (!$fp) { @unlink($dest); reply(500,['ok'=>false,'error'=>'Cannot open queue']); }
flock($fp,LOCK_EX); $q=json_decode(stream_get_contents($fp)?:'[]',true); if(!is_array($q))$q=[];
$q[]=['id'=>bin2hex(random_bytes(8)),'filename'=>$name,'created'=>time(),'status'=>'pending']; $q=array_slice($q,-100);
rewind($fp); ftruncate($fp,0); fwrite($fp,json_encode($q,JSON_PRETTY_PRINT)); fflush($fp); flock($fp,LOCK_UN); fclose($fp);
reply(200,['ok'=>true,'filename'=>$name]);
?>