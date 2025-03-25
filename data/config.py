import discord
import os

async def get_nick(member: discord.Member):
    if member.nick is None:
        return member.name
    else:
        return member.nick

DB_NAME = os.getenv('earth-bot-db-name')
DB_USER = os.getenv('earth-bot-db-user')
DB_HOST = os.getenv('earth-bot-db-host')
DB_PASS = os.getenv('earth-bot-db-pass')

TOKEN = os.getenv('earth-bot-token')
COINS = '<:earth_coin1:862282603636457543>'
staff = [857609646915059712, 858073863309361183, 858073863309361183, 858073863309361183, 858073863309361183]
events = ['CSGO 5x5', 'ALIAS', 'ANIME', 'BRAWLHALLA', 'CODENAMES', 'DOTA 2 5x5', 'GARTIC PHONE', 'ROBLOX', 'ФИЛЬМ']
limits = [10, 6, None, 5, 6, 10, 5, 8, None]
descs = ['Counter-Strike: Global Offensive — многопользовательская компьютерная игра, разработанная компаниями Valve и Hidden Path Entertainment.', 'Alias — салонная командно-индивидуальная или парная интеллектуальная игра, в которой игрок должен за небольшое время объяснить как можно больше слов, чтобы его партнер их отгадал.', 'Аниме — японская мультипликация. В отличие от мультфильмов других стран, предназначенных в основном для просмотра детьми, бо́льшая часть выпускаемого аниме рассчитана на подростковую и взрослую аудитории, и во многом за счёт этого имеет высокую популярность в мире.', 'Brawlhalla — free-to-play-файтинг разработанный и выпущенный Blue Mammoth Games для Microsoft Windows, macOS, PlayStation 4, Xbox One, Nintendo Switch, Android, iOS.', 'Игра представляет собой словесно-командное соревнование. Игроки делятся на две команды. Перед игроками выкладывается поле из 25 случайных слов. Каждому слову соответствует секретный агент той или иной команды (красной или синей), мирный житель или убийца. Капитаны двух команд по очереди озвучивают подсказку для своих игроков, чтобы привести их к словам, которые соответствуют своим агентам.', 'Dota 2 — компьютерная многопользовательская командная игра в жанре multiplayer online battle arena, разработанная корпорацией Valve. Игра является продолжением DotA — пользовательской карты-модификации для игры Warcraft III: Reign of Chaos и дополнения к ней Warcraft III: The Frozen Throne.', '«Сломанный телефон» — салонная игра, используемая также в качестве одного из инструментов психотренинга. Суть игры — в организации передачи устного сообщения по цепочке, состоящей из как можно большего количества людей, и выявлении искажений его исходного содержания.', 'Roblox — многопользовательская онлайн-платформа, которая позволяет пользователям создавать свои собственные и играть в созданные другими пользователями игры.', 'Фильм — произведение киноискусства, фильм как продукт художественного творчества, имеющий в основе вымышленный сюжет, воплощённый в сценарии и интерпретируемый режиссёром, который создаётся с помощью актёрской игры или средств мультипликации.']
picts = ['https://media.discordapp.net/attachments/859153448309096458/865278556607479838/CSGO.png?width=960&height=242', 'https://media.discordapp.net/attachments/859153448309096458/865278548260814888/ALIAS.png?width=960&height=242', 'https://media.discordapp.net/attachments/859153448309096458/865278549870903336/ANIME.png?width=960&height=242', 'https://media.discordapp.net/attachments/859153448309096458/865278552046567435/BRAWLHALLA.png?width=960&height=242', 'https://media.discordapp.net/attachments/859153448309096458/865278554942210078/CODENAMES.png?width=960&height=242', 'https://media.discordapp.net/attachments/859153448309096458/865278558296997908/DOTA2.png?width=960&height=242', 'https://media.discordapp.net/attachments/859153448309096458/865278563325968384/GARTIC_PHONE.png?width=960&height=242', 'https://media.discordapp.net/attachments/859153448309096458/865278564940906508/ROBLOX.png?width=960&height=242', 'https://media.discordapp.net/attachments/859153448309096458/865278560705052693/FILM.png?width=960&height=242']
