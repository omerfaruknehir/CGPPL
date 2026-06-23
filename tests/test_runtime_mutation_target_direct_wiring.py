"""Regression contract for folding mutation-target diagnostics into runtime.py."""

from pathlib import Path

import pytest

import cgppl
import cgppl.runtime as runtime_module


@pytest.mark.xfail(reason="mutation target diagnostics are still installed through adapter modules")
def test_mutation_target_diagnostics_are_wired_directly_in_runtime():
    package_init = Path(cgppl.__file__).read_text()
    runtime_source = Path(runtime_module.__file__).read_text()

    assert "runtime_delete_target_wiring" not in package_init
    assert "runtime_annotation_target_wiring" not in package_init
    assert "install_delete_target_diagnostics" not in package_init
    assert "install_annotation_target_diagnostics" not in package_init

    expected_helpers = (
        "format_missing_delete_node_target_failure",
        "format_missing_delete_edge_target_failure",
        "format_missing_set_node_attr_target_failure",
        "format_missing_set_edge_attr_target_failure",
        "format_missing_set_node_label_target_failure",
        "format_missing_set_edge_label_target_failure",
        "format_missing_unset_node_attr_target_failure",
        "format_missing_unset_edge_attr_target_failure",
        "format_missing_unset_node_label_target_failure",
        "format_missing_unset_edge_label_target_failure",
    )
    for helper in expected_helpers:
        assert helper in runtime_source

    legacy_messages = (
        "delete node target not found",
        "delete edge target not found",
        "set node target not found",
        "set edge target not found",
        "unset node target not found",
        "unset edge target not found",
    )
    for message in legacy_messages:
        assert message not in runtime_source
