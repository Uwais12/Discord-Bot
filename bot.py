# bot.py
import os
import discord
from dotenv import load_dotenv
import random
import time
import requests
import json
from pprint import pprint
from datetime import date
import websocket
import threading
from threading import Timer



#1
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#2
bot = commands.Bot(command_prefix='!')

client = discord.Client()

# def hello():
#     threading.Timer(5.0, hello).start()
#     print('hello')

@bot.event
async def on_ready():
    print(f'{bot.user.name} is connected to the following server:\n')
    #await stocknews("appl", 1)
    # hello()

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my discord server'
    )

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Youre not worthy of doing this (you dont have the right role for it)')

@bot.command(name='roll_dice', help='<numberOfDice> <numberOfSides>')
async def roll(ctx, noDice: int, noSides: int):
    dice = [
        str(random.choice(range(1, noSides + 1)))
        for _ in range(noDice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='create-channel', help= '<channel name>')
@commands.has_role('admin')
async def create_channel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)
        await ctx.send(channel_name + ' Created')


@bot.command(name='xo', help='Tic Tac Toe')
async def xo(ctx):
    setPlayer1 = await ctx.send('Player 1 Name: ')
    player1reply =  await bot.wait_for('message')
    channel = player1reply.channel.id
    player1 = player1reply.author
    def check (m):
        return m.channel.id == channel
    setPlayer2 = await ctx.send('Player 2 Name: ')
    player2reply =  await bot.wait_for('message', check=check)
    player2 = player2reply.author
    
    won = False
    board = [
        '-','-','-',
        '-','-', '-',
        '-','-','-'
    ]
    
    while not won:
        p1answer = False
        p2answer = False
        player1p = False
        player2p = False
        l1 = await ctx.send(board[0]+ "   |   " +board[1]+"   |   "+board[2])
        l2 = await ctx.send(board[3]+ "   |   " +board[4]+"   |   "+board[5])
        l3 = await ctx.send(board[6]+ "   |   " +board[7]+"   |   "+board[8])

        play1 = await ctx.send('Player 1:\n')
        p1 = await bot.wait_for('message', check=check)

        while not player1p:
            if p1.author == player1:
                while not p1answer:
                    if p1:
                        await play1.delete()
                        await p1.delete()
                        if board[int(p1.content)-1]!= '-':
                            whoops = await ctx.send('This space is taken\nTry somewhere else')
                            play1 = await ctx.send('Player 1:\n')
                            p1 = await bot.wait_for('message', check=check)
                            await whoops.delete()
                        else:
                            p1answer = True

                player1p = True
            else:
                wrong = await ctx.send('Wrong Person!')
                play1 = await ctx.send('Player 1:\n')
                p1 = await bot.wait_for('message', check=check)
                await wrong.delete()

        board[int(p1.content)-1] = 'O'

        await l1.delete()
        await l2.delete()
        await l3.delete()

        l1 = await ctx.send(board[0]+ "   |   " +board[1]+"   |   "+board[2])
        l2 = await ctx.send(board[3]+ "   |   " +board[4]+"   |   "+board[5])
        l3 = await ctx.send(board[6]+ "   |   " +board[7]+"   |   "+board[8])

        full = 0
        for i in range(9):
            if board[i] == 'O':
                full += 1
            elif board[i]=='X':
                full += 1
            else:
                full += 0
        if full == 9:
            await ctx.send('Its a draw')
            won = True
            break
        
        for k in range(3):
            if board[k] == 'O' and board[k+3] == 'O' and board[k+6] == 'O':
                await ctx.send('Player 1 has won')
                won = True
                break
            elif board[k*3] == 'O' and board[(k*3)+1] == 'O' and board[(k*3)+2] == 'O':
                await ctx.send('Player 1 has won')
                won = True
                break

        if board[0] == 'O' and board[4] == 'O' and board[8] == 'O':
            await ctx.send('Player 1 has won')
            won = True
            
        elif board[2] == 'O' and board[4] == 'O' and board[6] == 'O':
            await ctx.send('Player 1 has won')
            won = True

        play2 = await ctx.send('Player 2:\n')
        p2 = await bot.wait_for('message', check=check)

        while not player2p:    
            
            if p2.author == player2:
                while not p2answer:
                    if p2:
                        await play2.delete()
                        await p2.delete()
                        if board[int(p2.content)-1]!= '-':
                            whoops = await ctx.send('This space is taken\nTry somewhere else')
                            play2 = await ctx.send('Player 2:\n')
                            p2 = await bot.wait_for('message', check=check)
                            await whoops.delete()
                        else:
                            p2answer = True
                player2p = True
            else:
                wrong = await ctx.send('Wrong Person!')
                play2 = await ctx.send('Player 2:\n')
                p2 = await bot.wait_for('message', check=check)
                await wrong.delete()

        board[int(p2.content)-1] = 'X'

        for l in range(3):
            if board[l] == 'X' and board[l+3] == 'X' and board[l+6] == 'X':
                await ctx.send('Player 2 has won')
                won = True
                break
            elif board[l*3] == 'X' and board[(l*3)+1] == 'X' and board[(l*3)+2] == 'X':
                await ctx.send('Player 2 has won')
                won = True
                break
        if board[0] == 'X' and board[4] == 'X' and board[8] == 'X':
            await ctx.send('Player 2 has won')
            won = True
            
        elif board[2] == 'X' and board[4] == 'X' and board[6] == 'X':
            await ctx.send('Player 2 has won')
            won = True

        await l1.delete()
        await l2.delete()
        await l3.delete()

@bot.command(name='gp', help='Guesspionage game')
async def guesspionage(ctx):
    await ctx.send('-----GUESSPIONAGE-----')
    player_info = []
    q1 = await ctx.send('How man people are playing?')
    noPlayers = await bot.wait_for('message')
    channel = noPlayers.channel.id
   
    def check (m):
        return m.channel.id == channel

    await q1.delete()
    await noPlayers.delete()

    for i in range (int(noPlayers.content)):
        q2 = await ctx.send('Player  name: ')
        pname = await bot.wait_for('message', check=check)
    
        
        player_info.append(
            {
            "name": pname.content,
            "playerID": pname.author,
            "points": 0
            }
        )
        await q2.delete()
        await pname.delete()

    await ctx.send('Players:')
    for i in range (int(noPlayers.content)):  
        await ctx.send(player_info[i]["name"])

    for i in range (1):
        answered = False
        guessernumb = random.randint(0, (int(noPlayers.content)-1))
        guesser = player_info[guessernumb]
        r1 = await ctx.send(f'{guesser["name"]} is Guessing first')
        time.sleep(1)
        question = 'How many people think uzair is fat?'
        actualAnswer = 78
        question1 = await ctx.send(f'{question}')
        uAnswer = await bot.wait_for('message', check=check)
        answer = int(uAnswer.content)
        await ctx.send(answer)
        for i in range (int(noPlayers.content)):
            ansered = False
            if i == guessernumb:
                if i !=  (int(noPlayers.content))-1:
                    i+=1
                else:
                    ansered = True
                    break
            else:
                await ctx.send(f'{player_info[i]["name"]} Higher or Lower?')
                pans = await bot.wait_for('message', check=check)
                
                while not answered:
                    if pans.author != player_info[i]["playerID"]:
                        await ctx.send('NOT YOU')
                        pans = await bot.wait_for('message', check=check)
                    else:
                        answered = True
                        break

                if answer < actualAnswer:
                    if pans.content == 'higher':
                        player_info[i]["points"] += 50
                        i+=1
                    
                    else:
                        player_info[i]["points"] += 0
                        i+=1
                
                elif answer > actualAnswer:
                    if pans.content == 'lower':
                        player_info[i]["points"] += 50
                        i+=1
                    
                    else:
                        player_info[i]["points"] += 0
                        i+=1
                
                else:
                    await ctx.send('Thats ur turn wasted')

        await ctx.send('The answer was '+actualAnswer)
        for l in range (int(noPlayers.content)-1):
            await ctx.send(f'{player_info[l]["name"]} - {player_info[l]["points"]}')

@bot.command(name='sn', help='Gives latest stock news <tickerSymbol> <numberOfStories>')
async def stocknews(ctx, symbol, numberOfStories: int):
    token = "bus4rv748v6t07kq4fg0"
    today = date.today()
    base_url = 'https://finnhub.io/api/v1/company-news?'
    r = requests.get(base_url, params={'symbol':symbol, 'token':token, 'from':'2020-01-01', 'to':today})
    text = r.text
    company_news = json.loads(text)
    
    
    for i in range (numberOfStories):
        summary = company_news[:numberOfStories][numberOfStories-1-i]['summary']
        link = company_news[:numberOfStories][numberOfStories-1-i]['url']
        datet = company_news[:numberOfStories][numberOfStories-1-i]['datetime']
        pic = company_news[:numberOfStories][numberOfStories-1-i]['image']
        embed=discord.Embed(title="Latest News", description=summary, color=0x00ff00, url=link)
        embed.set_image(url=pic)
        embed.set_footer(text=datet)
        embed.add_field(name='Link', value=link)
        await ctx.channel.send(embed=embed)

@bot.command(name='sest', help='Gives latest stock estimates <tickerSymbol>')
async def stock_estimates(ctx, symbol):
    token = "bus4rv748v6t07kq4fg0"
    base_url = "https://finnhub.io/api/v1/stock/price-target?"
    r = requests.get(base_url, params = {'symbol':symbol,'token':token})
    text = r.text

    company_price_target = json.loads(text)
    lupdate = company_price_target['lastUpdated']
    symbol1 = company_price_target['symbol']
    targetHigh1 = company_price_target['targetHigh']
    targetLow1 = company_price_target['targetLow']
    targetMean1 = company_price_target['targetMean']
    targetMedian1 = company_price_target['targetMedian']
    embed1=discord.Embed(title="StockEstimates", description=symbol1, color=0x00ff00)
    embed1.set_footer(text='Last Updated: '+lupdate)
    embed1.add_field(name="Target High", value=targetHigh1, inline=True)
    embed1.add_field(name="Target Low", value=targetLow1, inline=True)
    embed1.add_field(name='Target Mean', value=targetMean1, inline=False)
    embed1.add_field(name='Target Median', value=targetMedian1, inline=False)
    await ctx.channel.send(embed=embed1)

@bot.command(name='recom', help='Gives latest stock recommendatins <tickerSymbol> <numberOfRecommendations>')
async def stocknews(ctx, symbol, numberOfRecoms: int):
    token = "bus4rv748v6t07kq4fg0"
    today = date.today()
    base_url = "https://finnhub.io/api/v1/stock/recommendation?"
    r = requests.get(base_url, params = {'symbol':symbol,'token':token})
    text = r.text
    company_reccom = json.loads(text)
    
    for i in range (numberOfRecoms):
        symbol = company_reccom[:numberOfRecoms][numberOfRecoms-i-1]['symbol']
        buy = company_reccom[:numberOfRecoms][numberOfRecoms-i-1]['buy']
        hold = company_reccom[:numberOfRecoms][numberOfRecoms-i-1]['hold']
        sell = company_reccom[:numberOfRecoms][numberOfRecoms-i-1]['sell']
        strongbuy = company_reccom[:numberOfRecoms][numberOfRecoms-i-1]['strongBuy']
        period = company_reccom[:numberOfRecoms][numberOfRecoms-i-1]['period']
        strongsell = company_reccom[:numberOfRecoms][numberOfRecoms-i-1]['strongSell']
        embed=discord.Embed(title="Recommendations", description=symbol, color=0x00ff00)
        embed.set_footer(text="Period: "+period)
        embed.add_field(name="Buy", value=buy, inline=True)
        embed.add_field(name="Hold", value=hold, inline=True)
        embed.add_field(name='Sell', value=sell, inline=False)
        embed.add_field(name='Strong Buy', value=strongbuy, inline=True)
        embed.add_field(name='Strong Sell', value=strongsell, inline=True)
        await ctx.channel.send(embed=embed)

@bot.command(name='fin', help='Gives latest stock financials <tickerSymbol>')
async def stock_finacials(ctx, symbol):
    token = "bus4rv748v6t07kq4fg0"
    base_url = 'https://finnhub.io/api/v1/stock/metric?'
    r = requests.get(base_url, params = {'symbol': symbol, 'token':token,'metric':'price'})
    text = r.text
    company_basic_financials = json.loads(text)
    tenDayAvg = company_basic_financials['metric']['10DayAverageTradingVolume']
    thirtWeekReturn = company_basic_financials['metric']['13WeekPriceReturnDaily']
    fiveTwoHigh = company_basic_financials['metric']['52WeekHigh']
    fTHDate = company_basic_financials['metric']['52WeekHighDate']
    symbol = company_basic_financials['symbol']
    
    embed1=discord.Embed(title="Stock Financials", description=symbol, color=0x00ff00)
    embed1.add_field(name="10 Day Average", value=tenDayAvg, inline=False)
    embed1.add_field(name="13 Week Price Return Daily", value=thirtWeekReturn, inline=False)
    embed1.add_field(name='52 Week High', value=fiveTwoHigh, inline=True)
    embed1.add_field(name='52 Week High Date', value=fTHDate, inline=True)
    await ctx.channel.send(embed=embed1)



