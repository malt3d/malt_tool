#!/usr/bin/env python3

import list_messages
import module_tools

class malt_game():
    modules = []
    name = ""

def main():
    game = malt_game()
    game.modules = ["malt_basic", "malt", "malt_render", "malt_game"]
    game.name = "hello world"
    print("Building \"{}\"".format(game.name))

    print("Using modules: ")
    for module in game.modules:
        print("\t+ {}".format(module))


if __name__ == "__main__":
    main()

