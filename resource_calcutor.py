import sys
import os
import argparse
import copy

class Stack:
    def __init__(self, item, amount):
        self.item = item
        self.amount = amount
    
    def __str__(self):
        return "{0}x {1}".format(str(self.amount), self.item)

    @staticmethod
    def from_str(input):
        splitted = input.strip().split()
        return Stack(" ".join(splitted[1:]), int(splitted[0]))

class Recipe:
    def __init__(self, amount):
        self.amount = amount
        self.materials = []
        self.total_materials = 0
    
    def __str__(self):
        return "({0},{1},{2}) - {3}".format(self.amount, len(self.materials), self.total_materials, ",".join(str(x) for x in self.materials))

    def __lt__(self, other):
        if self.amount != other.amount:
            return self.amount >= other.amount
        sl = len(self.materials)
        ol = len(other.materials)
        if sl != ol:
            return sl <= ol
        return self.total_materials <= other.total_materials

    def add_material(self, material):
        self.total_materials = self.total_materials + material.amount
        self.materials.append(material)

def readable_dir(prospective_dir):
  if not os.path.isdir(prospective_dir):
    raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
  if os.access(prospective_dir, os.R_OK):
    return prospective_dir
  else:
    raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

def all_files(dir):
    files = []
    for root, _, f in os.walk(dir):
        for file in f:
            if ".txt" in file:
                files.append(os.path.join(root, file))
    return files

def process_recipes(dir):
    files = all_files(dir)

    recipes = dict()
    for f in files:
        with open(f) as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                if line.strip() == "":
                    continue
                target_stack = Stack.from_str(line)
                recipe_item_amount = int(fp.readline().strip())
                recipe = Recipe(target_stack.amount)
                for _ in range(0, recipe_item_amount):
                    recipe.add_material(Stack.from_str(fp.readline()))
                if target_stack.item not in recipes.keys():
                    recipes[target_stack.item] = []
                recipes[target_stack.item].append(recipe)

    for recipe_list in recipes.values():
        recipe_list.sort()
    
    return recipes

def calculate_resources(recipes, target_file):
    raw_stacks = dict()
    for line in target_file:
        target = Stack.from_str(line)
        raw_stacks[target.item] = raw_stacks.get(target.item, 0) + target.amount

    temp = None
    while temp is None or temp != raw_stacks:
        temp = copy.deepcopy(raw_stacks)
        for target_item, target_amount in temp.items():
            if target_item in recipes.keys():
                target_recipes = recipes[target_item]
                remaining = target_amount
                idx = 0
                expansion = dict()
                while remaining > 0:
                    if idx == len(target_recipes):
                        remaining = 0
                        for material in target_recipes[-1].materials:
                            expansion[material.item] = expansion.get(material.item, 0) + material.amount
                    else:
                        if remaining >= target_recipes[idx].amount:
                            remaining = remaining - target_recipes[idx].amount
                            for material in target_recipes[idx].materials:
                                expansion[material.item] = expansion.get(material.item, 0) + material.amount
                        else:
                            idx = idx + 1
                del raw_stacks[target_item]
                for item, amount in expansion.items():
                    raw_stacks[item] = raw_stacks.get(item, 0) + amount
                break
    
    return raw_stacks

def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "recipes", nargs=1,
        metavar="RECIPES_DIRECTORY", type=readable_dir,
        help="path to the recipes directory")

    parser.add_argument(
        "target", nargs=1,
        metavar="TARGET_FILE", type=argparse.FileType("r"),
        help="path to the target itens file")

    parser.add_argument(
        "output", nargs=1,
        metavar="OUTPUT_FILE", type=argparse.FileType("w"),
        help="path to the output file")

    args = parser.parse_args()

    recipes = process_recipes(args.recipes[0])

    raw = calculate_resources(recipes, args.target[0])

    for item, amount in raw.items():
        print("{0} {1}".format(str(amount), item).strip(), file=args.output[0])

if __name__ == "__main__":
    main()