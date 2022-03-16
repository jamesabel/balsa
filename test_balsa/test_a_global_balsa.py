import pytest

from balsa import Balsa, get_global_balsa, get_global_config, __author__


def test_global_balsa():

    with pytest.raises(RuntimeError):
        # not yet initialized
        get_global_balsa()

    with pytest.raises(RuntimeError):
        # not yet initialized
        get_global_config()

    balsa = Balsa("test_global_balsa", __author__, is_root=False)
    balsa.init_logger()

    global_balsa = get_global_balsa()
    assert global_balsa is not None
    assert global_balsa.backup_count > 0  # just test some attribute
    global_config = get_global_config()
    assert global_config is not None
    assert global_config["author"] == __author__
