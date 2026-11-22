"""
Automated Comprehensive Test Suite for NFA to DFA Converter
Automata Theory Verification
"""

import sys
from converter import NFA, NFAtoDFAConverter, simulate_dfa
from graph import generate_nfa_dot, generate_dfa_dot, render_dot_to_svg
from app import app


def test_nfa_case(name, spec, test_strings):
    print(f"\n=======================================================")
    print(f"Testing {name}")
    print(f"=======================================================")
    nfa = NFA(
        states=spec["states"],
        alphabet=spec["alphabet"],
        start_state=spec["start_state"],
        final_states=spec["final_states"],
        transitions=spec["transitions"]
    )

    valid, err = nfa.validate()
    assert valid, f"Validation failed: {err}"
    print(f"[PASS] NFA validation passed (has_epsilon={nfa.has_epsilon})")

    converter = NFAtoDFAConverter(nfa, include_dead_state=spec.get("include_dead_state", True))
    result = converter.convert()
    assert result["success"], "Conversion failed"
    dfa = result["dfa"]

    print(f"[PASS] Subset construction completed: {len(dfa['state_objects'])} DFA states generated.")
    for s in dfa["state_objects"]:
        flag = []
        if s["is_start"]: flag.append("START")
        if s["is_final"]: flag.append("FINAL")
        if s.get("is_dead"): flag.append("DEAD")
        print(f"   State {s['id']}: name={s['name']}, subset={s['nfa_subset']} {'[' + ', '.join(flag) + ']' if flag else ''}")

    # Test diagrams
    nfa_dot = generate_nfa_dot(nfa)
    dfa_dot = generate_dfa_dot(dfa)
    nfa_svg = render_dot_to_svg(nfa_dot)
    dfa_svg = render_dot_to_svg(dfa_dot)
    assert nfa_svg and "<svg" in nfa_svg, "NFA SVG generation failed"
    assert dfa_svg and "<svg" in dfa_svg, "DFA SVG generation failed"
    print(f"[PASS] Graphviz SVG diagrams generated successfully (NFA: {len(nfa_svg)} bytes, DFA: {len(dfa_svg)} bytes)")

    # Test string simulations
    all_match = True
    for s in test_strings:
        nfa_res = nfa.simulate(s)
        dfa_res = simulate_dfa(dfa, s)
        nfa_acc = nfa_res["accepted"]
        dfa_acc = dfa_res["accepted"]
        match = (nfa_acc == dfa_acc)
        status_str = "ACCEPTED" if nfa_acc else "REJECTED"
        disp_s = f'"{s}"' if s else "ε (empty)"
        print(f"   Input {disp_s.ljust(15)} -> NFA: {str(nfa_acc).ljust(5)} | DFA: {str(dfa_acc).ljust(5)} | Match: {match} ({status_str})")
        if not match:
            all_match = False

    assert all_match, f"Equivalence failure for {name}!"
    print(f"[PASS] PERFECT EQUIVALENCE: Both machines gave identical results on all {len(test_strings)} test strings.")


def run_all_tests():
    # Case 1: Standard NFA (Ends with '01')
    test_nfa_case(
        "NFA 1: Standard NFA (Strings ending in '01')",
        {
            "states": ["q0", "q1", "q2"],
            "alphabet": ["0", "1"],
            "start_state": "q0",
            "final_states": ["q2"],
            "transitions": [
                {"from": "q0", "symbol": "0", "to": ["q0", "q1"]},
                {"from": "q0", "symbol": "1", "to": ["q0"]},
                {"from": "q1", "symbol": "1", "to": ["q2"]}
            ]
        },
        ["01", "001", "101", "11101", "00001", "0", "1", "00", "010", "110", ""]
    )

    # Case 2: Epsilon NFA (Language a*b*c*)
    test_nfa_case(
        "NFA 2: Epsilon-NFA (Language a*b*c*)",
        {
            "states": ["q0", "q1", "q2"],
            "alphabet": ["a", "b", "c"],
            "start_state": "q0",
            "final_states": ["q2"],
            "transitions": [
                {"from": "q0", "symbol": "a", "to": ["q0"]},
                {"from": "q0", "symbol": "ε", "to": ["q1"]},
                {"from": "q1", "symbol": "b", "to": ["q1"]},
                {"from": "q1", "symbol": "ε", "to": ["q2"]},
                {"from": "q2", "symbol": "c", "to": ["q2"]}
            ]
        },
        ["", "a", "b", "c", "ab", "bc", "ac", "abc", "aaabbbccc", "ba", "ca", "cb", "cba", "bca", "aabac"]
    )

    # Case 3: Substring '00' or '11'
    test_nfa_case(
        "NFA 3: Substring '00' or '11'",
        {
            "states": ["q0", "q1", "q2", "q3", "q4"],
            "alphabet": ["0", "1"],
            "start_state": "q0",
            "final_states": ["q2", "q4"],
            "transitions": [
                {"from": "q0", "symbol": "0", "to": ["q0", "q1"]},
                {"from": "q0", "symbol": "1", "to": ["q0", "q3"]},
                {"from": "q1", "symbol": "0", "to": ["q2"]},
                {"from": "q3", "symbol": "1", "to": ["q4"]},
                {"from": "q2", "symbol": "0", "to": ["q2"]},
                {"from": "q2", "symbol": "1", "to": ["q2"]},
                {"from": "q4", "symbol": "0", "to": ["q4"]},
                {"from": "q4", "symbol": "1", "to": ["q4"]}
            ]
        },
        ["00", "11", "000", "111", "01001", "10110", "", "0", "1", "01", "10", "0101", "1010"]
    )

    # Case 4: NFA with Dead State (Starts with 'a' and ends with 'b')
    test_nfa_case(
        "NFA 4: Starts with 'a' and ends with 'b' (Dead State Required)",
        {
            "states": ["q0", "q1", "q2"],
            "alphabet": ["a", "b"],
            "start_state": "q0",
            "final_states": ["q2"],
            "transitions": [
                {"from": "q0", "symbol": "a", "to": ["q1"]},
                {"from": "q1", "symbol": "a", "to": ["q1"]},
                {"from": "q1", "symbol": "b", "to": ["q1", "q2"]}
            ],
            "include_dead_state": True
        },
        ["ab", "aab", "abb", "abbb", "aaabb", "b", "ba", "a", "bab", ""]
    )

    # Test Flask API client
    print(f"\n=======================================================")
    print("Testing Flask Web Endpoints")
    print(f"=======================================================")
    client = app.test_client()
    
    # GET /
    res = client.get("/")
    assert res.status_code == 200
    assert b"NFA to DFA Converter" in res.data
    print("[PASS] GET / returned 200 OK with correct heading.")

    # GET /api/samples
    res = client.get("/api/samples")
    assert res.status_code == 200
    samples = res.get_json()
    assert "sample1" in samples and "sample2" in samples
    print(f"[PASS] GET /api/samples returned {len(samples)} valid presets.")

    # POST /api/convert
    sample1 = samples["sample1"]
    res = client.post("/api/convert", json=sample1)
    assert res.status_code == 200
    conv_data = res.get_json()
    assert conv_data["success"] is True
    assert "nfa" in conv_data and "dfa" in conv_data and "steps" in conv_data
    assert conv_data["nfa"]["svg"] is not None
    assert conv_data["dfa"]["svg"] is not None
    print("[PASS] POST /api/convert executed successfully and returned diagrams & steps.")

    # POST /api/test-string
    test_payload = {
        "nfa": conv_data["nfa"],
        "dfa": conv_data["dfa"],
        "nfa_transitions": sample1["transitions"],
        "string": "01"
    }
    res = client.post("/api/test-string", json=test_payload)
    assert res.status_code == 200
    sim_data = res.get_json()
    assert sim_data["success"] is True
    assert sim_data["accepted"] is True
    assert sim_data["match"] is True
    print("[PASS] POST /api/test-string returned matching acceptance and simulation traces.")

    print("\n[OK] ALL UNIT AND INTEGRATION TESTS PASSED WITH 100% SUCCESS!\n")


if __name__ == "__main__":
    run_all_tests()

