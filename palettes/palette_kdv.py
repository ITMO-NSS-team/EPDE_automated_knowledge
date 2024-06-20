import matplotlib.colors
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from drawbase.read_compile_df_tuned import _round_values, read_csv, _round_if_many

import os
from pathlib import Path
sns.set(style="whitegrid", color_codes=True)


path = 'data_kdv/'
path = str(os.path.join(Path().absolute().parent, path))
names = ["0", "0.023", "0.046", "0.069", "0.092"]
n_df = 3
decimals = 4

df_ls = read_csv(path, names, n_df)
categories, df_lsr = _round_values(df_ls, decimals=decimals)


categories = categories[np.argsort(categories)]
categories = categories[:len(categories)-1]
# categories_trimmed = _round_if_many(categories)

categories_string = [str(el) for el in categories]
core_values = [1e-05, 5e-05, 0.0001, 0.0009, 1.4e-03]
core_colors = ["#385623", "#538135", "#669D41", "#89BF65", "#C5E0B3"]

categories_log = np.log(categories)
core_values_log = np.log(core_values)
norm=plt.Normalize(min(categories),max(categories))
tuples = list(zip(map(norm,core_values), core_colors))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", tuples)

listed1 = np.log(categories)
listed = cmap(norm(categories))


x = np.linspace(0, 6, len(categories))
y = np.zeros((len(categories), ))
colors = cmap(norm(categories_log))

plt.scatter(x,y,c=categories, cmap=cmap, norm=norm, s=1000)
plt.show()
