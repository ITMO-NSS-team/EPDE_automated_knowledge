import time
import numpy as np
import pandas as pd
import epde.interface.interface as epde_alg
from epde.evaluators import CustomEvaluator
from epde.interface.prepared_tokens import CustomTokens
from kdv_init_distrib import coefficients1, coefficients2
import matplotlib.pyplot as plt
import traceback
import logging
import os
from pathlib import Path


def find_coeff_diff(res):
    differences = []

    for pareto_front in res:
        for soeq in pareto_front:
            if soeq.obj_fun[0] < 0.02:
                eq_text = soeq.vals.chromosome['u'].value.text_form
                terms_dict = out_formatting(eq_text)
                diff = coefficients_difference(terms_dict)
                if diff != -1:
                    differences.append(diff)

    return differences


def coefficients_difference(terms_dict):
    mae1 = 0.
    mae2 = 0.
    eq_found = 0
    for term_hash in terms_dict.keys():
        mae1 += abs(terms_dict.get(term_hash) - coefficients1.get(term_hash))
        mae2 += abs(terms_dict.get(term_hash) - coefficients2.get(term_hash))
        if coefficients1.get(term_hash) != 0.0 and (abs(terms_dict.get(term_hash) - coefficients1.get(term_hash)) < 0.1\
                or abs(terms_dict.get(term_hash) - coefficients2.get(term_hash)) < 0.1):
            eq_found += 1

    mae1 /= len(terms_dict)
    mae2 /= len(terms_dict)
    mae = min(mae1, mae2)

    if eq_found == 4:
        return mae
    else:
        return -1


def out_formatting(string):
    string = string.replace("u{power: 1.0}", "u")
    string = string.replace("d^2u/dx2^2{power: 1.0}", "d^2u/dx2^2")
    string = string.replace("d^2u/dx1^2{power: 1.0}", "d^2u/dx1^2")
    string = string.replace("du/dx1{power: 1.0}", "du/dx1")
    string = string.replace("du/dx2{power: 1.0}", "du/dx2")
    string = string.replace("cos(t)sin(x){power: 1.0}", "cos(t)sin(x)")
    string = string.replace("d^3u/dx2^3{power: 1.0}", "d^3u/dx2^3")
    string = string.replace(" ", "")

    ls_equal = string.split('=')
    ls_left = ls_equal[0].split('+')
    ls_terms = []
    for term in ls_left:
        ls_term = term.split('*')
        ls_terms.append(ls_term)
    ls_right = ls_equal[1].split('*')

    terms_dict = {}
    for term in ls_terms:
        if len(term) == 1:
            terms_dict[1] = float(term[0])
        else:
            coeff = float(term.pop(0))
            terms_dict[hash_term(term)] = coeff

    terms_dict[hash_term(ls_right)] = -1.
    return terms_dict


def hash_term(term):
    total_term = 0
    for token in term:
        total_token = 1
        if type(token) == tuple:
            token = token[0]
        for char in token:
            total_token += ord(char)
        total_term += total_token * total_token
    return total_term


if __name__ == '__main__':
    path_full = os.path.join(Path().absolute().parent, "data_kdv", "KdV_sln_100.csv")
    df = pd.read_csv(path_full, header=None)

    os.path.join(Path().absolute().parent, "data_kdv", "d_x_100.csv")
    dddx = pd.read_csv(os.path.join(Path().absolute().parent, "data_kdv", "ddd_x_100.csv"), header=None)
    ddx = pd.read_csv(os.path.join(Path().absolute().parent, "data_kdv", "dd_x_100.csv"), header=None)
    dx = pd.read_csv(os.path.join(Path().absolute().parent, "data_kdv", "d_x_100.csv"), header=None)
    dt = pd.read_csv(os.path.join(Path().absolute().parent, "data_kdv", "d_t_100.csv"), header=None)

    u_init = df.values
    u_init = np.transpose(u_init)

    ddd_x = dddx.values
    ddd_x = np.transpose(ddd_x)
    dd_x = ddx.values
    dd_x = np.transpose(dd_x)
    d_x = dx.values
    d_x = np.transpose(d_x)
    d_t = dt.values
    d_t = np.transpose(d_t)

    derivs = np.zeros(shape=(u_init.shape[0],u_init.shape[1],4))
    derivs[:, :, 0] = d_t
    derivs[:, :, 1] = d_x
    derivs[:, :, 2] = dd_x
    derivs[:, :, 3] = ddd_x

    t = np.linspace(0, 1, u_init.shape[0])
    x = np.linspace(0, 1, u_init.shape[1])

    boundary = 0
    dimensionality = u_init.ndim
    grids = np.meshgrid(t, x, indexing='ij')

    ''' Parameters of the experiment '''
    write_csv = True
    print_results = True
    max_iter_number = 50

    draw_not_found = []
    draw_time = []
    draw_avgmae = []
    start_gl = time.time()
    magnitudes = [0, 0.023, 0.046, 0.069, 0.092]
    for magnitude in magnitudes:
        title = f'dfo{magnitude}'

        time_ls = []
        differences_ls = []
        differences_ls_none = []
        num_found_eq = []
        mean_diff_ls = []
        i = 0
        population_error = 0
        while i < max_iter_number:
            if magnitude != 0:
                u = u_init + np.random.normal(scale=magnitude * np.abs(u_init), size=u_init.shape)
            else:
                u = u_init
            epde_search_obj = epde_alg.EpdeSearch(use_solver=False, boundary=boundary,
                                                   dimensionality=dimensionality, coordinate_tensors=grids)

            custom_trigonometric_eval_fun = {
                'cos(t)sin(x)': lambda *grids, **kwargs: (np.cos(grids[0]) * np.sin(grids[1])) ** kwargs['power']}
            custom_trig_evaluator = CustomEvaluator(custom_trigonometric_eval_fun,
                                                    eval_fun_params_labels=['power'])
            trig_params_ranges = {'power': (1, 1)}
            trig_params_equal_ranges = {}

            custom_trig_tokens = CustomTokens(token_type='trigonometric',
                                              token_labels=['cos(t)sin(x)'],
                                              evaluator=custom_trig_evaluator,
                                              params_ranges=trig_params_ranges,
                                              params_equality_ranges=trig_params_equal_ranges,
                                              meaningful=True, unique_token_type=False)

            epde_search_obj.set_moeadd_params(population_size=8, training_epochs=90)
            start = time.time()
            try:
                epde_search_obj.fit(data=u, max_deriv_order=(1, 3),
                                    equation_terms_max_number=4, equation_factors_max_number=2,
                                    eq_sparsity_interval=(1e-08, 1e-06), derivs=[derivs],
                                    additional_tokens=[custom_trig_tokens, ])
            except Exception as e:
                logging.error(traceback.format_exc())
                population_error += 1
                continue
            end = time.time()
            epde_search_obj.equation_search_results(only_print=True, num=2)
            time1 = end-start

            res = epde_search_obj.equation_search_results(only_print=False, num=2)
            difference_ls = find_coeff_diff(res)

            if len(difference_ls) != 0:
                differences_ls.append(min(difference_ls))
                differences_ls_none.append(min(difference_ls))
                mean_diff_ls += difference_ls
            else:
                differences_ls_none.append(None)

            num_found_eq.append(len(difference_ls))
            print('Overall time is:', time1)
            print(f'Iteration processed: {i+1}/{max_iter_number}\n')
            time_ls.append(time1)
            i += 1

        if write_csv:
            arr = np.array([differences_ls_none, time_ls, num_found_eq])
            arr = arr.T
            df = pd.DataFrame(data=arr, columns=['MAE', 'time', 'number_found_eq'])
            df.to_csv(os.path.join(Path().absolute().parent, "data_kdv", f"{title}.csv"))

        if print_results:
            print()
            print(f'\nAverage time, s: {sum(time_ls) / len(time_ls):.2f}')
            if len(mean_diff_ls) != 0:
                print(f'Average MAE per eq: {sum(mean_diff_ls) / len(mean_diff_ls):.6f}')
                print(
                    f'Average minimum MAE per run: {sum(differences_ls) / (max_iter_number - num_found_eq.count(0)):.6f}')
            else:
                print("Equation was not found in any run")
            print(f'Average # of found eq per run: {sum(num_found_eq) / max_iter_number:.2f}')
            print(f"Runs where eq was not found: {num_found_eq.count(0)}")
            print(f"Num of population error occurrence: {population_error}")

        if len(mean_diff_ls) != 0:
            draw_avgmae.append(sum(differences_ls) / (max_iter_number - num_found_eq.count(0)))
        else:
            draw_avgmae.append(0.08)
        draw_not_found.append(num_found_eq.count(0))
        draw_time.append(sum(time_ls) / len(time_ls))

    end_gl = time.time()
    print(f"Overall time: {(end_gl - start_gl) / 60:.2f}, min.")
    plt.title("Original")
    plt.plot(magnitudes, draw_not_found, linewidth=2, markersize=9, marker='o')
    plt.ylabel("No. runs with not found eq.")
    plt.xlabel("Magnitude value")
    plt.grid()
    plt.show()

    plt.plot(magnitudes, draw_time, linewidth=2, markersize=9, marker='o')
    plt.title("Original")
    plt.ylabel("Time, s.")
    plt.xlabel("Magnitude value")
    plt.grid()
    plt.show()

    plt.plot(magnitudes, draw_avgmae, linewidth=2, markersize=9, marker='o')
    plt.title("Original")
    plt.ylabel("Average MAE")
    plt.xlabel("Magnitude value")
    plt.grid()
    plt.show()
