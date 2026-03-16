import telebot
import subprocess
import sys
import os
import threading
import http.server
import socketserver

# --- AYARLAR ---
TOKEN = "8329769755:AAHmwTY0UWSu16pec8dhZFdq3Gtf8yiaaLw"
bot = telebot.TeleBot(TOKEN)

# --- YÖNETİCİ AYARLARI ---
OWNER_ID = 8523396063
VIP_USERS = [OWNER_ID] 

aktif_islemler = {}

# Render'ın uyumasını engelleyen sunucu
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except:
        pass

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- SMS GÖNDERME FONKSİYONU ---
def operasyon_baslat(message, numara, mod_turu):
    user_id = message.from_user.id
    try:
        if mod_turu == "turbo":
            bot.send_message(message.chat.id, f"🚀 {numara} için **Turbo (Mod 2)** başlatıldı. Durdurana kadar devam eder!")
            # 2 (Mod) -> Numara -> Enter (Mail Boş)
            girdiler = f"2\n{numara}\n\n" 
        else:
            bot.send_message(message.chat.id, f"✅ {numara} için **Normal (Mod 1)** başlatıldı...\n🔢 Adet: 200\n⏱️ Aralık: 3 sn")
            # SENİN SIRALAMAN: 
            # 1 (Mod) -> Numara -> Enter (Mail Boş) -> 200 (Adet) -> 3 (Aralık)
            girdiler = f"1\n{numara}\n\n200\n3\n"

        # Arka planda enough.py'yi çalıştırır
        process = subprocess.Popen(
            [sys.executable, "enough.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        aktif_islemler[user_id] = process
        process.stdin.write(girdiler)
        process.stdin.flush()
        
        process.wait()
        
        if user_id in aktif_islemler:
            del aktif_islemler[user_id]

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Hata: {str(e)}")

# --- TELEGRAM KOMUTLARI ---

@bot.message_handler(commands=['start'])
def welcome(message):
    msg = (
        "🚀 **SMS-BOT-TR PANELİ** 🚀\n\n"
        "👉 `/sms numara` (200 Adet / 3 Saniye)\n"
        "👉 `/turbo numara` (Sonsuz VIP Mod)\n"
        "👉 `/durdur` (Saldırıyı Kes)\n"
        "👉 `/id` (ID öğren)"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['durdur'])
def stop_attack(message):
    user_id = message.from_user.id
    if user_id in aktif_islemler:
        process = aktif_islemler[user_id]
        process.kill() 
        del aktif_islemler[user_id]
        bot.reply_to(message, "🛑 İşlem durduruldu.")
    else:
        bot.reply_to(message, "🧐 Şu an aktif bir işlemin yok.")

@bot.message_handler(commands=['vip_ekle'])
def add_vip(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Yetkin yok!")
        return
    try:
        yeni_id = int(message.text.split()[1])
        if yeni_id not in VIP_USERS:
            VIP_USERS.append(yeni_id)
            bot.reply_to(message, f"✅ `{yeni_id}` VIP yapıldı.")
    except:
        bot.reply_to(message, "❌ Kullanım: /vip_ekle ID")

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"🆔 ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['sms'])
def normal_attack(message):
    parcalar = message.text.split()
    if len(parcalar) < 2:
        bot.reply_to(message, "❌ Örnek: `/sms 5051112233`")
        return
    threading.Thread(target=operasyon_baslat, args=(message, parcalar[1], "normal")).start()

@bot.message_handler(commands=['turbo'])
def turbo_attack(message):
    if message.from_user.id not in VIP_USERS:
        bot.reply_to(message, "⚠️ VIP olmalısın!")
        return
    parcalar = message.text.split()
    if len(parcalar) < 2:
        bot.reply_to(message, "❌ Örnek: `/turbo 5051112233`")
        return
    threading.Thread(target=operasyon_baslat, args=(message, parcalar[1], "turbo")).start()

if __name__ == "__main__":
    print("--- BOT OPERASYON DOSYASI AKTİF ---")
    bot.infinity_polling()
