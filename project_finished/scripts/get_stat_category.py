import requests
import re
import os
import csv

ft_url = 'http://www.nfl.com/stats/categorystats?archive=true&conference=null&statisticCategory=RUSHING&season=2017&seasonType=REG&experience=&tabSeq=0&qualified=false&Submit=Go'
ft_directory = 'project_prog1'
page_filename = 'rushing_RS.html'
csv_filename = 'rushing_RS.csv'

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

###########################################################################

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


def extract_player_blocks(page):
    player_blocks = []
    corrected = []
    regex =  re.compile(r'<tr class="(odd|even)">(.+?)</td></tr>', re.DOTALL)
    for match in re.findall(regex, page):
        player_blocks.append(str(match))
    for block in player_blocks: 
        corrected.append(re.sub('--', '0', block))
    return corrected

##############################################################################

def list_of_player_stats(block):

    stats = []
    corrected = []
    floated = []
    regex = r'\bt([\d,\.T]+)\b'  
    for match in re.finditer(regex, block):
        stats.append(match.group(1))
    for stat in stats:
        corrected.append(re.sub('T', '', stat))
    for correction in corrected: 
        floated.append(float(re.sub(',', '', correction)))

    return floated 
    

def basic_info_dictionary(block):
    
    regex = re.compile(
        r'<td>(?P<rank>\d{1,2}).+\/'
        r'players.+\d">(?P<name>[\w\. ]+).+team'
        r'=(?P<team>[A-Z]+)">.+<td>'
        r'(?P<position>[A-Z]+)<\/td>',
        re.DOTALL
    )
    data = re.search(regex, block)
    info_dict = data.groupdict()
    
    return info_dict


def fill_dictionary(block):

    i_dict = basic_info_dictionary(block)
    s_list = list_of_player_stats(block)
    
    i_dict['Attempts'] = int(s_list[0])
    i_dict['Yards'] = int(s_list[2])
    i_dict['Touchdowns'] = int(s_list[5])
    i_dict['Long'] = int(s_list[6])
    i_dict['20+'] = int(s_list[9])
    i_dict['40+'] = int(s_list[10])
    i_dict['Fumbles'] = s_list[11]
    
    return i_dict

#########################################################################

def statlines(directory, filename):
    content = file_to_string(directory, filename)
    player_blocks = extract_player_blocks(content)
    list_of_dicts = [fill_dictionary(block) for block in player_blocks]
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

#############################################################################

def generate():
    save_frontpage()
    dict_list = frontpage_statlines()
    write_NFL_csv(dict_list)

###########################################################################