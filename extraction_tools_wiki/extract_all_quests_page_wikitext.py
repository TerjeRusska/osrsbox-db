# !/usr/bin/python

"""
Author:  PH01L
Email:   phoil@osrsbox.com
Website: osrsbox.com
Date:    2018/01/10

Description:
Extract all wikitext from all quest pages. The required input is the 
"extract_all_quests.txt" file from the "extract_all_quests.py" script. 
This script will extract all wikitext to "extract_all_quests_page_wikitext"
directory for later processing.

Copyright (c) 2018, PH01L

###############################################################################
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

>>> CHANGELOG:
    1.0.0       Base functionality
"""

__version__ = "1.1.0"

custom_agent = {
    'User-Agent': 'some-agent',
    'From': 'name@domain.com' 
}

import os
import sys
import json
import glob
import random
import string
import requests
import mwparserfromhell

def extract_wikitext(page_name):
    norm_page_name = page_name.replace("&", "%26")
    norm_page_name = norm_page_name.replace("+", "%2B")
    # Example: http://oldschoolrunescape.wikia.com/api.php?action=parse&prop=wikitext&format=json&page=3rd_age_pickaxe
    url = "https://oldschool.runescape.wiki/api.php?action=parse&prop=wikitext&format=json&page=" + norm_page_name
    result = requests.get(url, headers=custom_agent)
    data = result.json()

    try:
        # Extract the actual content
        input = data["parse"]["wikitext"]["*"].encode("utf-8")
    except KeyError:
        # Or return if cannot extract wikitext from page
        return

    # Parse actual wikitext content using mwparserfromhell
    wikitext = mwparserfromhell.parse(input)

    # Convert to JSON 
    quest_dict = dict()
    quest_dict[page_name] = str(wikitext)

    out_fi_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(64))
    
    out_fi = "extract_all_quests_page_wikitext" + os.sep + out_fi_name + ".json"
    with open(out_fi, "w") as f:
        json.dump(quest_dict, f)  

################################################################################
if __name__=="__main__":   
    # Start processing: extract_all_quests.txt
    print(">>> Starting to extract wikitext for all quest...")
    
    print("  > Reading extract_all_quests page titles...")
    quests_to_process = list()
    with open("extract_all_quests.txt") as f:
        for l in f:
            l = l.strip()
            quests_to_process.append(l)

    directory = "extract_all_quests_page_wikitext"

    # Determine previously extracted page_titles
    print("  > Determining already extracted page titles...")
    processed_fis_path = directory + os.sep + "*"
    processed_fis = glob.glob(processed_fis_path)
    quests_already_processed = list()
    # Strip path from files
    for fi in processed_fis:
        with open(fi) as f:
            data = json.load(f)
            quest_name = next(iter(data))
            quests_already_processed.append(quest_name)

    if not os.path.exists(directory):
        os.makedirs(directory)

    print("  > Starting wikitext extraction...")
    quests_count = len(quests_to_process)
    count = 0
    for quest_page_title in quests_to_process:
        sys.stdout.write(">>> Processing: %d out of %d\r" % (count, quests_count))
        if quest_page_title in quests_already_processed:
            # Skip if already processed
            count += 1
            continue
        # Extract wikitext
        extract_wikitext(quest_page_title)
        count += 1    
