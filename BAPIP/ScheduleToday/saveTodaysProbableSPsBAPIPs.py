import statsapi
import pandas as pd
from datetime import datetime as dt
import dataframe_image as dfi

def getPlayerID(fullName: str, szn: int = 2025):
    players = statsapi.get('sports_players',{'season': szn})['people']
    return(
        next(
            p['id'] for p in players if p['fullName'] == fullName
        )
    )

def calcBAPIP(pid: int, szn: int = 2025):
    info = statsapi.plauer_stat_data(pid, group="[pitching]", type="season", sportId=1, season=szn)
    name = info['first_name']+ ' ' + info['last_name']

    pstats = info['stats'][0]['stats']
    total_bases_allowed = pstats['totalBases'] + pstats['baseOnBalls'] + pstats['hitByPitch']
    er = pstats['earnedRuns']
    ip = pstats['outs'] / 3
    games = pstats['gamesPlayed']
    starts = pstats['gamesStarted']

    return {"Player": name, 
            "Games": games, 
            "Starts": starts, 
            "Total IP": round(ip, 3), 
            "BAPIP": round(total_bases_allowed/ip,3),
            "ERPIP": round(er/ip,3)}

def getTodayProbableStarters():
    today_schedule = statsapi.schedule(dt.today().strftime('%Y-%m-%d'))
    slate = pd.DataFrame({"Matchup": [],
                            "Away SP": [],
                            "Away SP Total IP": [],
                            "Away SP BApIP": [],
                            "Away SP ERpIP": [],
                            "Home SP": [],
                            "Home SP Total IP": [],
                            "Home SP BApIP": [],
                            "Home SP ERpIP": []})
    
    for game in today_schedule:
        if game['doubleheader'] == 'N':
            matchup = f"{game['away_name']} vs {game['home_name']}"
        else:
            matchup = f"{game['away_name']} vs {game['home_name']}, Game {game['game_num']}"
        
        away_sp = game['away_probable_pitcher']
        home_sp = game['home_probable_pitcher']

        try:
            away_sp_stats = calcBAPIP(getPlayerID(away_sp))
        except:
            away_sp_stats = {"Player": None,
                             "Games": None,
                             "Starts": None,
                             "Total IP": None,
                             "BApIP": None,
                             "ERpIP": None}
                
        try:
            home_sp_stats = calcBAPIP(getPlayerID(home_sp))
        except:
            home_sp_stats = {"Player": None,
                             "Games": None,
                             "Starts": None,
                             "Total IP": None,
                             "BApIP": None,
                             "ERpIP": None}
    
        game_matchup = {"Matchup": matchup,
                            "Away SP": away_sp,
                            "Away SP Total IP": away_sp_stats['Total IP'],
                            "Away SP BApIP": away_sp_stats['BApIP'],
                            "Away SP ERpIP": away_sp_stats['ERpIP'],
                            "Home SP": home_sp,
                            "Home SP Total IP": home_sp_stats['Total IP'],
                            "Home SP BApIP": home_sp_stats['BApIP'],
                            "Home SP ERpIP": home_sp_stats['ERpIP']}
        
        slate = pd.concat([slate, pd.DataFrame([game_matchup])], ignore_index = True)
        
    return slate

def outputSlate(dfrm):
    try:
        max = max(list(dfrm['Away SP BApIP'])+list(dfrm['Home SP BApIP']))
        min = min(list(dfrm['Away SP BApIP'])+list(dfrm['Home SP BApIP']))
    except:
        max = 2.5
        min = 1.5
    #df_styled = df.style.background_gradient() #adding a gradient based on values in cell
    dfi.export(dfrm.style.background_gradient(cmaps='Greens',high=max,low=min,subset=['Away SP BApIP','Home SP BApIP']).applymap(lambda x: 'color: black; background-color: transparent' if pd.isnull(x) else ''),'today_schedule.png')

# execute
print('executing')
outputSlate(getTodayProbableStarters())
print('output expected...')
