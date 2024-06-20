import seaborn as sns
from matplotlib import rcParams
from drawbase.plot_time import plot_time
rcParams.update({'figure.autolayout': True})
sns.set(style="whitegrid", color_codes=True)

'''

    The variable DATA has the following possible states:
    wave;
    burgers;
    kdv;
    kdv_sindy;
    burgers_sindy;
    which corresponds to 5 input datasets and equations

'''
if __name__ == '__main__':
    DATA = "kdv_sindy"

    n_df = 2
    if DATA == "wave":
        path = 'data_wave/'
        names = ["0", "8.675e-6", "1.735e-5", "2.6025e-5", "3.47e-5"]
    elif DATA == "burgers":
        path = 'data_burg/'
        names = ["0", "9.175e-6", "1.835e-5", "2.7525e-5", "3.67e-5"]
    elif DATA == "burgers_sindy":
        path = 'data_burg_sindy/'
        names = ["0", "0.0075", "0.015", "0.0225", "0.03"]
    elif DATA == "kdv_sindy":
        path = 'data_kdv_sindy/'
        names = ["0", "2e-5", "4e-5", "6e-5", "8e-5"]
    elif DATA == "kdv":
        path = 'data_kdv/'
        names = ["0", "0.023", "0.046", "0.069", "0.092"]
    else:
        raise NameError('Unknown equation type')
    plot_time(path, names, n_df)
