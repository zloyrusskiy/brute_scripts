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
from multiprocessing.pool import Pool

import tqdm
from electrum import keystore

from brute.common import create_wallet


def find_matching_path(num_seq: list[int], seed: str, target_address: str):
    derivation_path = number_sequence_to_derivation_path(num_seq)
    ks = keystore.from_bip39_seed(seed, "", derivation_path, 'p2wpkh')
    wallet_instance = create_wallet(ks)
    first_receiving_address = wallet_instance.get_receiving_address()

    # print(" | ".join([derivation_path + '/0', first_receiving_address]))

    if first_receiving_address == target_address:
        return derivation_path


class NumberSequenceIterator:
    def __init__(self, max_value: int, max_length: int):
        self.max_value = max_value
        self.max_length = max_length
        self.current = []

    def __iter__(self):
        return self

    def __next__(self):
        self.increment_position(0)

        if len(self.current) > self.max_length:
            raise StopIteration

        return self.current

    def increment_position(self, position: int):
        if position >= len(self.current):
            self.current.append(0)
        else:
            self.current[position] += 1

            if self.current[position] > self.max_value:
                self.current[position] = 0
                self.increment_position(position + 1)


def number_sequence_to_derivation_path(sequence: list[int]) -> str:
    def format_number(number: int) -> str:
        if bool(number & 0x80000000):
            return f"{number & 0x7FFFFFFF}'"
        else:
            return str(number)

    path_elements = [format_number(number) for number in sequence]
    path_part = "/".join(path_elements)
    return f'm/{path_part}'


def main(seed_words_str, target_address):
    seed_words = seed_words_str.split()
    assert len(seed_words) == 12, "Wrong seed words count"

    with Pool() as pool:
        iterator = NumberSequenceIterator(2 ** 32 - 1, 255)
        partial_fn = partial(find_matching_path, seed=seed_words_str, target_address=target_address)
        for result in tqdm.tqdm(pool.imap_unordered(partial_fn, iterator)):
            if result:
                print(f"found it!!! {result}")
                break


if __name__ == "__main__":
    _, in_seed_words_str, in_addr = sys.argv
    main(in_seed_words_str, in_addr)
