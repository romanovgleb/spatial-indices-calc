'''
Calculating PTAL score for a regular grid.
Script takes in spatial join one-to-many csv, where we have grid cell id,
route id (for each route we've previously built an isochrone) and travel time
(how long it takes to get to that grid cell from the route's stop), and then
calculates PTAL score for each grid.

I wrote it way back when I didn't know any style guides, but I'm still
hopeful it'll be useful to someone.

For more info on PTAL, check out
https://en.wikipedia.org/wiki/Public_transport_accessibility_level
'''

import csv
import pandas as pd
import datetime

print('start time:', datetime.datetime.now(), '\n')

route_df = pd.read_excel('all_routes_info.xlsx')
hex_dict = {}

i = 1 # counting csv rows
print('reading through the file - creating dict...')
# iterate through all the joined rows and create
# a dict for each cell with minimum walking time
# (for each route within that cell!)
with open('mockup_joined - Copy.csv', 'r') as fin:
    for row in csv.DictReader(fin, delimiter=';'):
        if i % 100000 == 0:
            print('row #'+str(i))
        i += 1
        iterable_hex_cell = int(row['id'])
        if int(row['id']) not in hex_dict: # if hex cell id not in hex dict - add it
                 hex_dict[iterable_hex_cell] = {}
        else:
            pass
        df_large_mode = str(route_df.loc[route_df['rowid'] == int(row['route_id'])]['mode_large'].item())
        if df_large_mode not in hex_dict[iterable_hex_cell]:
            # if mode not in cell dictionary - add it
            hex_dict[iterable_hex_cell][df_large_mode] = {}
        else:
            pass
        if int(row['route_id']) not in hex_dict[iterable_hex_cell][df_large_mode]:
            # if route is not in mode dict - add it (as a dictionary)
            hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])] = {}
            if 'WAT' not in hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])]:
                # if WAT is not yet in a route dictionary - add it!
                hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])]['WAT'] = int(row['traveltime'])
            else: # if WAT is already in dictionary - compare the times and leave the smallest
                if hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])]['WAT'] > int(row['traveltime']):
                    hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])]['WAT'] = int(row['traveltime'])
                else:
                    pass
        else:
            if 'WAT' not in hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])]:
                # if WAT is not yet in a route dictionary - add it!
                hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])]['WAT'] = int(row['traveltime'])
            else: # if WAT is already in dictionary - compare the times and leave the smallest
                if hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])]['WAT'] > int(row['traveltime']):
                    hex_dict[iterable_hex_cell][df_large_mode][int(row['route_id'])]['WAT'] = int(row['traveltime'])
                else:
                    pass

print(f'{i} rows in total.'+'\n')

# go through each route within each cell and calculate: WAT, TAT, EDF, PTAI
# for each item in dict calculate final PTAL based on PTAI of routes
print('calculating WAT, TAT, EDF, PTAI, PTAL, writing PTAL to csv...')

r = 1
with open('result_ptal.csv', 'w') as fout:
    writer = csv.DictWriter(fout, delimiter=';',
                            fieldnames=['hex_id', 'PTAL'], lineterminator='\n')
    writer.writeheader()
    for cell in hex_dict:
        if r % 10000 == 0:
            print('cell #' + str(r))
            r += 1
        ptai_list = [] # creating a list for accumulation of all the AIs for all modes
        for mode in hex_dict[cell]:
            edf_list = [] # a list for accumulation of EDF's for each route
            for route in hex_dict[cell][mode]:
                if mode == 'ngpt':
                    hex_dict[cell][mode][route]['TAT'] = float(hex_dict[cell][mode][route]['WAT']
                                                               + (float(route_df.loc[route_df['rowid'] == route]['interval'].item()/2)) + 0.75)
                elif mode == 'svt':
                    hex_dict[cell][mode][route]['TAT'] = float(hex_dict[cell][mode][route]['WAT']
                                                               + (float(route_df.loc[route_df['rowid'] == route]['interval'].item()/2)) + 0.75)
                hex_dict[cell][mode][route]['EDF'] = float(30/hex_dict[cell][mode][route]['TAT'])
                edf_list.append(hex_dict[cell][mode][route]['EDF'])
            edf_max = edf_list.pop(edf_list.index(max(edf_list)))
            hex_dict[cell][mode]['PTAI'] = edf_max + (sum(edf_list) * 0.5)
            ptai_list.append(hex_dict[cell][mode]['PTAI'])
        hex_dict[cell]['PTAL'] = sum(ptai_list)
        writer.writerow({'hex_id': cell, 'PTAL': hex_dict[cell]['PTAL']})

print(f'{r} cells written in total' + '\n')
print('end time:', datetime.datetime.now())
