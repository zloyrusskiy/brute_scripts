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
from multiprocessing import Pool
from electrum import keystore, bitcoin

MAX_ADDR_INDEX = 2 ** 31 - 1


def find_matching_address(index: int, ks: keystore.BIP32_KeyStore):
    addr_pub = ks.derive_pubkey(0, index)
    addr = bitcoin.public_key_to_p2wpkh(addr_pub)
    return index, addr


def main(seed_words_str: str, start_index: int):
    assert len(seed_words_str.split()) == 12, "Wrong seed words count"

    ks = keystore.from_seed(seed_words_str, "")

    with Pool() as pool:
        addr_range = range(start_index, MAX_ADDR_INDEX + 1)
        partial_fn = partial(find_matching_address, ks=ks)
        for (ind, addr) in pool.imap_unordered(partial_fn, addr_range, chunksize=1000):
            sys.stdout.write(f'{ind}:{addr}\n')


if __name__ == "__main__":
    _, in_seed_words_str, start_index_str = sys.argv
    main(in_seed_words_str, int(start_index_str))
