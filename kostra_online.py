""" NiderschlagSpendenDaten von KOSTRA """

## import modules

# from zipfile import ZipFile as zp
import requests, zipfile, io
import pandas as pd
import streamlit as st

import base64
from io import BytesIO

'''
# Niederschlagsspenden von KOSTRA - DWD 2010  
  
####  Quelle: Deutscher Wetterdienst  
  
KOSTRA-DWD - Rasterdaten zu Niederschlagsspenden in Abhängigkeit von der Niederschlagsdauer D und der Jährlichkeit T (Wiederkehrintervall).

'''



URL_COORD = 'https://opendata.dwd.de/climate_environment/CDC/grids_germany/return_periods/precipitation/KOSTRA/KOSTRA_DWD_2010R/asc/KOSTRA-DWD-2010R_geog_Bezug.xlsx'

SHEET = 'Raster_geog_Bezug'

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

# @st.cache
def csv_name(nro):
	""" csv name generator """
	csv_nm = str(
	'StatRR_KOSTRA-DWD-2010R_D'+str(nro)+'.csv')
	return csv_nm

# @st.cache
def df_name(nro):
	""" df name generator """
	df_nm = str('df'+str(nro)+'.csv')
	return df_nm

# @st.cache(suppress_st_warning=True)
def get_csv_df(pos):
	""" get csv-s to df """
	st.write(pos)
	r = requests.get(URL[pos])
	z = zipfile.ZipFile(io.BytesIO(r.content))
	csv = z.open(csv_name(REGEN_DAUER[pos]))
	df = pd.read_csv(csv, sep = ';', index_col=('INDEX_RC'))
	return df

# @st.cache
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


## Prozess

# Coordinaten einbitten

x = st.text_input('geog. Breite °N', value='9.955283')
y = st.text_input('geog. Länge °O', value='53.545022')

if st.button('OK'):
	x = float(x)
	y = float(y)
	st.write('Kostra Daten einlesen.')
	
	# KOSTRA Raster einlesen zu df
	df = pd.read_excel(URL_COORD, sheet_name = SHEET)
	
	# 1 row filtern
	i_rc_row = df[ ((df['X1_NW_GEO']) <= x) & (df['X4_NE_GEO'] >= x) & (df['Y1_NW_GEO'] >= y) & (df['Y2_SW_GEO'] <= y)]
	# st.dataframe(i_rc_row)
	I_RC = i_rc_row.iloc[0, 0]
	st.write('Index-RC: ' + str(I_RC))
	
	st.write('Benötigte Daten samelln.')
	
	##	make local_RS
	
	LOCAL_RS = pd.DataFrame()
	
	for i in range(0, len(REGEN_DAUER)):
		DF_TEMP = get_csv_df(i)
		# st.write(i)
		LOCAL_RS = df_row_exp(DF_TEMP, I_RC, LOCAL_RS, i)

	LOCAL_RS.index = REGEN_DAUER
	LOCAL_RS.index.name = 'Regendauer'
	LOCAL_RS.columns.name = 'Regenhaufigkeit'
	
	st.dataframe(LOCAL_RS)
	
	# LOCAL_RS_FILE_NAME = str('kostra_' + str(I_RC) + '_l.csv')
	# LOCAL_RS.to_csv(LOCAL_RS_FILE_NAME, sep='\t', decimal=',')

	# st.write(LOCAL_RS_FILE_NAME + ' ist fertig!')
	
	# if st.button('LOCAL_RS_FILE_NAME runterladen'):
	# 	st.markdown(get_table_download_link(LOCAL_RS), unsafe_allow_html=True)
