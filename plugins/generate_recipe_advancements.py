from beet import Context, Advancement


def beet_default(ctx: Context):
    advancements = get_advancements(ctx)
    create_advancements(ctx, advancements)


def create_advancements(ctx: Context, data: dict):
    for ingredient, paths in data.items():
        name = ingredient.split(":")[1]
        advancement = {
            "parent": "minecraft:recipes/root",
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:inventory_changed",
                    "conditions": {"items": [{}]},
                }
            },
            "rewards": {"recipes": paths},
        }

        # Normal advancement
        if not ingredient.startswith("#"):
            advancement["criteria"]["requirement"]["conditions"]["items"][0][
                "items"
            ] = [ingredient]
        # Tag
        else:
            advancement["criteria"]["requirement"]["conditions"]["items"][0][
                "tag"
            ] = ingredient[1:]

        ctx.data.advancements[f"2re:recipes/{name}"] = Advancement(advancement)


def get_advancements(ctx: Context) -> dict:
    """Get all new recipe results with their ingredients"""
    advancements = {}

    recipes = ctx.data.recipes
    for recipe in recipes.match("2re:*"):
        content = recipes[recipe].data

        ingredients = []
        if content["type"] == "minecraft:crafting_shaped":
            ingredients = get_crafting_shaped_ingredients(content["key"])
        if content["type"] == "minecraft:crafting_shapeless":
            ingredients = get_ingredient(content["ingredients"])
        if content["type"] in [
            "minecraft:blasting",
            "minecraft:smelting",
            "minecraft:smoking",
            "minecraft:campfire_cooking",
            "minecraft:stonecutting",
        ]:
            ingredients = get_ingredient(content["ingredient"])
        if content["type"] == "minecraft:smithing":
            ingredients += get_ingredient(content["base"])
            ingredients += get_ingredient(content["addition"])
        ingredients = remove_duplicates(ingredients)

        ingredients.append(get_result(content["result"]))

        for ingredient in ingredients:
            if ingredient not in advancements:
                advancements[ingredient] = []
            advancements[ingredient].append(recipe)

    return advancements


def get_result(part: dict | list) -> str:
    result = ""

    if type(part) == dict:
        result = part["item"]
    if type(part) == str:
        result = part

    return result


def get_ingredient(part: dict | list) -> list:
    ingredients = []

    if type(part) == dict:
        ingredient = part.get("item")
        if ingredient:
            ingredients.append(ingredient)

        ingredient = part.get("tag")
        if ingredient:
            ingredients.append("#" + ingredient)

    if type(part) == list:
        for element in part:
            ingredient = get_ingredient(element)
            ingredients += ingredient

    return ingredients


def get_crafting_shaped_ingredients(keys: dict) -> list:
    ingredients = []

    for element in keys.values():
        ingredients += get_ingredient(element)

    return ingredients


def remove_duplicates(list_: list) -> list:
    return list(set(list_))
