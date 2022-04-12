# In[1]:


import pandas as pd

# import data
dataset_url = 'https://epistat.sciensano.be/Data/COVID19BE.xlsx'
all_dfs = pd.read_excel(dataset_url, sheet_name=None)
# dataframe per sheet
cases = all_dfs['CASES_AGESEX']
vaccin = all_dfs['VACC']
hospital = all_dfs['HOSP']
mortality = all_dfs['MORT']


# # 1. Zevendaags gemiddelde aantal bevestigde besmettingen (sinds 1 maart 2020)

# In[2]:


cases_pivot = pd.pivot_table(cases, index = 'DATE', values = ['CASES'], aggfunc='sum')
cases_pivot['zevencalc'] = cases_pivot['CASES'].rolling(window=7).mean()
cases_pivot['zeven'] = cases_pivot['zevencalc'].round(decimals=0)
del cases_pivot['zevencalc']
zevendaags = cases_pivot.drop(cases_pivot.index[range(6)])
zevendaags.reset_index(level=0, inplace=True)
zevendaags['DATUM'] = zevendaags['DATE'].apply(lambda x: x.strftime('%d/%m/%Y'))
zevendaags.drop(zevendaags.tail(3).index,inplace=True)
zevendaags.to_csv('1_besmettingen_zevendaags.csv', index=False)


# # 2. Positiviteitsratio

# In[12]:


positiviteitsratio_url = 'https://epistat.sciensano.be/Data/COVID19BE_tests.csv'
positiviteitsratio_df = pd.read_csv(positiviteitsratio_url)
positiviteitsratio = positiviteitsratio_df.pivot_table(index = 'DATE', values = ['TESTS_ALL', 'TESTS_ALL_POS'], aggfunc = 'sum').reset_index()
positiviteitsratio['positiviteitsratio'] = positiviteitsratio['TESTS_ALL_POS'] / positiviteitsratio['TESTS_ALL']*100
positiviteitsratio['Negatieve testresultaten'] = positiviteitsratio['TESTS_ALL'] - positiviteitsratio['TESTS_ALL_POS']
positiviteitsratio = positiviteitsratio.rename(columns = {'TESTS_ALL_POS': 'Positieve testresultaten'}, inplace = False)
positiviteitsratio.to_csv('2_positiviteitsratio.csv')


# # 3.  Hospitalisaties

# In[13]:


hospital_pivot = pd.pivot_table(hospital, index = 'DATE', values = ['TOTAL_IN', 'NEW_IN'], aggfunc='sum')
hospital_pivot = hospital_pivot.rename(columns = {'TOTAL_IN': 'Totaal aantal covid-patiënten in het ziekenhuis', 'NEW_IN': 'Opnames voor deze dag'}, inplace = False)
hospital_pivot.to_csv('3_hospitalisaties.csv', index=True)


# # 4. ICU

# In[31]:


icu_pivot = pd.pivot_table(hospital, index = 'DATE', values = ['TOTAL_IN_ICU'], aggfunc='sum').reset_index()
icu_pivot = icu_pivot.rename(columns = {'TOTAL_IN_ICU': 'Totaal aantal patiënten in ICU'}, inplace = False)
icu_pivot.to_csv('4_total_icu.csv', index=True)


# # 5. Overlijdens

# In[36]:


mortality_pivot = pd.pivot_table(mortality, index = 'DATE', values = 'DEATHS', aggfunc='sum')
mortality_pivot.drop(mortality_pivot.tail(1).index,inplace=True)
mortality_pivot = mortality_pivot.rename(columns = {'DEATHS': 'Aantal Covid-overlijdens'}, inplace = False)
mortality_pivot['Aantal Covid-overlijdens opgeteld'] = mortality_pivot['Aantal Covid-overlijdens'].cumsum()
mortality_pivot.to_csv('5_overlijdens.csv', index=True)


# # 6. Vaccinatiedekking volwassenen

# In[16]:


population_total = 11521238.0
population_minors = 2312122.0
population_adult = population_total - population_minors
vaccinatiedekking_pivot = pd.pivot_table(vaccin, index = 'DOSE', columns = 'AGEGROUP', values = 'COUNT', aggfunc='sum')
vaccinatiedekking_pivot['+18'] = vaccinatiedekking_pivot['18-24'] + vaccinatiedekking_pivot['25-34'] + vaccinatiedekking_pivot['35-44'] +vaccinatiedekking_pivot['45-54'] + vaccinatiedekking_pivot['55-64'] + vaccinatiedekking_pivot['65-74'] + vaccinatiedekking_pivot['75-84'] + vaccinatiedekking_pivot['85+']
vaccinatiedekking_pivot.drop(['00-04', '05-11', '12-15', '16-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75-84', '85+'], axis=1, inplace=True)
vaccinatiedekking_pivot = vaccinatiedekking_pivot.transpose()
vaccinatiedekking_pivot['Eerste dosis abs'] = vaccinatiedekking_pivot['A'] + vaccinatiedekking_pivot['C']
vaccinatiedekking_pivot['Volledig gevaccineerd abs'] = vaccinatiedekking_pivot['B'] + vaccinatiedekking_pivot['C']
vaccinatiedekking_pivot['Extra dosis'] = vaccinatiedekking_pivot['E']
vaccinatiedekking_pivot['Rest van de bevolking abs'] = population_adult - vaccinatiedekking_pivot['A'] - vaccinatiedekking_pivot['C']
vaccinatiedekking_pivot['18+ met minstens eerste dosis'] = vaccinatiedekking_pivot['Eerste dosis abs'] / population_adult * 100
vaccinatiedekking_pivot['18+ volledig gevaccineerd'] = vaccinatiedekking_pivot['Volledig gevaccineerd abs'] / population_adult * 100
vaccinatiedekking_pivot['18+ met boosterprik'] = vaccinatiedekking_pivot['Extra dosis'] /population_adult * 100
vaccinatiedekking_pivot['18+ die nog geen prik kreeg'] = vaccinatiedekking_pivot['Rest van de bevolking abs'] / population_adult * 100
vaccinatiedekking_pivot['18+ met 2de boosterprik'] = vaccinatiedekking_pivot['E2'] /population_adult * 100
vaccinatiedekking_pivot['18+ die nog geen prik kreeg'] = vaccinatiedekking_pivot['Rest van de bevolking abs'] / population_adult * 100
vaccinatiedekking_pivot.drop(['A', 'B', 'C', 'E', 'E2', 'Eerste dosis abs', 'Volledig gevaccineerd abs', 'Rest van de bevolking abs', 'Extra dosis'], axis=1, inplace=True)
vaccinatiedekking_pivot = vaccinatiedekking_pivot.transpose()
vaccinatiedekking_pivot.to_csv('6_vaccinatiedekking_volwassenen.csv', index=True)


# # 7. Vaccinatiedekking totale bevolking

# In[27]:


population_total = 11521238.0
population_minors = 2312122.0
population_adult = population_total - population_minors
vaccinatiedekking_total = pd.pivot_table(vaccin, columns = 'DOSE', values = 'COUNT', aggfunc='sum')
vaccinatiedekking_total['Eerste dosis'] = (vaccinatiedekking_total['A'] + vaccinatiedekking_total['C']) / population_total * 100
vaccinatiedekking_total['Volledig gevaccineerd'] = (vaccinatiedekking_total['B'] + vaccinatiedekking_total['C']) / population_total * 100
vaccinatiedekking_total['Boosterprik'] = vaccinatiedekking_total['E']  / population_total * 100
vaccinatiedekking_total['2de boosterprik'] = vaccinatiedekking_total['E2']  / population_total * 100
vaccinatiedekking_total['Ongevaccineerd'] = (population_total - vaccinatiedekking_total['A'] - vaccinatiedekking_total['C']) / population_total * 100
vaccinatiedekking_total.drop(['A', 'B', 'C', 'E', 'E2'], axis=1, inplace=True)
vaccinatiedekking_total = vaccinatiedekking_total.transpose()
vaccinatiedekking_total.to_csv('7_vaccinatiedekking_totale_bevolking.csv', index=True)


# # 8. Vaccinatiedekking per regio

# In[26]:


duitstalig_volwassen = 63036.0
vlaams_volwassen = 5363075.0
brussels_volwassen = 944417.0
waals_volwassen = 2901624.0 - duitstalig_volwassen
vaccinvolwassen = vaccin.drop(vaccin[vaccin.AGEGROUP.isin(["00-04", "05-11", "12-15", "16-17", "12-15", "16-17"])].index)
vaccinvolwassen = pd.pivot_table(vaccinvolwassen, index = 'REGION', columns = 'DOSE', values = 'COUNT', aggfunc='sum')
vaccinvolwassen['volwassen'] = [brussels_volwassen, vlaams_volwassen, duitstalig_volwassen, waals_volwassen]
vaccinvolwassen['Minstens één dosis'] = (vaccinvolwassen['A'] + vaccinvolwassen['C']) / vaccinvolwassen['volwassen'] * 100
vaccinvolwassen['Volledig gevaccineerd'] = (vaccinvolwassen['B'] + vaccinvolwassen['C']) / vaccinvolwassen['volwassen'] * 100
vaccinvolwassen['Boosterprik'] = vaccinvolwassen['E'] / vaccinvolwassen['volwassen'] * 100
vaccinvolwassen['Regio'] = ['Brussel', 'Vlaanderen', 'Duitstalige gebieden', 'Wallonië']
vaccinvolwassen = vaccinvolwassen[['Regio', 'Minstens één dosis', 'Volledig gevaccineerd', 'Boosterprik']]
vaccinvolwassen.to_csv('8_vax_per_regio.csv', index=True)

# # 8. Vaccins cumulatief

vaccin_pivot = pd.pivot_table(vaccin, index = 'DATE', columns = 'DOSE', values = 'COUNT', aggfunc='sum')
vaccin_pivot = vaccin_pivot.fillna(0)
vaccin_pivot['A_cum'] = vaccin_pivot['A'].cumsum()
vaccin_pivot['B_cum'] = vaccin_pivot['B'].cumsum()
vaccin_pivot['C_cum'] = vaccin_pivot['C'].cumsum()
vaccin_pivot['E_cum'] = vaccin_pivot['E'].cumsum()
vaccin_pivot['Totaal aantal mensen volledig gevaccineerd (opgeteld)'] = vaccin_pivot['B_cum'] + vaccin_pivot['C_cum']
vaccin_pivot['Totaal aantal mensen met minstens één dosis (opgeteld)'] = vaccin_pivot['A_cum'] + vaccin_pivot['C_cum']
vaccin_pivot['Totaal aantal mensen met een boosterprik (opgeteld)'] = vaccin_pivot['E_cum']
vaccin_pivot.drop(['A', 'B', 'C', 'E', 'A_cum', 'B_cum', 'C_cum', 'E_cum'], axis=1, inplace=True)
vaccin_pivot.to_csv('9_vaccin_opgeteld.csv', index=True)
