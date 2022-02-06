#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 11:36:07 2021
"""
from pyGFeedControl import get_args, startup, main_loop, gracious_decay


def main() -> None:

    gracious_decay()

    config_src = get_args()

    config = startup(config_src)

    main_loop(config)

if __name__ == "__main__":
    main()
