"""Exact cubic amplitude-product circuit: Classiq Qmod model, not a QSVT run.

Default execution only creates and parses models locally. --cloud explicitly
requests synthesis plus noiseless Classiq simulator state vectors and requires
an already authenticated Classiq SDK session. It never selects QPU hardware.
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

import numpy as np
from classiq import (
    CX, S, Z, Const, Output, QArray, QBit, QNum,
    allocate, calculate_state_vector, create_model, hadamard_transform,
    prepare_amplitudes, qfunc, synthesize,
)


def fixture_amplitudes(fixture):
    if fixture == "real":
        return np.array([1, 2, -1, 0], dtype=complex) / np.sqrt(6)
    if fixture == "complex":
        return np.array([1, 1j, -1, 0], dtype=complex) / np.sqrt(3)
    raise ValueError("fixture must be real or complex")


def build_model(fixture="real", mode="uniform"):
    if mode not in {"uniform", "importance"}:
        raise ValueError("mode must be uniform or importance")
    x = fixture_amplitudes(fixture)
    # prepare_amplitudes accepts REAL amplitudes. The complex fixture is
    # prepared with nonnegative amplitudes followed by explicit S/Z phases.
    amplitudes = (x.real if fixture == "real" else np.abs(x)).tolist()

    @qfunc
    def load_input(out: Output[QArray[QBit]]):
        prepare_amplitudes(amplitudes=amplitudes, bound=0.0, out=out)
        if fixture == "complex":
            # Qmod index 0 carries weight 1; index 1 carries weight 2.
            S(out[0])
            Z(out[1])

    @qfunc
    def diagonal_filter(address: Const[QArray[QBit]],
                        work: Output[QArray[QBit]]):
        load_input(work)
        CX(ctrl=address[0], target=work[0])
        CX(ctrl=address[1], target=work[1])

    if mode == "uniform":
        @qfunc
        def main(address: Output[QNum[2]], work0: Output[QNum[2]],
                 work1: Output[QNum[2]], work2: Output[QNum[2]]):
            allocate(2, address)
            hadamard_transform(address)
            diagonal_filter(address, work0)
            diagonal_filter(address, work1)
            diagonal_filter(address, work2)
    else:
        @qfunc
        def main(address: Output[QNum[2]], work0: Output[QNum[2]],
                 work1: Output[QNum[2]]):
            load_input(address)
            diagonal_filter(address, work0)
            diagonal_filter(address, work1)
    return create_model(main)


def reference(fixture, mode):
    x = fixture_amplitudes(fixture)
    branch = x**3 / (2 if mode == "uniform" else 1)
    success = float(np.vdot(branch, branch).real)
    target = x**3 / np.linalg.norm(x**3)
    return branch, success, target


def read_register_integer(value):
    # pandas.iterrows can coerce integer columns to complex when the row also
    # contains a complex amplitude. Reject a genuinely non-integral value.
    number = complex(value)
    if abs(number.imag) > 1e-12 or not np.isclose(number.real, round(number.real), atol=1e-12):
        raise ValueError("Register column is not an integer")
    return int(round(number.real))


def postselect_dataframe(frame, fixture, mode):
    """Use named QNum outputs; do not assume physical qubit allocation order."""
    work_names = ["work0", "work1"] + (["work2"] if mode == "uniform" else [])
    required = ["address", "amplitude", *work_names]
    if any(name not in frame.columns for name in required):
        raise ValueError("State-vector DataFrame is missing named register columns")
    branch = np.zeros(4, dtype=complex)
    for _, row in frame.iterrows():
        if all(read_register_integer(row[name]) == 0 for name in work_names):
            address = read_register_integer(row["address"])
            if not 0 <= address < 4:
                raise ValueError("Unexpected address value")
            branch[address] += complex(row["amplitude"])
    success = float(np.vdot(branch, branch).real)
    if success <= 0:
        raise ValueError("No retained branch")
    target = reference(fixture, mode)[2]
    conditioned = branch / np.sqrt(success)
    fidelity = float(abs(np.vdot(target, conditioned))**2)
    expected_success = reference(fixture, mode)[1]
    if not np.isclose(success, expected_success, atol=1e-9):
        raise AssertionError("Classiq simulator success probability mismatch")
    if not np.isclose(fidelity, 1, atol=1e-9):
        raise AssertionError("Classiq simulator conditional-state fidelity mismatch")
    return {"success_probability": success, "conditional_fidelity": fidelity,
            "conditional_amplitudes": [[float(z.real), float(z.imag)] for z in conditioned]}


def strip_debug_metadata(serialized_model):
    """Remove non-executable SDK source/debug metadata before sharing models."""
    def clean(value):
        if isinstance(value, dict):
            return {key: None if key in {
                "source_ref", "back_ref", "compressed_debug_info"
            } else clean(item) for key, item in value.items()}
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value
    return json.dumps(clean(json.loads(str(serialized_model))), separators=(",", ":"))


def validate_local(output):
    output.mkdir(parents=True, exist_ok=True)
    records = []
    from classiq.interface.model.model import Model
    for fixture in ["real", "complex"]:
        for mode in ["uniform", "importance"]:
            model = build_model(fixture, mode)
            text = strip_debug_metadata(model)
            parsed = json.loads(text)
            Model.model_validate_json(text)
            destination = output / f"{fixture}-{mode}.qmod.json"
            destination.write_text(text + "\n", encoding="utf-8")
            branch, success, target = reference(fixture, mode)
            records.append({
                "fixture": fixture, "mode": mode,
                "declared_address_and_work_qubits": 8 if mode == "uniform" else 6,
                "total_forward_state_preparation_calls": 3,
                "model_json_parse": "passed", "sdk_model_schema_validation": "passed",
                "serialized_model_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "model_top_level_keys": list(parsed),
                "reference_success_probability": success,
                "reference_target": [[float(z.real), float(z.imag)] for z in target],
                "reference_scope": "Classical exact branch algebra; not Classiq cloud simulation",
                "synthesis_status": "not_run", "state_vector_status": "not_run",
                "qpu_status": "not_run", "qsvt_status": "not_used",
            })
    return {"classiq_version": importlib.metadata.version("classiq"),
            "validation_scope": "Local Qmod model creation, JSON parse and SDK schema validation only",
            "records": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("classiq-models"))
    parser.add_argument("--cloud", action="store_true",
                        help="Synthesize and request Classiq simulator state vectors with an existing SDK login")
    args = parser.parse_args()
    report = validate_local(args.output)
    if args.cloud:
        for record in report["records"]:
            model = build_model(record["fixture"], record["mode"])
            program = synthesize(model)
            frame = calculate_state_vector(program, backend="simulator",
                                           amplitude_threshold=0.0, verbose=False)
            record.update(postselect_dataframe(frame, record["fixture"], record["mode"]))
            record["synthesis_status"] = "passed"
            record["state_vector_status"] = "passed: noiseless Classiq simulator"
    (args.output / "classiq-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"classiq_version": report["classiq_version"],
                      "models_validated": len(report["records"]),
                      "cloud_requested": args.cloud,
                      "all_model_schema_checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
