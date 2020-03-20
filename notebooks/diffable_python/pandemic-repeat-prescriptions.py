# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# In this notebook we are looking to see what proprotion of prescriptions are for one week, one month, two months and three months to inform our rapid evidence review on prescription duration during a pandemic.
#
# In order to do this we use the same methodology as the [OpenPrescribing Seven Day Prescribing aka dosette boxes measure](https://openprescribing.net/measure/seven_day_prescribing/national/england/) i.e. we select a basket of commonly prescribed medicines which are almost exclusively used once daily so we can ascertain the duration based on quantity.

##importing libraries that are need to support analysis
import pandas as pd
import numpy as np
from ebmdatalab import bq, maps, charts
import matplotlib.pyplot as plt
import os

# + active=""
# ## ensuring the format is consistent for floats,pounds and pence
# pd.set_option('display.float_format', lambda x: '%.2f' % x)

# +
## here we extract data for modelling
sql = '''
SELECT
  quantity_per_item,
  sum(items) as items
FROM
 ebmdatalab.hscic.raw_prescribing_normalised AS presc
INNER JOIN
  ebmdatalab.hscic.practices AS prac
ON
  presc.practice = prac.code
WHERE
(bnf_code LIKE "0205051R0%" OR  ##ramipril
bnf_code LIKE "0212000B0%" OR ##atrovastatin
bnf_code LIKE "0212000Y0%" OR ##simvastatin
bnf_code LIKE "0602010V0%" OR ##levothyroxine
bnf_code LIKE "0206020A0%") ##amlodipine
AND
(bnf_name LIKE '%tablet%' OR
bnf_name LIKE '% tab %' OR
bnf_name LIKE '% tab' OR
bnf_name LIKE '% tabs %' OR
bnf_name LIKE '% tabs' OR
bnf_name LIKE '%capsule%' OR
bnf_name LIKE '% caps %' OR
bnf_name LIKE '% caps' OR
bnf_name LIKE '%caplet%' OR
bnf_name LIKE '%Chewtab%') ##this restricts to tablets or capsules
AND
setting = 4
AND (month BETWEEN '2019-01-01'
    AND '2019-12-01') ##this restricts to one year 2019 
GROUP BY
  quantity_per_item
    '''

df_pandemic_repeatrx = bq.cached_read(sql, csv_path=os.path.join('..','data','pandemic_repeatrx.csv'))
df_pandemic_repeatrx.head(10)
# -

## here we get the total quantity on each prescription as a column
df_pandemic_repeatrx["total_quantity"] = df_pandemic_repeatrx["quantity_per_item"]*df_pandemic_repeatrx["items"] 


###here we make a list of common durations e.g. week, month etc
lst = [7,28,56,84]

# +
##lets have a look at the common durations
df_common = df_pandemic_repeatrx.loc[(df_pandemic_repeatrx["quantity_per_item"].isin(lst))]

print(df_common)
# -

## lets see what proprotions based on the volume of tabs/caps
total = df_pandemic_repeatrx["total_quantity"].sum()
df_common["proportion_of_qty"] = df_common["total_quantity"]/total*100
df_common

#  45% of the total volume appears on one month prescriptions.
