"""
Graphviz Automata Visualizer for NFA and DFA
Styled for the Retro Windows 95/98 engineering aesthetic.
Includes built-in pure-Python SVG layout engine with retro styling.
"""

import os
import re
import math
import shutil
import subprocess
from typing import Dict, List, Any, Optional

DOT_PATH = shutil.which("dot") or (
    "/opt/homebrew/bin/dot" if os.path.exists("/opt/homebrew/bin/dot") else None
) or (
    "/usr/local/bin/dot" if os.path.exists("/usr/local/bin/dot") else None
)


def generate_nfa_dot(nfa) -> str:
    """Generate Graphviz DOT script for an NFA with retro Windows styling."""
    lines = [
        'digraph NFA {',
        '    rankdir=LR;',
        '    bgcolor="transparent";',
        '    nodesep=0.6;',
        '    ranksep=0.8;',
        '    margin=0.2;',
        '    node [fontname="Courier New, monospace", fontsize=12, fontcolor="#112211", shape=circle, style="filled", fillcolor="#f5f2eb", color="#2e3d33", penwidth=2.0, width=0.8, height=0.8];',
        '    edge [fontname="Courier New, monospace", fontsize=11, fontcolor="#1a2e1c", color="#3a4d3c", arrowsize=0.8, penwidth=1.6];',
        '',
        '    // Invisible start arrow entry point',
        '    __start [style=invis, shape=none, width=0, height=0, label=""];',
        f'    __start -> "{nfa.start_state}" [label="start", color="#1a4971", fontcolor="#1a4971", penwidth=2.2, arrowsize=0.9];',
        ''
    ]

    # Accepting states
    if nfa.final_states:
        lines.append('    // Accepting states (double circles with forest green accent)')
        lines.append('    node [shape=doublecircle, fillcolor="#e8f2e9", color="#1f6636", penwidth=2.4, fontcolor="#0f4420"];')
        for fs in nfa.final_states:
            lines.append(f'    "{fs}";')
        lines.append('')

    # Regular states
    regular_states = [s for s in nfa.states if s not in nfa.final_states]
    if regular_states:
        lines.append('    // Regular states')
        lines.append('    node [shape=circle, fillcolor="#f5f2eb", color="#2e3d33", penwidth=2.0, fontcolor="#112211"];')
        for rs in regular_states:
            lines.append(f'    "{rs}";')
        lines.append('')

    # Aggregate transitions between identical state pairs
    edge_map: Dict[tuple, List[str]] = {}
    for from_s, sym_dict in nfa.transitions.items():
        for sym, targets in sym_dict.items():
            disp_sym = "ε" if sym == "ε" else sym
            for to_s in targets:
                pair = (from_s, to_s)
                if pair not in edge_map:
                    edge_map[pair] = []
                if disp_sym not in edge_map[pair]:
                    edge_map[pair].append(disp_sym)

    lines.append('    // Transitions')
    for (from_s, to_s), syms in edge_map.items():
        label = ", ".join(syms)
        if "ε" in syms:
            lines.append(f'    "{from_s}" -> "{to_s}" [label="{label}", color="#5c3d75", fontcolor="#5c3d75"];')
        else:
            lines.append(f'    "{from_s}" -> "{to_s}" [label="{label}"];')

    lines.append('}')
    return "\n".join(lines)


def generate_dfa_dot(dfa_data: Dict[str, Any]) -> str:
    """Generate Graphviz DOT script for a converted DFA with retro Windows styling."""
    states = dfa_data["state_objects"]
    start_id = dfa_data["start_state_id"]
    transitions = dfa_data["transitions"]

    lines = [
        'digraph DFA {',
        '    rankdir=LR;',
        '    bgcolor="transparent";',
        '    nodesep=0.7;',
        '    ranksep=0.9;',
        '    margin=0.2;',
        '    node [fontname="Courier New, monospace", fontsize=11, fontcolor="#112211", shape=circle, style="filled", fillcolor="#f5f2eb", color="#2e3d33", penwidth=2.0, margin="0.1,0.1"];',
        '    edge [fontname="Courier New, monospace", fontsize=11, fontcolor="#1a2e1c", color="#3a4d3c", arrowsize=0.8, penwidth=1.6];',
        '',
        '    // Invisible start arrow entry point',
        '    __start [style=invis, shape=none, width=0, height=0, label=""];',
        f'    __start -> "{start_id}" [label="start", color="#1a4971", fontcolor="#1a4971", penwidth=2.2, arrowsize=0.9];',
        ''
    ]

    for s in states:
        sid = s["id"]
        sname = s["name"]
        
        if s.get("is_dead"):
            style_attrs = 'shape=circle, fillcolor="#fbeeee", color="#942828", penwidth=2.2, fontcolor="#942828"'
            lines.append(f'    "{sid}" [label="{sname}", {style_attrs}];')
        elif s.get("is_final"):
            style_attrs = 'shape=doublecircle, fillcolor="#e8f2e9", color="#1f6636", penwidth=2.4, fontcolor="#0f4420"'
            lines.append(f'    "{sid}" [label="{sname}", {style_attrs}];')
        else:
            style_attrs = 'shape=circle, fillcolor="#f5f2eb", color="#2e3d33", penwidth=2.0, fontcolor="#112211"'
            lines.append(f'    "{sid}" [label="{sname}", {style_attrs}];')

    lines.append('')
    lines.append('    // Transitions')
    edge_map: Dict[tuple, List[str]] = {}
    for t in transitions:
        pair = (t["from_id"], t["to_id"])
        if pair not in edge_map:
            edge_map[pair] = []
        if t["symbol"] not in edge_map[pair]:
            edge_map[pair].append(t["symbol"])

    for (from_id, to_id), syms in edge_map.items():
        label = ", ".join(syms)
        if from_id == "DEAD" and to_id == "DEAD":
            lines.append(f'    "{from_id}" -> "{to_id}" [label="{label}", color="#942828", fontcolor="#942828"];')
        else:
            lines.append(f'    "{from_id}" -> "{to_id}" [label="{label}"];')

    lines.append('}')
    return "\n".join(lines)


def render_fallback_svg(dot: str) -> str:
    """Pure Python SVG generator for automata diagrams with Retro Windows styling."""
    start_match = re.search(r'__start\s*->\s*\"([^\"]+)\"', dot)
    start_node = start_match.group(1) if start_match else None

    nodes: Dict[str, Dict[str, Any]] = {}
    double_nodes = set()
    for m in re.finditer(r'node\s*\[[^\]]*doublecircle[^\]]*\];\s*([^;]+);', dot):
        for n in re.findall(r'\"([^\"]+)\"', m.group(1)):
            double_nodes.add(n)

    for m in re.finditer(r'\"([^\"]+)\"\s*\[([^\]]+)\]', dot):
        nid = m.group(1)
        if nid == '__start':
            continue
        attrs = m.group(2)
        lbl_m = re.search(r'label=\"([^\"]*)\"', attrs)
        label = lbl_m.group(1) if lbl_m else nid
        is_final = ('doublecircle' in attrs) or (nid in double_nodes)
        is_dead = ('#fbeeee' in attrs) or ('#942828' in attrs) or (nid == 'DEAD')
        nodes[nid] = {'id': nid, 'label': label, 'is_final': is_final, 'is_dead': is_dead}

    edges: List[tuple] = []
    for m in re.finditer(r'\"([^\"]+)\"\s*->\s*\"([^\"]+)\"\s*\[([^\]]*)\]', dot):
        u, v, attrs = m.group(1), m.group(2), m.group(3)
        if u == '__start':
            continue
        lbl_m = re.search(r'label=\"([^\"]*)\"', attrs)
        lbl = lbl_m.group(1) if lbl_m else ''
        edges.append((u, v, lbl))
        if u not in nodes:
            nodes[u] = {'id': u, 'label': u, 'is_final': u in double_nodes, 'is_dead': u == 'DEAD'}
        if v not in nodes:
            nodes[v] = {'id': v, 'label': v, 'is_final': v in double_nodes, 'is_dead': v == 'DEAD'}

    if not nodes:
        return '<svg viewBox="0 0 200 100" width="100%" height="100%"></svg>'

    layers: Dict[str, int] = {}
    if start_node and start_node in nodes:
        layers[start_node] = 0
        queue = [start_node]
        while queue:
            curr = queue.pop(0)
            for u, v, _ in edges:
                if u == curr and v not in layers and v != u and v != 'DEAD':
                    layers[v] = layers[curr] + 1
                    queue.append(v)

    max_l = max(layers.values(), default=0)
    for n in nodes:
        if n not in layers:
            if n == 'DEAD':
                layers[n] = max_l + 1
            else:
                layers[n] = max_l + 1
                max_l += 1

    layer_map: Dict[int, List[str]] = {}
    for n, l in sorted(layers.items(), key=lambda x: x[1]):
        layer_map.setdefault(l, []).append(n)

    col_width = 165
    row_height = 110
    has_backward = any(layers.get(u, 0) > layers.get(v, 0) for u, v, _ in edges if u != v)

    max_k = max(len(l) for l in layer_map.values())
    height = max(280, max_k * row_height + (90 if has_backward else 50))
    width = max(420, len(layer_map) * col_width + 120)

    pos: Dict[str, tuple] = {}
    for l_idx, (l, nids) in enumerate(sorted(layer_map.items())):
        k = len(nids)
        for i, nid in enumerate(nids):
            x = 90 + l_idx * col_width
            y = (height - (50 if has_backward else 0)) / 2 + (i - (k - 1) / 2.0) * row_height
            lbl = nodes[nid]['label']
            r = max(26, 13 + len(lbl) * 4)
            pos[nid] = (x, y, r)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background: transparent;">',
        '  <defs>',
        '    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#3a4d3c"/>',
        '    </marker>',
        '    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1a4971"/>',
        '    </marker>',
        '    <marker id="arrow-purple" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#5c3d75"/>',
        '    </marker>',
        '    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '      <path d="M 0 1 L 10 5 L 0 9 z" fill="#942828"/>',
        '    </marker>',
        '  </defs>'
    ]

    # Start arrow
    if start_node and start_node in pos:
        sx, sy, sr = pos[start_node]
        svg.append(f'  <path d="M {sx - 55} {sy} L {sx - sr - 2} {sy}" stroke="#1a4971" stroke-width="2.2" marker-end="url(#arrow-blue)"/>')
        svg.append(f'  <text x="{sx - 32}" y="{sy - 7}" fill="#1a4971" font-size="11" font-weight="bold" font-family="Courier New, monospace" text-anchor="middle">start</text>')

    # Edges
    pair_counts: Dict[tuple, int] = {}
    for u, v, lbl in edges:
        p = tuple(sorted([u, v]))
        pair_counts[p] = pair_counts.get(p, 0) + 1

    backward_idx = 0
    for u, v, lbl in edges:
        x1, y1, r1 = pos[u]
        x2, y2, r2 = pos[v]
        marker = 'url(#arrow-purple)' if 'ε' in lbl else ('url(#arrow-red)' if u == 'DEAD' and v == 'DEAD' else 'url(#arrow)')
        color = '#5c3d75' if 'ε' in lbl else ('#942828' if u == 'DEAD' and v == 'DEAD' else '#3a4d3c')

        if u == v:
            # Self loop
            svg.append(f'  <path d="M {x1 - 10} {y1 - r1} C {x1 - 25} {y1 - r1 - 35}, {x1 + 25} {y1 - r1 - 35}, {x1 + 10} {y1 - r1}" fill="none" stroke="{color}" stroke-width="1.8" marker-end="{marker}"/>')
            svg.append(f'  <text x="{x1}" y="{y1 - r1 - 18}" fill="{color}" font-size="11" font-weight="bold" font-family="Courier New, monospace" text-anchor="middle">{lbl}</text>')
        elif layers.get(u, 0) > layers.get(v, 0):
            # Backward edge
            backward_idx += 1
            ctrl_y = height - 16 - (backward_idx % 2) * 14
            svg.append(f'  <path d="M {x1} {y1 + r1} C {x1} {ctrl_y}, {x2} {ctrl_y}, {x2} {y2 + r2}" fill="none" stroke="{color}" stroke-width="1.8" marker-end="{marker}"/>')
            mid_x = (x1 + x2) / 2
            svg.append(f'  <text x="{mid_x}" y="{ctrl_y - 5}" fill="{color}" font-size="11" font-weight="bold" font-family="Courier New, monospace" text-anchor="middle">{lbl}</text>')
        else:
            # Forward edge
            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)
            if dist > 0:
                ux, uy = dx / dist, dy / dist
                sx = x1 + ux * r1
                sy = y1 + uy * r1
                ex = x2 - ux * r2
                ey = y2 - uy * r2

                is_bidir = pair_counts.get(tuple(sorted([u, v])), 0) > 1
                if is_bidir:
                    cx = (sx + ex) / 2 - uy * 24
                    cy = (sy + ey) / 2 + ux * 24
                    svg.append(f'  <path d="M {sx} {sy} Q {cx} {cy} {ex} {ey}" fill="none" stroke="{color}" stroke-width="1.8" marker-end="{marker}"/>')
                    svg.append(f'  <text x="{cx}" y="{cy - 4}" fill="{color}" font-size="11" font-weight="bold" font-family="Courier New, monospace" text-anchor="middle">{lbl}</text>')
                else:
                    svg.append(f'  <line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke="{color}" stroke-width="1.8" marker-end="{marker}"/>')
                    mx = (sx + ex) / 2
                    my = (sy + ey) / 2 - 7
                    svg.append(f'  <text x="{mx}" y="{my}" fill="{color}" font-size="11" font-weight="bold" font-family="Courier New, monospace" text-anchor="middle">{lbl}</text>')

    # Nodes
    for nid, (x, y, r) in pos.items():
        ninfo = nodes[nid]
        lbl = ninfo['label']
        if ninfo['is_dead']:
            fill = '#fbeeee'
            stroke = '#942828'
            text_color = '#942828'
            svg.append(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
        elif ninfo['is_final']:
            fill = '#e8f2e9'
            stroke = '#1f6636'
            text_color = '#0f4420'
            svg.append(f'  <circle cx="{x}" cy="{y}" r="{r + 4}" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
            svg.append(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        else:
            fill = '#f5f2eb'
            stroke = '#2e3d33'
            text_color = '#112211'
            svg.append(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2.0"/>')

        svg.append(f'  <text x="{x}" y="{y}" dy="0.35em" fill="{text_color}" font-size="11" font-weight="bold" font-family="Courier New, monospace" text-anchor="middle">{lbl}</text>')

    svg.append('</svg>')
    return '\n'.join(svg)


def render_dot_to_svg(dot_string: str) -> Optional[str]:
    """Render a DOT script to SVG using the dot binary if available, or pure-Python SVG engine."""
    global DOT_PATH
    if not DOT_PATH or not os.path.exists(DOT_PATH):
        DOT_PATH = shutil.which("dot") or (
            "/opt/homebrew/bin/dot" if os.path.exists("/opt/homebrew/bin/dot") else None
        )

    if DOT_PATH and os.path.exists(DOT_PATH):
        try:
            proc = subprocess.run(
                [DOT_PATH, "-Tsvg"],
                input=dot_string,
                capture_output=True,
                text=True,
                check=True
            )
            svg_content = proc.stdout
            svg_start = svg_content.find("<svg")
            if svg_start != -1:
                return svg_content[svg_start:]
            return svg_content
        except Exception as e:
            print(f"Error rendering dot to SVG via dot binary: {e}")

    return render_fallback_svg(dot_string)
