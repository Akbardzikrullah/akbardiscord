import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# 1. SETUP INTENTS
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. SETTING ID CHANNEL DISCORD KAMU
LOG_CHANNEL_ID = 1512126729399828621 

# FUNGSI PEMBUAT GAMBAR YANG SUDAH DI-UPDATE (Menerima jenis background)
def buat_gambar_log(avatar_bytes, username, status_text, jenis_gambar="welcome"):
    """
    Fungsi otomatis untuk menggambar avatar dan teks.
    jenis_gambar bisa diisi: "welcome" atau "leave"
    """
    
    # Pilih background berdasarkan jenisnya
    if jenis_gambar == "welcome":
        nama_file_bg = "background.png" # Gambar welcome lama kamu
    else:
        nama_file_bg = "background_leave.png" # Gambar leave BARU kamu

    try:
        # Buka template background yang dipilih
        base_img = Image.open(nama_file_bg).convert("RGBA")
    except FileNotFoundError:
        # Cadangan jika file gambar leave belum di-upload
        base_img = Image.new("RGBA", (800, 450), color=(50, 50, 50, 255))
        draw_error = ImageDraw.Draw(base_img)
        draw_error.text((400, 225), f"Error: {nama_file_bg} hilang", fill="white", anchor="mm")
        
    
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
    
    try:
        font_besar = ImageFont.truetype("font.ttf", 55) # Ukuran tulisan WELCOME/SAYONARA
        font_kecil = ImageFont.truetype("font.ttf", 32) # Ukuran tulisan nama akun
    except:
        font_besar = ImageFont.load_default()
        font_kecil = ImageFont.load_default()
    
    # Atur warna teks berdasarkan jenis gambar agar serasi
    warna_teks = "white"
    if jenis_gambar == "leave":
        warna_teks = "lightgray" # Contoh: dibikin rada pudar kalau leave
    
    # Gambar teks utama tepat di bawah foto profil
    draw.text((400, 310), status_text, font=font_besar, fill=warna_teks, anchor="mm")
    
    # Gambar nama akun Discord orang tersebut
    draw.text((400, 375), username, font=font_kecil, fill=warna_teks, anchor="mm")
    
    # Simpan hasil gambar ke memori sementara (RAM)
    buffer_gambar = io.BytesIO()
    base_img.save(buffer_gambar, format="PNG")
    buffer_gambar.seek(0)
    
    return buffer_gambar

@bot.event
async def on_ready():
    print(f"=== Bot {bot.user.name} Sudah Online & Siap Memantau Server! ===")

@bot.event
async def on_member_join(member):
    """Kondisi 1: JOIN server secara otomatis"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel: return
        
    try:
        avatar_bytes = await member.display_avatar.read()
        # Perhatikan jenis_gambar="welcome"
        file_gambar = buat_gambar_log(avatar_bytes, str(member.name), status_text="WELCOME", jenis_gambar="welcome")
        discord_file = discord.File(fp=file_gambar, filename="welcome.png")
        await channel.send(f"Selamat datang {member.mention} di server kami! 🎉", file=discord_file)
    except Exception as e:
        print(f"Gagal memproses gambar welcome: {e}")

@bot.event
async def on_member_remove(member):
    """Kondisi 2: LEAVE / KELUAR server secara otomatis"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel: return
        
    try:
        avatar_bytes = await member.display_avatar.read()
        # DI SINI KUNCINYA: Pakai jenis_gambar="leave" dan teks "SAYONARA"
        file_gambar = buat_gambar_log(avatar_bytes, str(member.name), status_text="SAYONARA", jenis_gambar="leave")
        discord_file = discord.File(fp=file_gambar, filename="leave.png")
        await channel.send(f"Yah, {member.name} baru aja keluar dari server... 😢 Bye!", file=discord_file)
    except Exception as e:
        print(f"Gagal memproses gambar leave: {e}")

# Perintah tes ping biasa
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! Bot Warung Kiamat siap siaga memantau server! 🚀")

# Perintah pancingan untuk ngetes sistem gambar welcome (Background LAMA)
@bot.command()
async def tesjoin(ctx):
    """Ketik !tesjoin untuk memancing gambar welcome (Background Lama)"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel: return await ctx.send("ID Channel tidak ditemukan!")
        
    await ctx.send("⏳ Sedang memproses gambar pancingan welcome...")
    try:
        avatar_bytes = await ctx.author.display_avatar.read()
        # Pakai background welcome
        file_gambar = buat_gambar_log(avatar_bytes, str(ctx.author.name), status_text="WELCOME", jenis_gambar="welcome")
        discord_file = discord.File(fp=file_gambar, filename="welcome_test.png")
        await channel.send(f"⚠️ [TEST JOIN] Selamat datang {ctx.author.mention} di server kami! 🎉", file=discord_file)
    except Exception as e:
        await ctx.send(f"❌ Terjadi error: {e}")

# Perintah pancingan untuk ngetes sistem gambar leave (Background BARU)
@bot.command()
async def tesleave(ctx):
    """Ketik !tesleave untuk memancing gambar sayonara (Background Baru)"""
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel: return await ctx.send("ID Channel tidak ditemukan!")
        
    await ctx.send("⏳ Sedang memproses gambar pancingan leave...")
    try:
        avatar_bytes = await ctx.author.display_avatar.read()
        # Pakai background LEAVE (background_leave.png)
        file_gambar = buat_gambar_log(avatar_bytes, str(ctx.author.name), status_text="SAYONARA", jenis_gambar="leave")
        discord_file = discord.File(fp=file_gambar, filename="leave_test.png")
        await channel.send(f"⚠️ [TEST LEAVE] Yah, {ctx.author.name} baru aja keluar dari server... 😢 Bye!", file=discord_file)
    except Exception as e:
        await ctx.send(f"❌ Terjadi error: {e}")

# 3. KONEKSIKAN KE DISCORD DEVELOPER PORTAL
# PENTING: Masukkan TOKEN HASIL RESET PALING BARU di dalam tanda petik dua bawah ini!
TOKEN_BARU = "MTUxNTM2OTM0ODAyMDA0Mzg4Ng.GZtr13.28p8EsngECeOwGDdemIOxrijCJnj2PUrgU6t_E"

bot.run(TOKEN_BARU)