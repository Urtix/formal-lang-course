import pyformlang.cfg as pycfg


def cfg_to_weak_normal_form(cfg: pycfg.CFG) -> pycfg.CFG:
    nullable_cfg = cfg.get_nullable_symbols()

    productions = set(cfg.to_normal_form().productions)
    for var in nullable_cfg:
        var = pycfg.Variable(var.value)
        eps = [pycfg.Epsilon()]
        productions.add(pycfg.Production(var, eps))

    wcnf = pycfg.CFG(
        start_symbol=cfg.start_symbol, productions=productions
    ).remove_useless_symbols()

    return wcnf
