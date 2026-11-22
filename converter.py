"""
NFA to DFA Converter
Automata Theory - Subset Construction Engine with Epsilon Transitions
"""

from collections import deque
from typing import Dict, List, Set, Tuple, Any, Optional

EPSILON_ALIASES = {"", "ε", "eps", "epsilon", "e", "lambda", "λ", "E"}


def is_epsilon(sym: str) -> bool:
    return sym in EPSILON_ALIASES


def canonical_set_name(s: Set[str]) -> str:
    """Format a set of state names cleanly: e.g. {q0, q1} or ∅"""
    if not s:
        return "∅"
    sorted_items = sorted(list(s))
    return "{" + ", ".join(sorted_items) + "}"


class NFA:
    def __init__(
        self,
        states: List[str],
        alphabet: List[str],
        start_state: str,
        final_states: List[str],
        transitions: List[Dict[str, Any]],
    ):
        self.states = [s.strip() for s in states if s.strip()]
        # Filter alphabet so epsilon is not included in alphabet
        self.alphabet = [a.strip() for a in alphabet if a.strip() and not is_epsilon(a.strip())]
        # Preserve order while deduplicating
        self.alphabet = list(dict.fromkeys(self.alphabet))
        self.start_state = start_state.strip()
        self.final_states = [f.strip() for f in final_states if f.strip()]
        
        # Build transitions dict: delta[state][symbol] = set(target_states)
        # symbol 'ε' is used internally for epsilon
        self.transitions: Dict[str, Dict[str, Set[str]]] = {s: {} for s in self.states}
        self.has_epsilon = False

        for t in transitions:
            from_state = t.get("from", "").strip()
            sym = t.get("symbol", "").strip()
            to_states = t.get("to", [])
            if isinstance(to_states, str):
                to_states = [s.strip() for s in to_states.split(",") if s.strip()]
            
            if is_epsilon(sym):
                norm_sym = "ε"
                self.has_epsilon = True
            else:
                norm_sym = sym
            
            if from_state in self.transitions:
                if norm_sym not in self.transitions[from_state]:
                    self.transitions[from_state][norm_sym] = set()
                for target in to_states:
                    target = target.strip()
                    if target:
                        self.transitions[from_state][norm_sym].add(target)

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate the NFA inputs."""
        if not self.states:
            return False, "States list cannot be empty."
        if not self.alphabet:
            return False, "Alphabet cannot be empty."
        if not self.start_state:
            return False, "Start state must be specified."
        if self.start_state not in self.states:
            return False, f"Start state '{self.start_state}' is not in the set of states."
        for fs in self.final_states:
            if fs not in self.states:
                return False, f"Final state '{fs}' is not in the set of states."
        
        for s, sym_map in self.transitions.items():
            if s not in self.states:
                return False, f"Transition from unknown state '{s}'."
            for sym, targets in sym_map.items():
                if sym != "ε" and sym not in self.alphabet:
                    return False, f"Unknown transition symbol '{sym}' (not in alphabet {self.alphabet})."
                for target in targets:
                    if target not in self.states:
                        return False, f"Transition from '{s}' on '{sym}' leads to unknown state '{target}'."
        return True, None

    def epsilon_closure(self, states_set: Set[str]) -> Set[str]:
        """Compute the epsilon closure of a set of states using DFS/BFS."""
        closure = set(states_set)
        stack = list(states_set)
        while stack:
            curr = stack.pop()
            eps_targets = self.transitions.get(curr, {}).get("ε", set())
            for target in eps_targets:
                if target not in closure:
                    closure.add(target)
                    stack.append(target)
        return closure

    def move(self, states_set: Set[str], symbol: str) -> Set[str]:
        """Compute the set of states reachable on `symbol` from `states_set`."""
        reachable = set()
        for s in states_set:
            reachable.update(self.transitions.get(s, {}).get(symbol, set()))
        return reachable

    def simulate(self, input_string: str) -> Dict[str, Any]:
        """Simulate string processing on the NFA."""
        # Initial active states
        current_active = self.epsilon_closure({self.start_state})
        trace = [{
            "step": 0,
            "char": "ε-closure(start)",
            "states": sorted(list(current_active)),
            "display_states": canonical_set_name(current_active),
            "explanation": f"Initial state {self.start_state} with ε-closure -> {canonical_set_name(current_active)}"
        }]

        for i, char in enumerate(input_string, 1):
            if char not in self.alphabet:
                return {
                    "accepted": False,
                    "error": f"Symbol '{char}' not in alphabet.",
                    "trace": trace,
                    "final_states": sorted(list(current_active))
                }
            
            moved = self.move(current_active, char)
            next_active = self.epsilon_closure(moved)
            
            trace.append({
                "step": i,
                "char": char,
                "moved_before_closure": sorted(list(moved)),
                "states": sorted(list(next_active)),
                "display_states": canonical_set_name(next_active),
                "explanation": f"On symbol '{char}': move({canonical_set_name(current_active)}, '{char}') = {canonical_set_name(moved)}, ε-closure = {canonical_set_name(next_active)}"
            })
            current_active = next_active

        is_accepted = bool(current_active & set(self.final_states))
        return {
            "accepted": is_accepted,
            "trace": trace,
            "final_states": sorted(list(current_active)),
            "accepted_by": sorted(list(current_active & set(self.final_states)))
        }

    def get_transition_table(self) -> Dict[str, Any]:
        """Generate formatted transition table for the NFA."""
        headers = ["State"] + self.alphabet
        if self.has_epsilon:
            headers.append("ε")
        
        rows = []
        for s in self.states:
            is_start = (s == self.start_state)
            is_final = (s in self.final_states)
            prefix = ""
            if is_start and is_final:
                prefix = "→ *"
            elif is_start:
                prefix = "→ "
            elif is_final:
                prefix = "* "

            row_data = {
                "state": s,
                "display_state": f"{prefix}{s}",
                "is_start": is_start,
                "is_final": is_final,
                "transitions": {}
            }
            for sym in self.alphabet:
                targets = self.transitions.get(s, {}).get(sym, set())
                row_data["transitions"][sym] = canonical_set_name(targets)
            if self.has_epsilon:
                eps_targets = self.transitions.get(s, {}).get("ε", set())
                row_data["transitions"]["ε"] = canonical_set_name(eps_targets)
            rows.append(row_data)
        
        return {
            "headers": headers,
            "rows": rows,
            "has_epsilon": self.has_epsilon
        }


class NFAtoDFAConverter:
    def __init__(self, nfa: NFA, include_dead_state: bool = True):
        self.nfa = nfa
        self.include_dead_state = include_dead_state

    def convert(self) -> Dict[str, Any]:
        """Execute the subset construction algorithm and return detailed steps and resulting DFA."""
        steps = []
        
        # Step 1: Epsilon closures of individual states
        eps_closures = {}
        for s in self.nfa.states:
            closure = self.nfa.epsilon_closure({s})
            eps_closures[s] = sorted(list(closure))
        
        steps.append({
            "step_number": 1,
            "title": "Calculate Epsilon-Closures of All NFA States",
            "description": "The ε-closure of a state q is the set of all states reachable from q by following zero or more ε-transitions.",
            "data": [
                {
                    "state": s,
                    "closure": eps_closures[s],
                    "display": f"ε-closure({s}) = {canonical_set_name(set(eps_closures[s]))}"
                }
                for s in self.nfa.states
            ]
        })

        # Step 2: Initial DFA state
        start_set = self.nfa.epsilon_closure({self.nfa.start_state})
        start_frozenset = frozenset(start_set)
        
        # Mapping from frozenset of NFA states -> DFA state info
        state_counter = 0
        dfa_states_map: Dict[frozenset, Dict[str, Any]] = {}

        def get_or_create_state_id(fset: frozenset, is_dead: bool = False) -> str:
            nonlocal state_counter
            if fset not in dfa_states_map:
                if is_dead or len(fset) == 0:
                    state_id = "DEAD"
                    display_name = "∅"
                else:
                    state_id = f"q{state_counter}"
                    display_name = canonical_set_name(set(fset))
                    state_counter += 1
                
                dfa_states_map[fset] = {
                    "id": state_id,
                    "name": display_name,
                    "nfa_subset": sorted(list(fset)),
                    "is_start": (fset == start_frozenset),
                    "is_final": bool(set(fset) & set(self.nfa.final_states)),
                    "is_dead": is_dead or len(fset) == 0
                }
            return dfa_states_map[fset]["id"]

        initial_id = get_or_create_state_id(start_frozenset)
        initial_name = dfa_states_map[start_frozenset]["name"]
        
        steps.append({
            "step_number": 2,
            "title": "Determine Initial DFA State",
            "description": f"The initial state of the DFA is the ε-closure of the NFA's start state '{self.nfa.start_state}'.",
            "initial_state_id": initial_id,
            "initial_state_name": initial_name,
            "subset": sorted(list(start_set)),
            "formula": f"DFA Start State {initial_id} = ε-closure({{{self.nfa.start_state}}}) = {initial_name}"
        })

        # Step 3: Iterative Subset Construction
        queue = deque([start_frozenset])
        visited = set()
        dfa_transitions: List[Dict[str, Any]] = []
        construction_table_logs: List[Dict[str, Any]] = []

        dead_state_needed = False
        dead_frozenset = frozenset()

        while queue:
            curr_fset = queue.popleft()
            if curr_fset in visited:
                continue
            visited.add(curr_fset)
            
            curr_info = dfa_states_map[curr_fset]
            curr_name = curr_info["name"]
            curr_id = curr_info["id"]

            log_entry = {
                "dfa_state_id": curr_id,
                "dfa_state_name": curr_name,
                "nfa_subset": sorted(list(curr_fset)),
                "transitions": {}
            }

            for sym in self.nfa.alphabet:
                # Compute move
                moved = self.nfa.move(set(curr_fset), sym)
                # Compute ε-closure of move
                closure = self.nfa.epsilon_closure(moved)
                closure_fset = frozenset(closure)

                if len(closure) == 0:
                    if self.include_dead_state:
                        dead_state_needed = True
                        target_id = get_or_create_state_id(dead_frozenset, is_dead=True)
                        target_info = dfa_states_map[dead_frozenset]
                        dfa_transitions.append({
                            "from_id": curr_id,
                            "from_name": curr_name,
                            "symbol": sym,
                            "to_id": target_id,
                            "to_name": target_info["name"]
                        })
                        log_entry["transitions"][sym] = {
                            "move": "∅",
                            "closure": "∅",
                            "to_state_id": target_id,
                            "to_state_name": target_info["name"],
                            "is_new": False
                        }
                    else:
                        log_entry["transitions"][sym] = {
                            "move": "∅",
                            "closure": "∅",
                            "to_state_id": None,
                            "to_state_name": "∅ (undefined)",
                            "is_new": False
                        }
                else:
                    is_new = (closure_fset not in dfa_states_map)
                    target_id = get_or_create_state_id(closure_fset)
                    target_info = dfa_states_map[closure_fset]
                    if closure_fset not in visited and closure_fset not in queue:
                        queue.append(closure_fset)

                    dfa_transitions.append({
                        "from_id": curr_id,
                        "from_name": curr_name,
                        "symbol": sym,
                        "to_id": target_id,
                        "to_name": target_info["name"]
                    })

                    log_entry["transitions"][sym] = {
                        "move": canonical_set_name(moved),
                        "closure": target_info["name"],
                        "to_state_id": target_id,
                        "to_state_name": target_info["name"],
                        "is_new": is_new
                    }

            construction_table_logs.append(log_entry)

        # Handle Dead State self-loops if included and referenced
        if dead_state_needed and self.include_dead_state:
            dead_info = dfa_states_map[dead_frozenset]
            for sym in self.nfa.alphabet:
                dfa_transitions.append({
                    "from_id": dead_info["id"],
                    "from_name": dead_info["name"],
                    "symbol": sym,
                    "to_id": dead_info["id"],
                    "to_name": dead_info["name"]
                })
            construction_table_logs.append({
                "dfa_state_id": dead_info["id"],
                "dfa_state_name": dead_info["name"],
                "nfa_subset": [],
                "transitions": {
                    sym: {
                        "move": "∅",
                        "closure": "∅",
                        "to_state_id": dead_info["id"],
                        "to_state_name": dead_info["name"],
                        "is_new": False
                    }
                    for sym in self.nfa.alphabet
                }
            })

        steps.append({
            "step_number": 3,
            "title": "Compute Transitions for Reachable Subsets",
            "description": "For each DFA subset S and input symbol a, compute move(S, a) = ∪ δ(q, a) for q ∈ S, then apply ε-closure.",
            "logs": construction_table_logs
        })

        # Step 4: Identify Final States
        final_dfa_states = [s for s in dfa_states_map.values() if s["is_final"]]
        non_final_dfa_states = [s for s in dfa_states_map.values() if not s["is_final"]]

        steps.append({
            "step_number": 4,
            "title": "Identify Accepting/Final DFA States",
            "description": f"Any DFA state whose subset contains at least one NFA final state ({', '.join(self.nfa.final_states)}) is marked as accepting in the DFA.",
            "final_states": [
                {
                    "id": s["id"],
                    "name": s["name"],
                    "contains_final": [q for q in s["nfa_subset"] if q in self.nfa.final_states]
                }
                for s in final_dfa_states
            ],
            "non_final_states": [
                {
                    "id": s["id"],
                    "name": s["name"]
                }
                for s in non_final_dfa_states
            ]
        })

        # Step 5: Summary
        steps.append({
            "step_number": 5,
            "title": "Conversion Complete",
            "description": f"Successfully constructed equivalent DFA with {len(dfa_states_map)} states and {len(dfa_transitions)} transitions.",
            "total_states": len(dfa_states_map),
            "total_transitions": len(dfa_transitions),
            "dead_state_included": dead_state_needed and self.include_dead_state
        })

        # Format DFA transition table
        dfa_table = self._build_dfa_table(list(dfa_states_map.values()), dfa_transitions)

        # Build DFA object structure
        all_dfa_states = list(dfa_states_map.values())
        
        return {
            "success": True,
            "steps": steps,
            "dfa": {
                "states": [s["name"] for s in all_dfa_states],
                "state_ids": [s["id"] for s in all_dfa_states],
                "state_objects": all_dfa_states,
                "alphabet": self.nfa.alphabet,
                "start_state_id": initial_id,
                "start_state_name": initial_name,
                "final_state_ids": [s["id"] for s in final_dfa_states],
                "final_state_names": [s["name"] for s in final_dfa_states],
                "transitions": dfa_transitions,
                "table": dfa_table
            }
        }

    def _build_dfa_table(self, states: List[Dict[str, Any]], transitions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a neat table data structure for the DFA."""
        headers = ["DFA State", "NFA Subset"] + self.nfa.alphabet + ["Accepting?"]
        
        # Pre-index transitions: trans_map[(from_id, symbol)] = to_name
        trans_map = {}
        for t in transitions:
            trans_map[(t["from_id"], t["symbol"])] = t["to_name"]

        rows = []
        for s in states:
            prefix = ""
            if s["is_start"] and s["is_final"]:
                prefix = "→ *"
            elif s["is_start"]:
                prefix = "→ "
            elif s["is_final"]:
                prefix = "* "

            row_data = {
                "id": s["id"],
                "name": s["name"],
                "display_name": f"{prefix}{s['name']}",
                "nfa_subset": canonical_set_name(set(s["nfa_subset"])),
                "is_start": s["is_start"],
                "is_final": s["is_final"],
                "is_dead": s.get("is_dead", False),
                "transitions": {}
            }
            for sym in self.nfa.alphabet:
                target = trans_map.get((s["id"], sym), "∅")
                row_data["transitions"][sym] = target
            rows.append(row_data)

        return {
            "headers": headers,
            "rows": rows
        }


def simulate_dfa(dfa_data: Dict[str, Any], input_string: str) -> Dict[str, Any]:
    """Simulate string processing on the converted DFA."""
    start_id = dfa_data["start_state_id"]
    alphabet = dfa_data["alphabet"]
    final_ids = set(dfa_data["final_state_ids"])
    
    # Map state id to name
    id_to_name = {s["id"]: s["name"] for s in dfa_data["state_objects"]}
    
    # Map transitions: (from_id, symbol) -> to_id
    delta = {}
    for t in dfa_data["transitions"]:
        delta[(t["from_id"], t["symbol"])] = t["to_id"]

    curr_id = start_id
    trace = [{
        "step": 0,
        "char": "start",
        "state_id": curr_id,
        "state_name": id_to_name.get(curr_id, curr_id),
        "explanation": f"Initial DFA State: {id_to_name.get(curr_id, curr_id)}"
    }]

    for i, char in enumerate(input_string, 1):
        if char not in alphabet:
            return {
                "accepted": False,
                "error": f"Symbol '{char}' not in alphabet.",
                "trace": trace,
                "final_state_id": curr_id,
                "final_state_name": id_to_name.get(curr_id, curr_id)
            }
        
        next_id = delta.get((curr_id, char))
        if not next_id:
            return {
                "accepted": False,
                "error": f"No transition defined from {id_to_name.get(curr_id, curr_id)} on '{char}'.",
                "trace": trace,
                "final_state_id": curr_id,
                "final_state_name": id_to_name.get(curr_id, curr_id)
            }
        
        trace.append({
            "step": i,
            "char": char,
            "state_id": next_id,
            "state_name": id_to_name.get(next_id, next_id),
            "explanation": f"δ({id_to_name.get(curr_id, curr_id)}, '{char}') -> {id_to_name.get(next_id, next_id)}"
        })
        curr_id = next_id

    is_accepted = (curr_id in final_ids)
    return {
        "accepted": is_accepted,
        "trace": trace,
        "final_state_id": curr_id,
        "final_state_name": id_to_name.get(curr_id, curr_id)
    }

