"""
NFA to DFA Converter - Flask Backend Application
Automata Theory College Project
"""

import os
from flask import Flask, render_template, request, jsonify
from converter import NFA, NFAtoDFAConverter, simulate_dfa
from graph import generate_nfa_dot, generate_dfa_dot, render_dot_to_svg

app = Flask(__name__)

# Sample NFAs for immediate demonstration and testing
SAMPLE_NFAS = {
    "sample1": {
        "title": "Ends with '01'",
        "description": "Binary strings ending with '01'.",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["0", "1"],
        "start_state": "q0",
        "final_states": ["q2"],
        "transitions": [
            {"from": "q0", "symbol": "0", "to": ["q0", "q1"]},
            {"from": "q0", "symbol": "1", "to": ["q0"]},
            {"from": "q1", "symbol": "1", "to": ["q2"]}
        ],
        "test_strings": ["01", "001", "1101", "100", "010", ""]
    },
    "sample2": {
        "title": "Epsilon-NFA: a*b*c*",
        "description": "Language L = a*b*c* with ε-transitions.",
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
        ],
        "test_strings": ["", "a", "abc", "aabbcc", "ac", "ba", "cba"]
    },
    "sample3": {
        "title": "Contains Substring '00' or '11'",
        "description": "Binary strings containing '00' or '11'.",
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
        ],
        "test_strings": ["00", "11", "01001", "10110", "0101", ""]
    },
    "sample4": {
        "title": "Starts with 'a', Ends with 'b'",
        "description": "Strings starting with 'a' and ending with 'b' (triggers dead state ∅).",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["a", "b"],
        "start_state": "q0",
        "final_states": ["q2"],
        "transitions": [
            {"from": "q0", "symbol": "a", "to": ["q1"]},
            {"from": "q1", "symbol": "a", "to": ["q1"]},
            {"from": "q1", "symbol": "b", "to": ["q1", "q2"]}
        ],
        "test_strings": ["ab", "aab", "abbb", "b", "ba", "a", ""]
    },
    "sample5": {
        "title": "Contains Substring '01'",
        "description": "Binary strings containing substring '01'.",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["0", "1"],
        "start_state": "q0",
        "final_states": ["q2"],
        "transitions": [
            {"from": "q0", "symbol": "0", "to": ["q0", "q1"]},
            {"from": "q0", "symbol": "1", "to": ["q0"]},
            {"from": "q1", "symbol": "1", "to": ["q2"]},
            {"from": "q2", "symbol": "0", "to": ["q2"]},
            {"from": "q2", "symbol": "1", "to": ["q2"]}
        ],
        "test_strings": ["01", "001", "101", "11010", "111", "000", ""]
    },
    "sample6": {
        "title": "Even Number of 0s",
        "description": "Binary strings with an even number of 0s.",
        "states": ["q0", "q1"],
        "alphabet": ["0", "1"],
        "start_state": "q0",
        "final_states": ["q0"],
        "transitions": [
            {"from": "q0", "symbol": "0", "to": ["q1"]},
            {"from": "q0", "symbol": "1", "to": ["q0"]},
            {"from": "q1", "symbol": "0", "to": ["q0"]},
            {"from": "q1", "symbol": "1", "to": ["q1"]}
        ],
        "test_strings": ["", "00", "0000", "1", "11", "010", "0", "000", "101"]
    }
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.svg")


@app.route("/api/samples", methods=["GET"])
def get_samples():
    return jsonify(SAMPLE_NFAS)


@app.route("/api/convert", methods=["POST"])
def convert_nfa():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON payload received."}), 400

        states = data.get("states", [])
        alphabet = data.get("alphabet", [])
        start_state = data.get("start_state", "")
        final_states = data.get("final_states", [])
        transitions = data.get("transitions", [])
        include_dead_state = data.get("include_dead_state", True)

        nfa = NFA(
            states=states,
            alphabet=alphabet,
            start_state=start_state,
            final_states=final_states,
            transitions=transitions
        )

        valid, error_msg = nfa.validate()
        if not valid:
            return jsonify({"success": False, "error": error_msg}), 400

        # Generate NFA Table and Diagram
        nfa_table = nfa.get_transition_table()
        nfa_dot = generate_nfa_dot(nfa)
        nfa_svg = render_dot_to_svg(nfa_dot)

        # Convert to DFA
        converter = NFAtoDFAConverter(nfa, include_dead_state=include_dead_state)
        result = converter.convert()

        # Generate DFA Diagram
        dfa_dot = generate_dfa_dot(result["dfa"])
        dfa_svg = render_dot_to_svg(dfa_dot)

        response_data = {
            "success": True,
            "nfa": {
                "states": nfa.states,
                "alphabet": nfa.alphabet,
                "start_state": nfa.start_state,
                "final_states": nfa.final_states,
                "has_epsilon": nfa.has_epsilon,
                "table": nfa_table,
                "dot": nfa_dot,
                "svg": nfa_svg
            },
            "dfa": {
                **result["dfa"],
                "dot": dfa_dot,
                "svg": dfa_svg
            },
            "steps": result["steps"]
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"success": False, "error": f"Server processing error: {str(e)}"}), 500


@app.route("/api/test-string", methods=["POST"])
def test_string():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No payload provided."}), 400

        nfa_spec = data.get("nfa")
        dfa_spec = data.get("dfa")
        test_str = data.get("string", "")

        if not nfa_spec or not dfa_spec:
            return jsonify({"success": False, "error": "Missing NFA or DFA specification."}), 400

        # Reconstruct NFA
        nfa = NFA(
            states=nfa_spec.get("states", []),
            alphabet=nfa_spec.get("alphabet", []),
            start_state=nfa_spec.get("start_state", ""),
            final_states=nfa_spec.get("final_states", []),
            transitions=data.get("nfa_transitions", [])
        )

        nfa_sim = nfa.simulate(test_str)
        dfa_sim = simulate_dfa(dfa_spec, test_str)

        match = (nfa_sim.get("accepted") == dfa_sim.get("accepted"))

        return jsonify({
            "success": True,
            "string": test_str,
            "string_display": f'"{test_str}"' if test_str else 'ε (Empty string)',
            "match": match,
            "accepted": nfa_sim.get("accepted"),
            "nfa_result": nfa_sim,
            "dfa_result": dfa_sim
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Simulation error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting NFA to DFA Converter on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

