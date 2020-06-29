import math


def simulate_contributions_for(recipient_type, world):
    contribution_ratio = world['contribution_ratio']
    n_app_devs = world['n_app_devs']
    # n_apps = world['n_apps']
    n_users = world['n_users']
    per_app_users = world['per_app_users']
    apps_used_per_user = world['apps_used_per_user']
    lib_app_penetration = world['lib_app_penetration']
    known_app_value_to_user = world['known_app_value_to_user']
    known_lib_value_to_user = world['known_lib_value_to_user']
    lib_value_to_app_dev = world['lib_value_to_app_dev']
    app_dev_user_awareness = world['app_dev_user_awareness']

    contributing_devs = math.ceil(
        n_app_devs * lib_app_penetration)

    if(recipient_type == 'app'):
        contributing_users = math.ceil(per_app_users)
        user_amount = known_app_value_to_user * contribution_ratio
        dev_amount = 0

    else:  # lib
        contributing_users = math.ceil(n_users)
        user_amount = known_lib_value_to_user * apps_used_per_user
        dev_amount = (lib_value_to_app_dev -
                      (known_lib_value_to_user * per_app_users * app_dev_user_awareness)) * contribution_ratio

    user_contribs = [user_amount] * contributing_users
    dev_contribs = [dev_amount] * contributing_devs
    contributions = user_contribs + dev_contribs

    total_user_contribs_label = 'total_user_contribs_per_' + recipient_type
    total_dev_contribs_label = 'total_dev_contribs_per_' + recipient_type
    per_user_contribs_label = 'per_user_contribs_per_' + recipient_type
    per_dev_contribs_label = 'per_dev_contribs_per_' + recipient_type

    world.update([
        (total_user_contribs_label, sum(user_contribs)),
        (total_dev_contribs_label, sum(dev_contribs)),
        (per_user_contribs_label, user_amount),
        (per_dev_contribs_label, dev_amount)
    ])

    return contributions, world


def sum_of_roots(contributions):
    roots = [i ** (1/2) for i in contributions]
    return sum(roots)


def calc_match_for(contributions):
    roots = sum_of_roots(contributions)
    return roots ** 2


def calc_funding_for(recipient_type, world):
    contributions, world = simulate_contributions_for(recipient_type, world)
    raw_match = calc_match_for(contributions)
    directs = sum(contributions)

    return raw_match, directs, world


def calc_clr_matches(_raw_matches, world):
    budget = world['clr_budget']

    raw_sum = sum(_raw_matches)
    props = [i / raw_sum for i in _raw_matches]
    clr_matches = [i * budget for i in props]
    return clr_matches
