import pathlib


def test_construction_diagnostics_are_wired_directly_in_runtime():
    package_init = pathlib.Path("src/cgppl/__init__.py").read_text()
    runtime_source = pathlib.Path("src/cgppl/runtime.py").read_text()
    adapter_path = pathlib.Path("src/cgppl/runtime_construction_wiring.py")

    assert "install_construction_diagnostics" not in package_init
    assert not adapter_path.exists()
    assert "format_add_node_failure" in runtime_source
    assert "format_add_edge_failure" in runtime_source
    assert "format_add_edge_endpoint_failure" in runtime_source
    assert "add node failed:" not in runtime_source
    assert "add edge failed:" not in runtime_source
    assert "add edge endpoint failed:" not in runtime_source
