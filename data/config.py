import discord

async def get_nick(member: discord.Member):
    if member.nick is None:
        return member.name
    else:
        return member.nick

DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_HOST = 'localhost'
DB_PASS = '18273645'

TOKEN = 'ODYxMTk4MTA0OTMzNDMzMzg1.YOGTPA.334GREG0rMoiXLnxPimhzjf7INw'
staff = [857609646915059712, 858073863309361183, 858073863309361183, 858073863309361183, 858073863309361183, 703942596011229190]