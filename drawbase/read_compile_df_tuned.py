import pandas as pd
import numpy as np


def read_csv(path, names, df_n):
    dfo_ls, dfs_ls, dfs_tuned = [], [], []
    for name in names:
        dfo_ls.append(pd.read_csv(f'{path}dfo{name}.csv', index_col="Unnamed: 0"))
        dfs_ls.append(pd.read_csv(f'{path}dfs{name}.csv', index_col="Unnamed: 0"))
        dfs_tuned.append(pd.read_csv(f'{path}dfs{name}_tuned.csv', index_col="Unnamed: 0"))

    if df_n == 3:
        return [dfo_ls, dfs_ls, dfs_tuned]
    else:
        dfp_ls = []
        for name in names:
            dfp_ls.append(pd.read_csv(f'{path}dfp{name}.csv', index_col="Unnamed: 0"))

        return [dfo_ls, dfs_ls, dfs_tuned, dfp_ls]


def _round_wide_range_values(df_ls: list, decimals):
    df_maes = [df.MAE for df in df_ls]
    for df in df_maes:
        for i in range(len(df)):
            new_val = df.loc[i].round(decimals)
            decimal = decimals
            while new_val == 0.0:
                decimal = decimal + 1
                new_val = df.loc[i].round(decimal)
            if decimal == decimals:
                df.loc[i] = df.loc[i].round(decimal)
            else:
                df.loc[i] = df.loc[i].round(decimal+1)
    return df_maes


def _round_values(df_lsls, decimals, wide_range=False):
    df_lsr = []
    ls_all_mae = []
    if type(decimals) == int:
        decimals_epde = decimals
    else:
        decimals_epde = decimals[0]
        decimals_sindy = decimals[1]

    for i in range(len(df_lsls)):
        if i != 3:
            if wide_range:
                df_maes = _round_wide_range_values(df_lsls[i], decimals_epde)
                df_lsr.append(df_maes)
                ls_all_mae.append(pd.concat(df_maes))
            else:
                df_lsr.append([df.MAE.round(decimals_epde) for df in df_lsls[i]])
                ls_all_mae.append(pd.concat([df.MAE.round(decimals_epde) for df in df_lsls[i]]))
        else:
            df_maes = _round_wide_range_values(df_lsls[i], decimals_sindy)
            df_lsr.append(df_maes)
            ls_all_mae.append(pd.concat(df_maes))
    dfr = pd.concat(ls_all_mae)
    categories = dfr.unique()
    if np.nanmin(categories) == 0.0:
        return _round_values(df_lsls, decimals, wide_range=True)
    if len(categories) >= 25:
        categories, df_lsr = _round_if_many(df_lsr)

    return categories, df_lsr


def _round_if_many(df_lsr):
    ls_all_mae = []
    for i in range(len(df_lsr)):
        for df in df_lsr[i]:
            for j in range(len(df)):
                for rank in range(1, 10):
                    if rank*1e-5 + 0.5e-5 > df.loc[j] >= rank*1e-5 - 0.5e-5:
                        df.loc[j] = rank*1e-5
            ls_all_mae.append(df)
    dfr = pd.concat(ls_all_mae)
    categories = dfr.unique()
    categories.sort()
    return categories, df_lsr


def _split_numbers_list(numbers_list, n_groups):
    n_splits = min(len(numbers_list), n_groups)

    ratios = [
        (i, numbers_list[i + 1] / numbers_list[i]) for i in range(len(numbers_list) - 1)
    ]
    sorted_ratios = sorted(ratios, key=lambda r: r[1], reverse=True)

    chosen_splits = (
            [0]
            + sorted([r[0] + 1 for r in sorted_ratios[: n_splits - 1]])
            + [len(numbers_list)]
    )
    return [
        numbers_list[chosen_splits[i]: chosen_splits[i + 1]]
        for i in range(len(chosen_splits) - 1)]


def _make_input_df(names, df_ls, decimals):
    categories, df_lsr = _round_values(df_ls, decimals=decimals)
    categories = categories[np.argsort(categories)]

    count_ls = []
    for _ in range(len(df_ls)):
        count_ls.append(pd.DataFrame(0, index=names, columns=categories))

    cdf_ls = []
    for k in range(len(df_ls)):
        cdf_ls.append(pd.concat([df_lsr[k][i].rename(names[i]) for i in range(len(names))], axis=1))

    for k in range(len(cdf_ls)):
        for name in names:
            counted = cdf_ls[k][name].value_counts()
            nans = sum(cdf_ls[k][name].isna())

            for idx in counted.index:
                count_ls[k].loc[name, idx] = counted.loc[idx]
            count_ls[k].loc[name, np.nan] = int(nans)
    return count_ls


def read_compile_mae_df(path, names, decimals, n_df):
    df_ls = read_csv(path, names, n_df)
    return _make_input_df(names, df_ls, decimals=decimals)
