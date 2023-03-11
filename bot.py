import asyncio
import discord
from discord.ext import commands
import mysql.connector
import string
import random
import datetime

# ify i znaki
TOKEN = "MTA3ODExNzU4MTMwMDQzMjkzNw.G0eDA-.Va-2JYHdzhc1tJgDk-9qeYRLxID4xb79aT8xO8"
DB_HOST = "sql8.freemysqlhosting.net"
DB_USER = "sql8602922"
DB_PASS = "N529MjlXlf"
DB_NAME = "sql8602922"
#bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents) 
bot.remove_command("help")

# Połączenie z bazą danych
mydb = mysql.connector.connect(
  host=DB_HOST,
  user=DB_USER,
  password=DB_PASS,
  database=DB_NAME
)
#komendy mod i pomoc
@bot.command()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    embed = discord.Embed(title="Clear", description=f"Usunięto {amount} wiadomości.", color=discord.Color.green())
    await ctx.send(embed=embed, delete_after=5)

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="Pomoc", color=0xff0000)
    embed.add_field(name="", value="Prefix bota to !", inline=False)
    embed.add_field(name="Licencje", value="!licencja genruje licencje na zawsze", inline=False)
    embed.add_field(name="Licencja time", value="!licencjatime generuje licencje casowa np: !licencja 30(30day bez day musi byc)", inline=False)
    embed.set_footer(text="ISTERBOX")
    await ctx.send(embed=embed)

#weryfikacja
@bot.command()
async def verify(ctx, role: discord.Role, title: str, description: str, button_label: str):
    embed = discord.Embed(title=title, description=description)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('✅')

    verified_users = []

    def check(reaction, user):
        return (
            user != bot.user
            and str(reaction.emoji) == '✅'
            and reaction.message.id == msg.id
            and user not in verified_users
        )

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', check=check)
        except asyncio.TimeoutError:
            break
        else:
            await user.add_roles(role)
            verify_embed = discord.Embed(title="Weryfikacja", description=f"{user.mention} pomyślnie zweryfikowany.")
            verify_msg = await ctx.send(embed=verify_embed)
            verified_users.append(user)
            await msg.remove_reaction('✅', user)
            await asyncio.sleep(1)
            await verify_msg.delete()
#Licencje
# Funkcja generująca losową licencję i zapisująca ją do bazy danych MySQL
def generate_license_and_save():
    letters_and_digits = string.ascii_uppercase + string.digits
    license_key = ''.join(random.choice(letters_and_digits) for i in range(16))

    # Zapisywanie licencji do bazy danych MySQL
    mycursor = mydb.cursor()
    sql = "INSERT INTO licenses (license_key) VALUES (%s)"
    val = (license_key,)
    mycursor.execute(sql, val)
    mydb.commit()

    return license_key

# Obsługa zdarzenia generowania licencji
@bot.command()
async def licencja(ctx):
    license_key = generate_license_and_save()

    await ctx.send(f"Oto wygenerowana licencja: {license_key}")

# tworzymy komendę
@bot.command()
async def licencjatime(ctx, dni: int):
    # generujemy losowy ciąg dla licencji
    license_key = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    
    # obliczamy datę wygaśnięcia licencji
    expiration_date = datetime.date.today() + datetime.timedelta(days=dni)
    
    # zapisujemy licencję do bazy danych wraz z datą wygaśnięcia
    mycursor = mydb.cursor()
    sql = "INSERT INTO licenses (license_key, expiration_date) VALUES (%s, %s)"
    val = (license_key, expiration_date)
    mycursor.execute(sql, val)
    mydb.commit()

    # wysyłamy wygenerowaną licencję w wiadomości na czacie
    await ctx.send(f"Twoja licencja czasowa na {dni} dni to: {license_key}. Wygasa ona dnia {expiration_date}")

#Wlanczanie bota
bot.run(TOKEN)
