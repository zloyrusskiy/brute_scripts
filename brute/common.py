from electrum import simple_config, storage, wallet


def create_wallet(ks, config=None, gap_limit=1):
    if config is None:
        config = simple_config.SimpleConfig()

    db = storage.WalletDB("", manual_upgrades=False)
    db.put("keystore", ks.dump())
    db.put("gap_limit", gap_limit)
    return wallet.Standard_Wallet(db, None, config=config)
