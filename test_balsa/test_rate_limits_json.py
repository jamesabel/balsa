import json
import logging

from ismain import is_main

from balsa import Balsa, DialogBoxHandler, balsa_clone, __author__


# Test created by AI (Claude Code)
def test_rate_limits_json_round_trip():
    application_name = "test_rate_limits_json_round_trip"

    balsa = Balsa(application_name, __author__, is_root=False)
    config = balsa.config_as_dict()

    round_tripped_config = json.loads(json.dumps(config))
    assert round_tripped_config == config  # the exported config must survive a JSON round-trip exactly

    clone = balsa_clone(round_tripped_config, "clone")
    assert all(isinstance(level, int) for level in clone.rate_limits)
    assert logging.ERROR in clone.rate_limits  # DialogBoxHandler looks up record.levelno, which is an int


# Test created by AI (Claude Code)
def test_rate_limits_int_keyed_config_backward_compatibility():
    application_name = "test_rate_limits_int_keyed_config_backward_compatibility"

    balsa = Balsa(application_name, __author__, is_root=False)
    config = balsa.config_as_dict()
    # pre-0.24 config_as_dict() exported int keys - such configs (e.g. old pickles) must still work
    config["rate_limits"] = {int(level): limits for level, limits in config["rate_limits"].items()}

    clone = balsa_clone(config, "clone")
    assert all(isinstance(level, int) for level in clone.rate_limits)
    assert logging.ERROR in clone.rate_limits


# Test created by AI (Claude Code)
def test_rate_limits_export_has_str_keys():
    application_name = "test_rate_limits_export_has_str_keys"

    balsa = Balsa(application_name, __author__, is_root=False)
    config = balsa.config_as_dict()
    assert len(config["rate_limits"]) > 0
    assert all(isinstance(level, str) for level in config["rate_limits"])


# Test created by AI (Claude Code)
def test_rate_limits_direct_construction_with_str_keys():
    application_name = "test_rate_limits_direct_construction_with_str_keys"

    balsa = Balsa(application_name, __author__, is_root=False, rate_limits={"40": {"count": 1, "time": 1.0}})
    assert balsa.rate_limits == {40: {"count": 1, "time": 1.0}}


# Test created by AI (Claude Code)
def test_rate_limits_live_mutation():
    application_name = "test_rate_limits_live_mutation"

    balsa = Balsa(application_name, __author__, is_root=False)
    balsa.rate_limits[logging.WARNING]["count"] = 4  # existing callers mutate the live attribute by int level
    assert balsa.rate_limits[logging.WARNING]["count"] == 4


# Test created by AI (Claude Code)
def test_dialog_box_handler_normalizes_str_keys():
    handler = DialogBoxHandler({"40": {"count": 1, "time": 1.0}})
    assert handler.rate_limits == {40: {"count": 1, "time": 1.0}}


if is_main():
    test_rate_limits_json_round_trip()
    test_rate_limits_int_keyed_config_backward_compatibility()
    test_rate_limits_export_has_str_keys()
    test_rate_limits_direct_construction_with_str_keys()
    test_rate_limits_live_mutation()
    test_dialog_box_handler_normalizes_str_keys()
