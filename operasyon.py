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

# --- YÖNETİCİ AYARLARI ---
# Senin ID numaran artık kurucu olarak tanımlı
OWNER_ID = 8523396063

# VIP Listesi (Bot başladığında kurucu otomatik VIP olur)
VIP_USERS = [OWNER_ID]

# Render'ın kapanmasını engellemek için sahte port sunucusu
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Render Portu {port} üzerinden aktif tutuluyor.")
            httpd.serve_forever()
    except Exception as e:
        print(f"Sunucu hatası: {e}")

# Port sunucusunu arka planda başlat
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- SMS GÖNDERME FONKSİYONU ---
def operasyon_baslat(message, numara, mod_turu):
    try:
        if mod_turu == "turbo":
            bot.send_message(message.chat.id, f"🚀 {numara} için **Turbo (Mod 2)** operasyonu başladı!", parse_mode="Markdown")
            # Turbo mod: 100 SMS gönderir
            girdiler = f"2\n{numara}\n\n100\n" 
        else:
            bot.send_message(message.chat.id, f"✅ {numara} için **Normal (Mod 1)** operasyonu başladı!", parse_mode="Markdown")
            # Normal mod: 25 SMS gönderir
            girdiler = f"1\n{numara}\n\n25\n"

        # enough.py dosyasını ayrı bir işlem olarak çalıştırır (Botu kilitlemez)
        process = subprocess.Popen(
            [sys.executable, "enough.py"],
            stdin=subprocess.PIPE,
            text=True
        )
        process.stdin.write(girdiler)
        process.stdin.flush()
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)}")

# --- YÖNETİCİ KOMUTLARI ---

@bot.message_handler(commands=['vip_ekle'])
def add_vip(message):
    # Sadece OWNER_ID bu komutu kullanabilir
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Bu yetki sadece Kurucuya (Nuri) aittir!")
        return
    
    try:
        yeni_id = int(message.text.split()[1])
        if yeni_id not in VIP_USERS:
            VIP_USERS.append(yeni_id)
            bot.reply_to(message, f"✅ `{yeni_id}` ID'li kullanıcı VIP listesine eklendi. Artık Turbo kullanabilir!", parse_mode="Markdown")
        else:
            bot.reply_to(message, "⚠️ Bu kullanıcı zaten VIP listesinde.")
    except:
        bot.reply_to(message, "❌ Kullanım: `/vip_ekle 12345678`", parse_mode="Markdown")

@bot.message_handler(commands=['id'])
def my_id(message):
    bot.reply_to(message, f"🆔 Senin ID numaran: `{message.from_user.id}`", parse_mode="Markdown")

# --- GENEL KOMUTLAR ---
@bot.message_handler(commands=['start'])
def welcome(message):
    msg = (
        "🚀 **Enough-Reborn Kontrol Paneli**\n\n"
        "Şu an Sanal VDS üzerinde 7/24 Aktif!\n\n"
        "👉 `/sms 5051112233` (Normal)\n"
        "👉 `/turbo 5051112233` (VIP Özel)\n"
        "👉 `/id` (ID numaranı öğren)\n\n"
        "👑 **Yönetici Notu:** Birini VIP yapmak için `/vip_ekle ID` yazabilirsin."
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['sms'])
def normal_attack(message):
    komut_parcalari = message.text.split()
    if len(komut_parcalari) < 2:
        bot.reply_to(message, "❌ Kullanım: /sms 5051112233")
        return
    numara = komut_parcalari[1]
    # Threading sayesinde aynı anda birden fazla kişi kullanabilir
    threading.Thread(target=operasyon_baslat, args=(message, numara, "normal")).start()

@bot.message_handler(commands=['turbo'])
def turbo_attack(message):
    if message.from_user.id not in VIP_USERS:
        bot.reply_to(message, "⚠️ **Turbo Mod sadece VIP üyeler içindir!**\nÜyelik için kurucuyla iletişime geçin.", parse_mode="Markdown")
        return
    komut_parcalari = message.text.split()
    if len(komut_parcalari) < 2:
        bot.reply_to(message, "❌ Kullanım: /turbo 5051112233")
        return
    numara = komut_parcalari[1]
    threading.Thread(target=operasyon_baslat, args=(message, numara, "turbo")).start()

# --- BOTU ÇALIŞTIR ---
def run_bot():
    print("--- SMS BOTU VDS MODUNDA AKTİF ---")
    while True:
        try:
            bot.infinity_polling(timeout=90, long_polling_timeout=30)
        except Exception as e:
            print(f"Hata oluştu, yeniden deneniyor: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
