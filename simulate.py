from clr import calc_funding_for
import pandas as pd


def init_world(params):
    n_app_devs = params['n_app_devs']
    n_lib_devs = params['n_lib_devs']
    n_users = params['n_users']
    apps_built_per_app_dev = params['apps_built_per_app_dev']
    app_user_penetration = params['app_user_penetration']
    face_app_value_to_user = params['face_app_value_to_user']
    user_lib_awareness = params['user_lib_awareness']
    true_lib_value_ratio = params['true_lib_value_ratio']

    n_apps = n_app_devs * apps_built_per_app_dev
    n_libs = n_lib_devs
    per_app_users = n_users * app_user_penetration
    n_app_users = n_users * n_apps * app_user_penetration
    apps_used_per_user = n_apps * app_user_penetration

    true_lib_value_per_app = face_app_value_to_user * true_lib_value_ratio
    true_app_value_per_app = face_app_value_to_user - true_lib_value_per_app

    known_lib_value_to_user = true_lib_value_per_app * user_lib_awareness
    known_app_value_to_user = face_app_value_to_user - known_lib_value_to_user

    total_true_value_per_app = true_app_value_per_app * per_app_users
    total_true_value_per_lib = true_lib_value_per_app * n_app_users

    lib_value_to_app_dev = true_lib_value_per_app * per_app_users

    world = params.copy()

    world.update([
        ('n_apps', n_apps),
        ('n_libs', n_libs),
        ('per_app_users', per_app_users),
        ('n_app_users', n_app_users),
        ('apps_used_per_user', apps_used_per_user),
        ('known_lib_value_to_user', known_lib_value_to_user),
        ('known_app_value_to_user', known_app_value_to_user),
        ('true_lib_value_per_app', true_lib_value_per_app),
        ('true_app_value_per_app', true_app_value_per_app),
        ('total_true_value_per_app', total_true_value_per_app),
        ('total_true_value_per_lib', total_true_value_per_lib),
        ('lib_value_to_app_dev', lib_value_to_app_dev)
    ])

    return world


def true_values(world):
    n_apps = world['n_apps']
    n_libs = world['n_libs']
    total_true_value_per_app = world['total_true_value_per_app']
    total_true_value_per_lib = world['total_true_value_per_lib']

    total_true_app_value = total_true_value_per_app * n_apps
    total_true_lib_value = total_true_value_per_lib * n_libs
    total_true_value = total_true_app_value + total_true_lib_value

    lib_value_ratio = total_true_lib_value / total_true_value

    world.update([
        ('total_true_value', total_true_value)
    ])

    results = {
        'true app value': total_true_app_value,
        'true lib value': total_true_lib_value,
        'lib value ratio': lib_value_ratio
    }
    return (results, world)


def run_clr(world):
    n_apps = world['n_apps']
    n_libs = world['n_libs']
    clr_budget = world['clr_budget']

    raw_match_per_app, directs_per_app, world2 = calc_funding_for('app', world)
    raw_match_per_lib, directs_per_lib, world3 = calc_funding_for(
        'lib', world2)

    per_dev_contribs_per_lib = world3['per_dev_contribs_per_lib']

    total_directs = directs_per_app * n_apps + directs_per_lib
    per_app_directs_ratio = directs_per_app / total_directs
    per_lib_directs_ratio = directs_per_lib / total_directs

    raw_matches = [raw_match_per_app] * n_apps + [raw_match_per_lib] * n_libs
    total_raw_matches = sum(raw_matches)
    per_app_match_ratio = raw_matches[0] / total_raw_matches
    per_lib_match_ratio = raw_matches[10] / total_raw_matches

    clr_match_per_app = per_app_match_ratio * clr_budget
    clr_match_per_lib = per_lib_match_ratio * clr_budget

    funds_received_per_app = clr_match_per_app + directs_per_app
    funds_received_per_lib = clr_match_per_lib + directs_per_lib

    net_funding_per_app = funds_received_per_app - per_dev_contribs_per_lib

    app_funds_received = funds_received_per_app * n_apps
    lib_funds_received = funds_received_per_lib * n_libs

    lib_funding_ratio = lib_funds_received / \
        (lib_funds_received + app_funds_received)

    world3.update([
        ('raw_match_per_app', raw_match_per_app),
        ('raw_match_per_lib', raw_match_per_lib),
        ('directs_per_app', directs_per_app),
        ('directs_per_lib', directs_per_lib),
        ('total_directs', total_directs),
        ('total_raw_matches', total_raw_matches),
        ('per_app_match_ratio', per_app_match_ratio),
        ('per_app_directs_ratio', per_app_directs_ratio),
        ('clr_match_per_app', clr_match_per_app),
        ('clr_match_per_lib', clr_match_per_lib),


    ])

    results = {
        'lib matching ratio': round(per_lib_match_ratio, 3),
        'lib direct funding ratio': round(per_lib_directs_ratio, 3),
        'lib total funding ratio': round(lib_funding_ratio, 3),
        'app funds received': round(app_funds_received, ),
        'lib funds received': round(lib_funds_received, 2),
        'per app net funding': round(net_funding_per_app, 2),
        'per lib net funding': round(funds_received_per_lib, 2)
    }

    return (results, world3)


def run_simulation(params):
    world = init_world(params)
    trues, world2 = true_values(world)
    funds, world3 = run_clr(world2)
    results = trues.copy()
    results.update(funds)

    return results, world3


def multi_sim(params, sim_param, sim_values):
    rows = []

    for i in sim_values:
        params[sim_param] = i
        results, _ = run_simulation(params)
        cells = [i] + [results[k] for k in results.keys()]
        rows.append(cells)

    columns = [sim_param] + list(results.keys())

    df = pd.DataFrame(data=rows, columns=columns).set_index(sim_param)

    return df
