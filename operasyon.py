import telebot
import subprocess
import sys
import os
import time
import threading
import http.server
import socketserver

# --- AYARLAR ---
TOKEN = "8329769755:AAHmwTY0UWSu16pec8dhZFdq3Gtf8yiaaLw"
bot = telebot.TeleBot(TOKEN)

# VIP kullanıcıların ID'lerini buraya ekle (Kendi ID'ni @userinfobot'tan öğrenebilirsin)
VIP_USERS = [12345678] # Kendi ID'ni buraya yaz

# Render'ın kapanmasını engellemek için sahte port
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- SMS GÖNDERME FONKSİYONU (HER KULLANICI İÇİN AYRI ÇALIŞIR) ---
def operasyon_baslat(message, numara, mod_turu):
    try:
        if mod_turu == "turbo":
            bot.send_message(message.chat.id, f"🚀 {numara} için **Turbo (Mod 2)** operasyonu başladı!", parse_mode="Markdown")
            girdiler = f"2\n{numara}\n\n100\n" # Turbo'da 100 SMS
        else:
            bot.send_message(message.chat.id, f"✅ {numara} için **Normal (Mod 1)** operasyonu başladı!", parse_mode="Markdown")
            girdiler = f"1\n{numara}\n\n25\n" # Normal'de 25 SMS

        # Her saldırı kendi sürecinde (process) çalışır, botu kilitlemez
        process = subprocess.Popen(
            [sys.executable, "enough.py"],
            stdin=subprocess.PIPE,
            text=True
        )
        process.stdin.write(girdiler)
        process.stdin.flush()
        
        # İşlem bitene kadar bekler (veya process.wait() eklenebilir)
        # Çoklu kullanım için process takibi burada lokal kalmalı
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)}")

# --- KOMUTLAR ---
@bot.message_handler(commands=['start'])
def welcome(message):
    msg = (
        "🚀 **Enough-Reborn Kontrol Paneli**\n\n"
        "Sanal VDS üzerinden 7/24 Aktif!\n\n"
        "Kullanım:\n"
        "👉 `/sms 5051112233` (Normal)\n"
        "👉 `/turbo 5051112233` (VIP Özel)"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['sms'])
def normal_attack(message):
    komut_parcalari = message.text.split()
    if len(komut_parcalari) < 2:
        bot.reply_to(message, "❌ Kullanım: /sms 5051112233")
        return
    
    numara = komut_parcalari[1]
    # Arka planda yeni bir iş parçacığı açar (Bot donmaz, başkası da kullanabilir)
    threading.Thread(target=operasyon_baslat, args=(message, numara, "normal")).start()

@bot.message_handler(commands=['turbo'])
def turbo_attack(message):
    if message.from_user.id not in VIP_USERS:
        bot.reply_to(message, "⚠️ **Turbo Mod sadece VIP üyeler içindir!**\nSatın almak için: @KendiKullaniciAdin", parse_mode="Markdown")
        return

    komut_parcalari = message.text.split()
    if len(komut_parcalari) < 2:
        bot.reply_to(message, "❌ Kullanım: /turbo 5051112233")
        return
    
    numara = komut_parcalari[1]
    # VIP kullanıcı için Turbo işlem başlatır
    threading.Thread(target=operasyon_baslat, args=(message, numara, "turbo")).start()

# --- BOTU ÇALIŞTIR ---
def run_bot():
    print("--- SMS BOTU VDS MODUNDA AKTİF ---")
    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=30)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
