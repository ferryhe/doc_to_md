from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_module():
    script_path = Path(__file__).resolve().parents[1] / "tools" / "run_single_engine_benchmark.py"
    spec = importlib.util.spec_from_file_location("run_single_engine_benchmark", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_run_single_engine_benchmark_supports_remote_engines() -> None:
    module = _load_module()

    assert "mistral" in module.ENGINE_SPECS
    assert "mathpix" in module.ENGINE_SPECS
    assert "deepseekocr" in module.ENGINE_SPECS
