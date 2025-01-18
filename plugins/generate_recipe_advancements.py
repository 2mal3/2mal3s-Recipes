from beet import Context, Advancement


def beet_default(ctx: Context):
    ingredient_recipe_relations = get_ingredient_recipe_relations(ctx)
    create_advancements_from_data(ctx, ingredient_recipe_relations)


def create_advancements_from_data(ctx: Context, data: dict[str, list[str]]):
    for ingredient, recipe_paths in data.items():
        name = ingredient.split(":")[1]
        advancement = {
            "parent": "minecraft:recipes/root",
            "criteria": {
                "requirement": {
                    "trigger": "minecraft:inventory_changed",
                    "conditions": {"items": [{"items": ingredient}]},
                }
            },
            "rewards": {"recipes": recipe_paths},
        }

        ctx.data.advancements[f"2re:recipes/{name}"] = Advancement(advancement)


def get_ingredient_recipe_relations(ctx: Context) -> dict:
    """Get all new recipe results with their ingredients"""
    relations = {}

    recipes = ctx.data.recipes
    for recipe in recipes.match("2re:*"):
        content = recipes[recipe].data

        ingredients = []
        if content["type"] == "minecraft:crafting_shaped":
            ingredients = get_shaped_crafting_shaped_ingredients(content["key"])
        elif content["type"] == "minecraft:crafting_shapeless":
            ingredients = get_ingredients_from_ingredient_object(content["ingredients"])
        elif content["type"] in [
            "minecraft:blasting",
            "minecraft:smelting",
            "minecraft:smoking",
            "minecraft:campfire_cooking",
            "minecraft:stonecutting",
        ]:
            ingredients = get_ingredients_from_ingredient_object(content["ingredient"])
        ingredients = remove_duplicates(ingredients)

        for ingredient in ingredients:
            if ingredient not in relations:
                relations[ingredient] = []
            relations[ingredient].append(recipe)

    return relations


def get_shaped_crafting_shaped_ingredients(keys: dict[str, list[str] | str]) -> list[str]:
    ingredients = []
    for ingredient_object in keys.values():
        ingredients += get_ingredients_from_ingredient_object(ingredient_object)
    return ingredients


def get_ingredients_from_ingredient_object(ingredient_object: str | list[str]) -> list[str]:
    if isinstance(ingredient_object, str):
        return [ingredient_object]
    elif isinstance(ingredient_object, list):
        return ingredient_object

    raise ValueError("Invalid ingredient object")


def remove_duplicates(list_: list) -> list:
    return list(set(list_))
