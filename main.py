import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# 1. SETUP INTENTS (Wajib aktif semua agar bot bisa membaca pesan dan data member masuk/keluar)
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True # <-- Sudah ditambahkan agar bot responsif

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. SETTING ID CHANNEL DISCORD KAMU
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
    """Kondisi 1: Ketika ada akun yang baru JOIN server"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
        
    try:
        # Ambil foto profil akun yang baru join
        avatar_bytes = await member.display_avatar.read()
        
        # Buat gambarnya dengan teks WELCOME
        file_gambar = buat_gambar_log(avatar_bytes, str(member.name), status_text="WELCOME")
        
        # Kirim ke channel Discord
        discord_file = discord.File(fp=file_gambar, filename="welcome.png")
        await channel.send(f"Selamat datang {member.mention} di server kami! 🎉", file=discord_file)
    except Exception as e:
        print(f"Gagal memproses gambar welcome: {e}")

@bot.event
async def on_member_remove(member):
    """Kondisi 2: Ketika ada akun yang LEAVE / KELUAR server"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
        
    try:
        # Ambil foto profil akun yang leave
        avatar_bytes = await member.display_avatar.read()
        
        # Buat gambarnya dengan teks SAYONARA
        file_gambar = buat_gambar_log(avatar_bytes, str(member.name), status_text="SAYONARA")
        
        # Kirim ke channel Discord
        discord_file = discord.File(fp=file_gambar, filename="leave.png")
        await channel.send(f"Yah, {member.name} baru aja keluar dari server... 😢 Bye!", file=discord_file)
    except Exception as e:
        print(f"Gagal memproses gambar leave: {e}")

# Perintah tes untuk memastikan bot tidak bisu lagi
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! Bot Warung Kiamat siap siaga memantau server! 🚀")

# 3. KONEKSIKAN KE DISCORD DEVELOPER PORTAL
# PENTING: Masukkan TOKEN BARU yang sudah di-reset di sini!
TOKEN_BARU = "MASUKKAN_TOKEN_HASIL_RESET_DISINI"

bot.run("MTUxNTM2OTM0ODAyMDA0Mzg4Ng.G-bqsJ.vMC1jV_k59Q9NqaIZEX-VSTK47LiYeQOnWdj1w")