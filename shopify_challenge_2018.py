# good copy

import requests, json
import networkx as nx
from collections import OrderedDict


ENDPOINT_PREFIX = 'https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=1&page='


def find_total_pages(url):
    r = requests.get(url)
    data = r.json()
    pagination = data['pagination']
    total = pagination['total']
    per_page = pagination['per_page']
    total_pages = total / per_page
    return total_pages + 1


def get_all_data_from_pages(total_pages):
    items = []
    for i in range(1, total_pages):
        key = str(i)
        url = ENDPOINT_PREFIX + key
        r = requests.get(url)
        data = r.json()
        for element in data['menus']:
            items.append(element)
    return items


def create_graph(items):
    G = nx.DiGraph()
    for element in items:
        node = element['id']
        G.add_node(node)
        edges = element['child_ids']
        for e in edges:
            G.add_edge(node, e)
    return G


def create_id_list(items):
    id_list = []
    for item in items:
        iid = item['id']
        if iid in id_list:
            continue
        id_list.append(iid)
    return id_list


def is_invalid(menu, invalid_menus):
    for im in invalid_menus:
        if bool(set(im).intersection(set(menu))):
            return True
    return False


def create_all_menus_list(id_list, G):
    all_menus = []
    visited = []
    for iid in id_list:
        if iid in visited:
            continue
        tmp_list = list(nx.dfs_preorder_nodes(G, iid))
        visited.extend(tmp_list)
        all_menus.append(tmp_list)
    return all_menus


def create_invalid_menus_list(G):
    invalid_menus = list(nx.simple_cycles(G))
    return invalid_menus


def create_valid_menus_list(invalid_menus, all_menus):
    valid_menus = []
    for menu in all_menus:
        if is_invalid(menu, invalid_menus):
            continue
        valid_menus.append(menu)
    return valid_menus


def create_menus_output(dict_valid_menus, dict_invalid_menus):
    d = {"valid_menus": [{"root_id": key, "children": value} for key, value in dict_valid_menus.items()],
        "invalid_menus": [{"root_id": key, "children": value} for key, value in dict_invalid_menus.items()]
         }
    json_string = json.dumps(d)
    print json_string


def create_dictionary_menus(menu, count, dict_menu):
    value = []
    key = menu[0]
    for i in range(count, len(menu)):
        value.append(menu[i])
    dict_menu[key] = value


def create_dict_valid_menus(valid_menus):
    #dict_valid_menus = {}
    dict_valid_menus = OrderedDict()
    for element in valid_menus:
        element.sort()
        count = 1
        create_dictionary_menus(element, count, dict_valid_menus)
    return dict_valid_menus


def create_dict_invalid_menus(invalid_menus, G):
    #dict_invalid_menus = {}
    dict_invalid_menus = OrderedDict()
    for element in invalid_menus:
        element.sort()
        first_node = element[0]
        last_position = len(element) - 1
        last = element[last_position]
        last_edge = G.edges(last)
        for item in last_edge:
            if first_node in item:
                count = 0
            else:
                count = 1
        create_dictionary_menus(element, count, dict_invalid_menus)
    return dict_invalid_menus


def run():
    url = ENDPOINT_PREFIX + '1'
    total_pages = find_total_pages(url)
    items = get_all_data_from_pages(total_pages)
    G = create_graph(items)
    id_list = create_id_list(items)
    all_menus = create_all_menus_list(id_list, G)
    invalid_menus = create_invalid_menus_list(G)
    valid_menus = create_valid_menus_list(invalid_menus, all_menus)
    dict_valid_menus = create_dict_valid_menus(valid_menus)
    dict_invalid_menus = create_dict_invalid_menus(invalid_menus, G)
    create_menus_output(dict_valid_menus, dict_invalid_menus)


if __name__ == "__main__":
    run()
