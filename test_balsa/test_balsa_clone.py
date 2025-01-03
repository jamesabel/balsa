from balsa import balsa_clone, Balsa, __author__


class CustomBalsa(Balsa):
    pass


test_config = {"name": "test_config", "author": "me", "verbose": False, "gui": False, "is_root": False}


def test_balsa_clone_no_parent():

    balsa = balsa_clone(test_config, "test_balsa_clone_no_parent")
    balsa.init_logger()
    balsa.log.error("yes parent")

    balsa.remove()


def test_balsa_clone_parent():

    my_balsa = Balsa("test_balsa_clone_parent_a", __author__)
    my_balsa_config = my_balsa.config_as_dict()

    new_balsa = balsa_clone(my_balsa_config, "test_balsa_clone_parent_b", my_balsa)
    new_balsa.init_logger()
    new_balsa.log.error("error")

    my_balsa.remove()
    new_balsa.remove()
