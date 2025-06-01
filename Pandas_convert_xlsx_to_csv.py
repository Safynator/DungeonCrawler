import pandas as pd
import os
df = pd.read_excel(os.path.join("levels", "level2_data.xlsx"))
df.to_csv("level2_data(2)", sep=",")
