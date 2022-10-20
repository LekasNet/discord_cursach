import discord
import sqlalchemy
from msg_reader import File
from discord.ext import commands
from config import settings, files
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Trees, Users, Registers, Base, Servers
from datetime import datetime
from time import sleep


intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.members = True


file = File('transitions.rsp')
file.reading()
file.information()
msg = file.printing()
print(msg)


roles = {'HSBG':'Hearthstone', 'Valorant':'Valorant', 'LoL':'lol', 'BrawlStars':'Brawl stars', 'wildrift':'Wild rift'}


bot = commands.Bot(command_prefix=settings['prefix'], intents=intents)
engine = create_engine('sqlite:///Trees.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


async def timer(channel, n):
    for i in range(n):
        await channel.send(embed=discord.Embed(
            description=f"{n - i - 1}"))
        sleep(1)



@bot.command()#
@commands.has_permissions( administrator=True )
async def permissions(ctx, *args):
    for arg in args:
        chnl, func = arg.split('-')
        channel = discord.utils.get(ctx.message.author.guild.channels, name=chnl)
        server = session.query(Servers).filter(Servers.func_nm == func).all()

        print(chnl, func, server[-1].func_nm)

        server[-1].oper_id = server[-1].oper_id
        server[-1].serv_id = 0
        server[-1].serv_nm = chnl
        server[-1].func_nm = func

        print(server[-1].oper_id, server[-1].serv_id, server[-1].serv_nm, server[-1].func_nm)

        session.commit()

        if func.isnumeric():
            await timer(channel, int(func))


@bot.event
async def on_member_join(member):

    func_name = "on_member_join"
    server = session.query(Servers).filter(Servers.func_nm == func_name).all()
    channel = discord.utils.get(ctx.message.author.guild.channels, name=server[-1].serv_nm)

    role = discord.utils.get(member.guild.roles, id=815554460276752416)

    await channel.send(embed=discord.Embed(
        description=f"{member.name}, приветствуем!"))
    await member.add_roles(role)

    action_card = session.query(Users).all()
    print(action_card[-1].user_id)

    user = action_card[-1].user_id + 1
    user_name = member.name

    user_card = Users(user_id=user, user_nm=user_name, tour_ct=0)
    session.add(user_card)
    session.commit()


@bot.command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')


@bot.command()
@commands.has_permissions( administrator=True )
async def tournament(ctx, name, max_usr_count):

    func_name = "tournament"
    server = session.query(Servers).filter(Servers.func_nm == func_name).all()
    channel = discord.utils.get(ctx.message.author.guild.channels, name=server[-1].serv_nm)

    member = ctx.message.author
    tour_card_in = session.query(Trees).all()

    tour_id = tour_card_in[-1].tour_id + 1
    tour_nm = name
    tour_dc = member.name
    tour_us = max_usr_count

    tour_card = Trees(tour_id=tour_id, tour_nm=tour_nm, tour_dc=tour_dc, tour_us=tour_us)
    session.add(tour_card)
    session.commit()

    await channel.send(embed=discord.Embed(
    description=
      f"Турнир {name} создан! Допустимое кол-во участников: {max_usr_count}. \n Чтобы зарегистрироваться пропишите <!register {tour_id}>"))


@bot.command()
async def register(ctx, tid):

    func_name = "register"
    server = session.query(Servers).filter(Servers.func_nm == func_name).all()
    channel = discord.utils.get(ctx.message.author.guild.channels, name=server[-1].serv_nm)

    member = ctx.message.author

    if not session.query(Trees).filter_by(tour_id=tid).all():
        await channel.send(embed=discord.Embed(description="Такого турнира не существует! Список турниров !list"))

    else:
        roles_id = {"1": 815536004382457876}
        role = discord.utils.get(member.guild.roles, id=roles_id["1"])

        await member.add_roles(role)
        await channel.send(embed=discord.Embed(
            description=
            f"{member.name} участвует в {discord.utils.get(member.guild.roles, id=815536004382457876)}"
        ))

    action_user = session.query(Users).filter_by(user_nm=member.name).all()[0].user_nm
    action_registration = session.query(Registers).all()[-1].regs_id + 1
    action_tour = tid
    action_date = datetime.now()

    registration_card = Registers(regs_id=action_registration, user_id=action_user,
                                  tour_id=action_tour, regs_dt=action_date)
    session.add(registration_card)
    session.commit()


@bot.command()
async def list(ctx, page=0):
  member = ctx.message.author
  channel = ctx.message.channel

  action_tourns = session.query(Trees).all()

  text = ""
  for i in range(1, len(action_tourns)):
    text += f"Name - ``{action_tourns[i].tour_nm}``, \tid - ``{action_tourns[i].tour_id}``, \tcreator - ``{action_tourns[i].tour_dc}``. \n"

  await channel.send(embed=discord.Embed(title="Список турниров:", description=text, color=0xfc0c0c))


@bot.command( pass_context=True )
@commands.has_permissions( administrator=True )
async def clear(ctx, count=0):
  if count==0 or count=="all":
    counter = 0
    async for message in ctx.channel.history():
      counter += 1
  else: counter = count
  await ctx.channel.purge(limit = counter + 1)


@bot.command( pass_context=True )
@commands.has_permissions( administrator=True )
async def delete(ctx, tid):
    session.query(Trees).filter(Trees.tour_id==tid).delete()
    session.commit()


@bot.command()
async def add_reactions(ctx, tour, *reacts):
    print(reacts)
    global msg
    await ctx.channel.purge(limit = 1)
    messages = await ctx.channel.history(limit=1).flatten()
    msg[str(messages[-1].id)] = tour
    file.writing({str(messages[-1].id): tour})
    if not len(reacts):
        reacts = ['1️⃣', '2️⃣', '3️⃣','4️⃣', '5️⃣', '6️⃣']
    for emoji in reacts:
        masg = await ctx.channel.fetch_message(messages[-1].id)
        await masg.add_reaction(emoji)
    

@bot.event
async def on_raw_reaction_add(payload):
    if (str(payload.message_id) in msg) and (payload.user_id != bot.user.id):
        channel = bot.get_channel(payload.channel_id)
        await channel.send(f'Получена реакция: {str(payload.emoji)}')

        # bot.remove_reaction(message.channel_id, message.message_id, message.name, message.user_id)

        message = await channel.fetch_message(payload.message_id)
        user = bot.get_user(payload.user_id)
        await message.remove_reaction(payload.emoji, user)
        print(payload.emoji)
        game = str(payload.emoji).split(':')[1]
        await message.channel.send(f"{user.mention}, зарегистрирован на {game}")
        role_nm = roles[game]
        print(role_nm)
        # await bot.add_roles(user, role) # выдаем автору роль

        print(user)
        guild = bot.get_guild(875612584060018708)
        member = guild.get_member(payload.user_id)
        role = discord.utils.get(member.guild.roles, name=f"{role_nm}")
        await member.add_roles(role)



@bot.command()
@commands.has_permissions( administrator=True )
async def del_reactions(ctx, tour=''):
    if tour == '':
        text = '\n'.join([i + ' ' + str(msg[i]) for i in msg])
        await ctx.channel.send(embed=discord.Embed(title="Список закреплённых реакций", description=text, color=0x0cfc0))
    elif tour == 'all':
        for j in range(len(msg)):
            for i in msg.keys():
                del msg[i]
                file.writing(msg)
                break
    else:
        for j in range(len(msg)):
            for i in msg.keys():
                if msg[i] == int(tour):
                    del msg[i]
                    file.writing(msg)
                    break



@bot.command()
async def info(ctx, page=0):
  text =  "***ВНИМАНИЕ!*** значения описанные в <> описываются БЕЗ них! \n (пример ``!clear 10`` - очистить 10 сообщений)"
  text += "```!info <page>```    - Справка (указывается номер страницы)"
  text += "```!clear <amount>``` - Очистить чат на количество сообщений (all очищает всё)"
  text += "```!list <page>```    - Список активных турниров (указывается номер страницы)"
  text += "```!register <id>```  - Зарегистрироваться на турнир (узнать id турнира можно в !list)"
  text += "```!tournament <name> <max_amount>``` - Создать турнир (только для администраторов)"
  text += "```!permissions <channel>-<func>``` - Задать канал по умолчанию (только для администраторов)"
  await ctx.channel.send(embed=discord.Embed(title="Справка:", description=text, color=0x0cfc0))




@bot.command()
async def test(ctx):
    await ctx.channel.purge(limit = 1)
    messages = await ctx.channel.history(limit=1).flatten()
    print(messages[-1].id)
    masg = await ctx.channel.fetch_message(messages[-1].id)
    print(masg.content)
    # print(msg)


bot.run(settings['token'])