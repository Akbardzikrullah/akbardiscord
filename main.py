import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# 1. SETUP INTENTS (Wajib aktif semua agar bot bisa membaca pesan dan data member masuk/keluar)
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. SETTING ID CHANNEL DISCORD KAMU
# ID Channel #welcome dari server secretone milikmu
LOG_CHANNEL_ID = 1512126729399828621 

def buat_gambar_log(avatar_bytes, username, status_text):
    """Fungsi otomatis untuk menggambar avatar kustom dan teks ke background"""
    # Buka template background.png yang ada di folder
    base_img = Image.open("background.png").convert("RGBA")
    
    # Olah foto profil user (downloaded via bytes)
    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar_img = avatar_img.resize((200, 200)) # Ukuran lingkaran foto profil
    
    # Membuat efek potong lingkaran (masking)
    mask = Image.new("L", (200, 200), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, 200, 200), fill=255)
    
    circular_avatar = ImageOps.fit(avatar_img, (200, 200), centering=(0.5, 0.5))
    circular_avatar.putalpha(mask)
    
    # Tempel foto profil ke tengah-tengah background template
    base_img.paste(circular_avatar, (300, 50), circular_avatar)
    
    # Menulis Teks Ucapan dan Username
    draw = ImageDraw.Draw(base_img)
    font_besar = ImageFont.truetype("font.ttf", 55) # Ukuran tulisan WELCOME/SAYONARA
    font_kecil = ImageFont.truetype("font.ttf", 32) # Ukuran tulisan nama akun
    
    # Gambar teks utama (WELCOME / SAYONARA) tepat di bawah foto profil
    draw.text((400, 310), status_text, font=font_besar, fill="white", anchor="mm")
    
    # Gambar nama akun Discord orang tersebut
    draw.text((400, 375), username, font=font_kecil, fill="white", anchor="mm")
    
    # Simpan hasil gambar ke memori sementara (RAM) agar tidak memenuhi harddisk
    buffer_gambar = io.BytesIO()
    base_img.save(buffer_gambar, format="PNG")
    buffer_gambar.seek(0)
    
    return buffer_gambar

@bot.event
async def on_ready():
    print(f"=== Bot {bot.user.name} Sudah Online & Siap Memantau Server! ===")

@bot.event
async def on_member_join(member):
    """Kondisi 1: Ketika ada akun yang baru JOIN server secara otomatis"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
        
    try:
        avatar_bytes = await member.display_avatar.read()
        file_gambar = buat_gambar_log(avatar_bytes, str(member.name), status_text="WELCOME")
        discord_file = discord.File(fp=file_gambar, filename="welcome.png")
        await channel.send(f"Selamat datang {member.mention} di server kami! 🎉", file=discord_file)
    except Exception as e:
        print(f"Gagal memproses gambar welcome: {e}")

@bot.event
async def on_member_remove(member):
    """Kondisi 2: Ketika ada akun yang LEAVE / KELUAR server secara otomatis"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
        
    try:
        avatar_bytes = await member.display_avatar.read()
        file_gambar = buat_gambar_log(avatar_bytes, str(member.name), status_text="SAYONARA")
        discord_file = discord.File(fp=file_gambar, filename="leave.png")
        await channel.send(f"Yah, {member.name} baru aja keluar dari server... 😢 Bye!", file=discord_file)
    except Exception as e:
        print(f"Gagal memproses gambar leave: {e}")

# Perintah tes ping biasa
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! Bot Warung Kiamat siap siaga memantau server! 🚀")

# Perintah pancingan untuk ngetes sistem gambar welcome tanpa perlu ada orang join asli
@bot.command()
async def tesjoin(ctx):
    """Ketik !tesjoin di server untuk memancing gambar welcome muncul menggunakan profilmu sendiri"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return await ctx.send("ID Channel tidak ditemukan, cek kembali LOG_CHANNEL_ID kamu!")
        
    await ctx.send("⏳ Sedang memproses gambar pancingan...")
    
    try:
        # Menggunakan data profil KAMU yang mengetik perintah untuk simulasi
        avatar_bytes = await ctx.author.display_avatar.read()
        
        # Jalankan fungsi canvas Pillow yang sama
        file_gambar = buat_gambar_log(avatar_bytes, str(ctx.author.name), status_text="WELCOME")
        
        # Kirim hasilnya ke channel welcome kamu
        discord_file = discord.File(fp=file_gambar, filename="welcome_test.png")
        await channel.send(f"⚠️ [TEST JOIN] Selamat datang {ctx.author.mention} di server kami! 🎉", file=discord_file)
        
    except Exception as e:
        await ctx.send(f"❌ Terjadi error saat membuat gambar: {e}")

# 3. KONEKSIKAN KE DISCORD DEVELOPER PORTAL
# PENTING: Masukkan TOKEN HASIL RESET PALING BARU di dalam tanda petik dua bawah ini!
TOKEN_BARU = ("MTUxNTM2OTM0ODAyMDA0Mzg4Ng.G-bqsJ.vMC1jV_k59Q9NqaIZEX-VSTK47LiYeQOnWdj1w")

bot.run(TOKEN_BARU)