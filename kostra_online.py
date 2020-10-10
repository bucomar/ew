""" NiderschlagSpendenDaten von KOSTRA """

## import modules

# from zipfile import ZipFile as zp
import requests, zipfile, io
import pandas as pd

##	make index_rc

# COORD_B = 53.5928618
# COORD_L = 9.4709494

############################################
### KOSTRA Koordinaten hier schreiben!!! ###
############################################
# COL = 68 ###################################
# ROW = 20 ###################################
############################################

############################################

# I_RC = int(str(COL) + '0' + str(ROW))
# print ('col: ', COL, '\n', 'row: ', ROW, '\n', 'index_rc: ', I_RC)





############################################
### GEO Koordinaten hier schreiben!!! ######
############################################
x = 9.6755 # geog. Breite °N ###############
y = 53.4646 # geog. Länge °O ###############
############################################

print('Kostra Daten einlesen.')

URL_COORD = 'https://opendata.dwd.de/climate_environment/CDC/grids_germany/return_periods/precipitation/KOSTRA/KOSTRA_DWD_2010R/asc/KOSTRA-DWD-2010R_geog_Bezug.xlsx'

SHEET = 'Raster_geog_Bezug'

df = pd.read_excel(URL_COORD, sheet_name = SHEET)

i_rc_row = df[ (df['X1_NW_GEO'] <= x) & (df['X4_NE_GEO'] >= x) & (df['Y1_NW_GEO'] >= y) & (df['Y2_SW_GEO'] <= y)]

i_rc_row

I_RC = i_rc_row.iloc[0, 0]

I_RC
type(I_RC)

print('Benötigte Daten samelln.')

##	url list
REGEN_DAUER = [
'0005', '0010', '0015', '0020', '0030', '0045', '0060', '0090', '0120', '0180', '0240', '0360', '0540', '0720', '1080', '1440', '2880', '4320'
]

URL = []

for i in range(len(REGEN_DAUER)):
	URL.append(
	'https://opendata.dwd.de/climate_environment/CDC/grids_germany/return_periods/precipitation/KOSTRA/KOSTRA_DWD_2010R/asc/StatRR_KOSTRA-DWD-2010R_D'
	+REGEN_DAUER[i]
	+'.csv.zip'
	)

## Functionen

def csv_name(nro):
	""" csv name generator """
	csv_nm = str(
	'StatRR_KOSTRA-DWD-2010R_D'+str(nro)+'.csv')
	return csv_nm

def df_name(nro):
	""" df name generator """
	df_nm = str('df'+str(nro)+'.csv')
	return df_nm

def get_csv_df(pos):
	""" get csv-s to df """
	print(pos)
	r = requests.get(URL[pos])
	z = zipfile.ZipFile(io.BytesIO(r.content))
	csv = z.open(csv_name(REGEN_DAUER[pos]))
	df = pd.read_csv(csv, sep = ';', index_col=('INDEX_RC'))
	return df

def df_row_exp(from_df, rc_i, to_df, pos):
	""" ##	row export to INDEX_RC """
	# to_df = pd.concat([to_df, from_df.loc[from_df['INDEX_RC'] == int(rc_index)]])
	a_row = from_df.loc[[rc_i]]
	a_row = a_row.apply(lambda i: round(i*100*100/60/int(REGEN_DAUER[pos]), 2))
	# print(a_row)
	# print()
	to_df = pd.concat([to_df, a_row])
	# print(to_df)
	# print()
	return to_df

##	make local_RS

LOCAL_RS = pd.DataFrame()

for i in range(0, len(REGEN_DAUER)):
	DF_TEMP = get_csv_df(i)
	LOCAL_RS = df_row_exp(DF_TEMP, I_RC, LOCAL_RS, i)

LOCAL_RS.index = REGEN_DAUER
LOCAL_RS.index.name = 'Regendauer'
LOCAL_RS.columns.name = 'Regenhaufigkeit'

print(LOCAL_RS)

LOCAL_RS_FILE_NAME = str('kostra_' + str(I_RC) + '_l.csv')
LOCAL_RS.to_csv(LOCAL_RS_FILE_NAME, sep='\t', decimal=',')

print(LOCAL_RS_FILE_NAME + ' ist fertig!')
