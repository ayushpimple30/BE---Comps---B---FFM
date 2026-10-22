SUCHANA BMO FILE TRANSFER

FILES
- index.html: upload page
- upload.php: validates image and queues it
- api/next.php: token-protected endpoint the Pi polls
- server-config.example.php: copy to server-config.php and set token/base URL
- bmo-pull.sh: Raspberry Pi downloader
- uploads/bmo/: uploaded files
- data/queue.json: pending queue

SERVER INSTALL
1. Upload this folder's contents into a folder on your HTTPS website, e.g. https://suchana.space/bmo-transfer/.
2. Copy server-config.example.php to server-config.php.
3. Generate a token: openssl rand -hex 32
4. Put the token in server-config.php and in bmo-pull.sh (API_TOKEN). Keep it secret.
5. Set public_base_url in server-config.php and SERVER_BASE in bmo-pull.sh to the app base URL. If deployed at domain root, use https://suchana.space. If in /bmo-transfer, use https://suchana.space/bmo-transfer.
6. Ensure PHP fileinfo is enabled; uploads/bmo and data/queue.json must be writable by the PHP user. Set PHP upload_max_filesize=10M and post_max_size=12M or higher.
7. Protect data/ and server-config.php. The included .htaccess rules work on Apache; for Nginx, add equivalent deny rules. Prefer keeping secrets/data outside the public web root when possible.
8. Test the upload page over HTTPS.

RASPBERRY PI 5
sudo apt update && sudo apt install -y curl python3 file
Edit SERVER_BASE and API_TOKEN in bmo-pull.sh, then:
chmod +x bmo-pull.sh
./bmo-pull.sh
Files save to /home/bmo_received/.

SECURITY / LIMITATION
Use HTTPS and a long random secret. Never put the secret in HTML/JavaScript. Add rate limiting and retention cleanup before public production use. This simple queue marks items claimed when the Pi polls; it does not retry automatically if the Pi fails mid-download. For robust production use, add acknowledgements/lease expiry.
