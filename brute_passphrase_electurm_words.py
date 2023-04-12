import itertools
import sys
from functools import partial
from multiprocessing import Pool

import tqdm
from electrum import keystore
from electrum.mnemonic import Wordlist

from brute.common import create_wallet


def find_matching_seed(passphrase, seed, target_address):
    passphrase_str = " ".join(passphrase)
    ks = keystore.from_seed(seed, passphrase_str)
    wallet_instance = create_wallet(ks)
    first_receiving_address = wallet_instance.get_receiving_address()

    # print(" | ".join([passphrase_str, first_receiving_address]))

    if first_receiving_address == target_address:
        return passphrase_str


def main(seed_words_str, target_address):
    seed_words = seed_words_str.split()
    assert len(seed_words) == 12, "Wrong seed words count"

    wordlist = Wordlist.from_file("english.txt")

    with Pool() as pool:
        perms = itertools.chain.from_iterable(
            itertools.permutations(wordlist, n + 1) for n in range(12)
        )
        partial_fn = partial(find_matching_seed, seed=seed_words_str, target_address=target_address)
        for result in tqdm.tqdm(pool.imap_unordered(partial_fn, perms)):
            if result:
                print(f"found it!!! {result}")
                break


if __name__ == "__main__":
    _, in_seed_words_str, in_addr = sys.argv
    main(in_seed_words_str, in_addr)
