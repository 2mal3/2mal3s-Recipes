import os
from json import loads
from shutil import rmtree


def add_item(item, type):
    if item not in items:
        items[item] = [type, []]
    items[item][1].append(f"{root}/{file_}")


items = {}
debug_data = {"files": {"total": 0, "normal": 0, "shapeless": 0, "crafting": 0, "smithing": 0}, "items": 0}
os.chdir("data")

# Generates file list
print(f"[INFO] Start scanning files under {os.getcwd()}\n")
walker = os.walk("2re/recipes")
for root, dirs, files in walker:
    for file_ in files:
        print(f"    [DEBUG] Scanning file {root}/{file_}")
        debug_data["files"]["total"] += 1

        file = open(f"{root}/{file_}", "r")
        recipe = loads(file.read())
        
        # "Normal" recipes
        if recipe["type"] != "minecraft:crafting_shapeless" and recipe["type"] != "minecraft:crafting_shaped" and recipe["type"] != "minecraft:smithing":
            debug_data["files"]["normal"] += 1
            for ingredient in recipe["ingredient"]:
                debug_data["items"] += 1
                add_item(recipe["ingredient"][ingredient], ingredient)

        # "Special" recipes
        # Shapeless crafting
        if recipe["type"] == "minecraft:crafting_shapeless":
            debug_data["files"]["shapeless"] += 1
            for ingredient in recipe["ingredients"]:
                debug_data["items"] += 1
                if "item" in ingredient:
                    add_item(ingredient["item"], 'item')
                if "tag" in ingredient:
                    add_item(ingredient["tag"], 'tag')

        # # Crafting
        if recipe["type"] == "minecraft:crafting_shaped":
            debug_data["files"]["crafting"] += 1
            for key in recipe["key"]:
                debug_data["items"] += 1
                for ingredient in recipe["key"][key]:
                    if ingredient == "item":
                        add_item(recipe["key"][key]["item"], 'item')
                    if ingredient == "tag":
                        add_item(recipe["key"][key]["tag"], 'tag')
        # # Smithing
        if recipe["type"] == "minecraft:smithing":
            debug_data["files"]["smithing"] += 1
            debug_data["items"] += 2

            if "tag" in recipe["base"]:
                add_item(recipe["base"]["tag"], 'tag')
            if "item" in recipe["base"]:
                add_item(recipe["base"]["item"], 'item')

            if "tag" in recipe["addition"]:
                add_item(recipe["addition"]["tag"], 'tag')
            if "item" in recipe["addition"]:
                add_item(recipe["addition"]["item"], 'item')

        file.close()


print(f"\n[INFO] Scanned {debug_data['files']['total']} recipes and processed {debug_data['items']} items")
print(f"[INFO] Generate {len(items)} advancements\n")


# Writes new files
rmtree("2re/advancements/recipes")
os.mkdir("2re/advancements/recipes")
for item in items:
    print(f"    [DEBUG] Generate advancement for {items[item][0]} {item}")

    advancement = {"parent": "minecraft:recipes/root", "criteria": {"requirement": {"trigger": "minecraft:inventory_changed", "conditions": {"items": [{}]}}}, "rewards": {"recipes": []}}
    # Append trigger
    if items[item][0] == "item":
        advancement["criteria"]["requirement"]["conditions"]["items"][0]["items"] = []
        advancement["criteria"]["requirement"]["conditions"]["items"][0]["items"].append(item)
    if items[item][0] == "tag":
        advancement["criteria"]["requirement"]["conditions"]["items"][0]["tag"] = item
    # Append rewards
    for recipe in items[item][1]:
        temp = recipe[:3] + ":" + recipe[12:-5]
        advancement["rewards"]["recipes"].append(temp)

    # Write the file
    if ":" in item:
        item = item.split(":")[1]
    file = open(f"2re/advancements/recipes/{item}.json", "w")
    file.write(str(advancement).replace("'", '"'))

    file.close()

print("\n[INFO] Done!")
# print(items)
