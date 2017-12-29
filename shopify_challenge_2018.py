# good copy

import requests, json
import networkx as nx

ENDPOINT_PREFIX = 'https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=1&page='


def findTotalPages(url):
    r = requests.get(url)
    data = r.json()
    pagination = data['pagination']
    total = pagination['total']
    perpage = pagination['per_page']
    totalpages = total / perpage
    return totalpages + 1


def getAllDataFromPages(totalpages):
    items = []
    for i in range(1, totalpages):
        key = str(i)
        url = ENDPOINT_PREFIX + key
        r = requests.get(url)
        data = r.json()
        for element in data['menus']:
            items.append(element)
    return items


def createGraph(items):
    G = nx.DiGraph()
    for element in items:
        node = element['id']
        G.add_node(node)
        edges = element['child_ids']
        for e in edges:
            G.add_edge(node, e)
    return G


def createIdList(items):
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


def createAllMenusList(id_list, G):
    all_menus = []
    visited = []
    for iid in id_list:
        if iid in visited:
            continue
        tmp_list = list(nx.dfs_preorder_nodes(G, iid))
        visited.extend(tmp_list)
        all_menus.append(tmp_list)
    return all_menus


def createInvalidMenusList(G):
    invalid_menus = list(nx.simple_cycles(G))
    return invalid_menus


def createValidMenusList(invalid_menus, all_menus):
    valid_menus = []
    for menu in all_menus:
        if is_invalid(menu, invalid_menus):
            continue
        valid_menus.append(menu)
    return valid_menus


def createMenusOutput(dict_valid_menus, dict_invalid_menus):
    d = {"valid_menus": [{"root_id": key, "children": value} for key, value in dict_valid_menus.items()],
         "invalid_menus": [{"root_id": key, "children": value} for key, value in dict_invalid_menus.items()]
         }
    json_string = json.dumps(d)
    print json_string


def createDictionaryMenus(menu, count, dict_menu):
    value = []
    key = menu[0]
    for i in range(count, len(menu)):
        value.append(menu[i])
    dict_menu[key] = value


def createDictValidMenus(valid_menus):
    dict_valid_menus = {}
    for element in valid_menus:
        element.sort()
        count = 1
        createDictionaryMenus(element, count, dict_valid_menus)
    return dict_valid_menus


def createDictInvalidMenus(invalid_menus, G):
    dict_invalid_menus = {}
    for element in invalid_menus:
        element.sort()
        first_node = element[0]
        last_position = len(element) - 1
        last = element[last_position]
        last_edge = G.edges(last)
        for element in last_edge:
            if first_node in element:
                count = 0
            else:
                count = 1
        createDictionaryMenus(element, count, dict_invalid_menus)
    return dict_invalid_menus


def run():
    url = ENDPOINT_PREFIX + '1'
    totalpages = findTotalPages(url)
    items = getAllDataFromPages(totalpages)
    G = createGraph(items)
    id_list = createIdList(items)
    all_menus = createAllMenusList(id_list, G)
    invalid_menus = createInvalidMenusList(G)
    valid_menus = createValidMenusList(invalid_menus, all_menus)
    dict_valid_menus = createDictValidMenus(valid_menus)
    dict_invalid_menus = createDictInvalidMenus(invalid_menus, G)
    createMenusOutput(dict_valid_menus, dict_invalid_menus)

if __name__ == "__main__":
    run()
