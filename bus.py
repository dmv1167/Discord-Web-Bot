import discord
import passiogo
from utils import refresh
from datetime import datetime, time

BASE = 'https://www.rit.edu'
BUS = f'{BASE}/parking/campus-shuttles'

def bus_alert() -> discord.Embed:
    system = passiogo.getSystemFromID(4006)
    alerts = [alert.__dict__ for alert in system.getSystemAlerts()]
    busses = f'{BASE}/parking/campus-shuttles'
    announce_list = ''
    for alert in alerts:
        announce_list += f'* **{alert["gtfsAlertHeaderText"]}**\n{alert["gtfsAlertDescriptionText"]}\n'

    bus_embed = discord.Embed(title="Campus Shuttle Announcements",
                              url=busses,
                              description=announce_list,
                              color=0xFF6900)
    bus_embed.set_author(name="RIT Busses",
                         icon_url='https://pbs.twimg.com/profile_images/1105451876689068033/eZFMq8pb_400x400.png')
    bus_embed.set_footer(text=datetime.now().strftime('%B %d, %Y | %I:%M:%S %p'))

    return bus_embed


def bus_info(num: int) -> discord.Embed:
    bus_content = refresh(BUS)
    bus_url = BUS
    system = passiogo.getSystemFromID(4006)

    schedules = bus_content.find('div', {'class': 'view-grouping-content'}).find_all('a')
    description = ''
    if int(num) == 0:
        color = 0xFF6900
        title = 'Bus Schedules'
        sched_links = [f'* [{schedule.text}]({BASE + schedule["href"]})' for schedule in schedules]
        for sched in sched_links:
            description = description + f'{sched}\n'
    else:
        title = schedules[int(num) - 1].text
        route = [route.__dict__ for route in system.getRoutes() if route.__dict__["name"] in title]
        if len(route) == 1:
            route = route[0]
        bus = [vehicle.__dict__ for vehicle in system.getVehicles() if vehicle.__dict__["routeName"] == route["name"]]
        if len(bus) == 1:
            bus = bus[0]
        color = int(f'{route["groupColor"][1:]}', 16)
        route_url = BASE + schedules[int(num) - 1]['href']
        route_content = refresh(route_url)
        table = route_content.find('table', {'class': 'table-striped'})
        stops = {}
        for header in table.find('thead').find_all('th'):
            if header not in stops:
                stops[header.text] = []
        found = False
        for row in table.find('tbody').find_all('tr'):
            if found:
                break
            for index, arrival in enumerate(row.find_all('td')):
                if found:
                    break
                if arrival is not None:
                    stop_time = datetime.strptime(arrival.text.upper(), '%I:%M %p').time()
                    stop = list(stops.keys())[index]
                    if datetime.now().time() < stop_time:
                        description = f'Next stop: **{stop}** at **{stop_time.strftime("%I:%M %p")}**'
                        found = True
                    stops[stop].append(arrival.text)
        if not found:
            description = 'This line has no further stops today'
        bus_url = route_url
        title = schedules[int(num) - 1].text


    embed = discord.Embed(title=title,
                            url=bus_url,
                            description=description,
                            color=color)
    embed.set_author(name="RIT Busses",
                     icon_url='https://pbs.twimg.com/profile_images/1123208686875414528/ecELpGo__400x400.png')
    embed.set_footer(text=datetime.now().strftime('%B %d, %Y | %I:%M:%S %p'))

    return embed