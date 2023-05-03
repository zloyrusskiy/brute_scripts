# Electrum - lightweight Bitcoin client
# Copyright (C) 2014 Thomas Voegtlin
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
from functools import partial
from itertools import permutations
from multiprocessing import Pool

import tqdm
from electrum import keystore

from brute.common import create_wallet


def find_matching_seed(new_seed_words, target_address):
    new_seed = " ".join(new_seed_words)
    seed_type = keystore.seed_type(new_seed)

    if seed_type == "segwit":
        ks = keystore.from_seed(new_seed, False)
        wallet_instance = create_wallet(ks)
        first_receiving_address = wallet_instance.get_receiving_address()

        # print(f"{new_seed} | {first_receiving_address}")

        if first_receiving_address == target_address:
            return new_seed


def main(seed_words_str, target_address):
    seed_words = seed_words_str.split()
    assert len(seed_words) == 12, "Wrong seed words count"

    with Pool() as pool:
        perms = permutations(seed_words, len(seed_words))
        partial_fn = partial(find_matching_seed, target_address=target_address)
        for result in tqdm.tqdm(pool.imap_unordered(partial_fn, perms)):
            if result:
                print(f"found it!!! {result}")
                break


if __name__ == "__main__":
    _, in_seed_words_str, in_addr = sys.argv
    main(in_seed_words_str, in_addr)
