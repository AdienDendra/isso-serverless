import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def lambda_handler(event, context):
    # 1. Ambil konfigurasi dari Environment Variables AWS
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = os.environ.get("adien.dendra@gmail.com")
    SENDER_PASSWORD = os.environ.get("bpibhvlkfaiogzxw") # App Password dari Google
    RECEIVER_EMAIL = os.environ.get("hello@adiendendra.com") # Email tujuan notifikasi
    
    # 2. Iterasi semua pesan yang masuk dari AWS SQS
    # SQS bisa mengirimkan beberapa pesan sekaligus dalam satu batch
    for record in event['Records']:
        try:
            # Ambil payload JSON yang dilempar oleh Lambda 1 (Isso)
            payload = json.loads(record['body'])
            
            author = payload.get("author", "Anonymous")
            comment = payload.get("comment", "(Kosong)")
            post_title = payload.get("post_title", "Unknown Post")
            
            # 3. Menyusun Struktur Email (Format Teks/HTML)
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = RECEIVER_EMAIL
            msg['Subject'] = f"📝 Komentar Baru di Blog: {post_title}"
            
            body = f"""
            Halo, ada komentar baru di blog Mas!
            
            Pengirim : {author}
            Artikel  : {post_title}
            Komentar :
            --------------------------------------------------
            {comment}
            --------------------------------------------------
            
            Silakan cek dashboard backend untuk melakukan moderasi jika diperlukan.
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # 4. Melakukan Koneksi Aman (TLS) ke Google SMTP
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls() # Mengaktifkan enkripsi jaringan
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            # Kirim email
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            server.quit()
            
            print(f"Berhasil mengirim email notifikasi untuk komentar dari {author}")
            
        except Exception as e:
            print(f"Gagal memproses pesan SQS atau kirim email. Error: {str(e)}")
            # Melempar exception agar SQS tahu pesan ini gagal dan harus dicoba lagi (retry)
            raise e
            
    return {
        'statusCode': 200,
        'body': json.dumps('Semua email notifikasi berhasil diproses!')
    }