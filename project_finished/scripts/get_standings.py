import requests
import re
import os
import csv

ft_url = 'https://www.nfl.com/standings/league/2017/REG'
ft_directory = 'project_prog1'
page_filename = 'standings_RS.html'
csv_filename = 'standings_RS.csv'

def url_to_string(url):    
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('failed to download')
        return 
    return r.text 


def string_to_file(text, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None

##########################################################################

def save_frontpage():
    data_string = url_to_string(ft_url) 
    if data_string is None:
        print('the url download failed')
    else:
        string_to_file(data_string, ft_directory, page_filename)
        return None 

############################################################################

def file_to_string(directory, filename):
    path = os.path.join(directory, filename)
    with open(path, 'r', encoding='utf-8') as file_in:
        return file_in.read()


def extract_team_blocks(page):

    team_blocks = []
    regex =  re.compile(
        r'\{"conference"(.+?)"clinchWc":(true|false)\}',
        re.DOTALL)
    for match in re.findall(regex, page):
        team_blocks.append(str(match))
    
    return team_blocks

##############################################################################

def info_dictionary(block):
    
    regex = re.compile(
        r'.+"fullName":"(?P<Team>[\w\. ]+)"'
        r'.+"overallWin":(?P<Wins>\d+),"overallLoss":(?P<Losses>\d+),'
        r'"overallTie":(?P<Ties>\d+),'
        r'"overallPct":(?P<Percent>[\.\d]+),'
        r'"overallPtsFor":(?P<Points_Scored>\d+),'
        r'"overallPtsAgainst":(?P<Points_allowed>\d+),'
        r'"homeWin":(?P<Home_Wins>\d+),"homeLoss":(?P<Home_Losses>\d+),'
        r'"homeTie":(?P<Home_Ties>\d+).+'
        r'"roadWin":(?P<Road_Wins>\d+),"roadLoss":(?P<Road_Losses>\d+),'
        r'"roadTie":(?P<Road_Ties>\d+).+'
        r'"conferenceWin":(?P<Conference_Wins>\d+),'
        r'"conferenceLoss":(?P<Conference_Losses>\d+),'
        r'"conferenceTie":(?P<Conference_Ties>\d+).+,'
        r'"last5Win":(?P<Final_Streak>\d+).+',
        re.DOTALL
    )
    data = re.search(regex, block)
    info_dict = data.groupdict()
    
    return info_dict

#########################################################################

def statlines(directory, filename):
    content = file_to_string(directory, filename)
    team_blocks = extract_team_blocks(content)
    list_of_dicts = [info_dictionary(block) for block in team_blocks]
    return list_of_dicts

def frontpage_statlines():
    return statlines(ft_directory, page_filename)
    
##########################################################################

def write_csv(fieldnames, rows, directory, filename):

    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return None


def write_NFL_stats_to_csv(list_of_dicts, directory, filename):
    write_csv(list_of_dicts[0].keys(), list_of_dicts, directory, filename)


def write_NFL_csv(list_of_dicts):
    write_NFL_stats_to_csv(list_of_dicts, ft_directory, csv_filename)

###########################################################################



