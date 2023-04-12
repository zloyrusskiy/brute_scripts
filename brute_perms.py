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
