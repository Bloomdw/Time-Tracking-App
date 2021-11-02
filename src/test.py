all_items = {"name1": 1, "name4": 4, "name3": 3, "name2": 2, "name5": 5}

a = dict(sorted(all_items.items(), key=lambda item: item[1]))
print(a)

items = a.items()
print(items[1][1])
print(list(items)[1][1])
