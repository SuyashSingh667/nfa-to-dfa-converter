/**
 * NFA to DFA Converter - Client Frontend Logic
 * Automata Theory College Project
 */

let currentNfaData = null;
let currentDfaData = null;
let currentRawTransitions = [];
const zoomStates = {
    nfaSvgContainer: 1,
    dfaSvgContainer: 1
};

// Built-in presets for instant synchronous loading
let samplePresets = {
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
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
    fetchSamplePresets().finally(() => {
        loadSamplePreset("sample1");
    });
});

function initEventListeners() {
    // Add transition row
    document.getElementById("addTransitionBtn").addEventListener("click", () => {
        addTransitionRow();
    });

    // Convert button
    document.getElementById("convertBtn").addEventListener("click", () => {
        convertNFA();
    });

    // Sample preset dropdown selection change (instant load)
    const sampleSelect = document.getElementById("sampleSelect");
    if (sampleSelect) {
        sampleSelect.addEventListener("change", (e) => {
            loadSamplePreset(e.target.value);
        });
    }

    // Reset button
    document.getElementById("resetAllBtn").addEventListener("click", () => {
        resetAllInputs();
    });

    // Test string button
    document.getElementById("testStringBtn").addEventListener("click", () => {
        testInputString();
    });

    // Enter key triggers string test
    document.getElementById("testStringInput").addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            testInputString();
        }
    });

    // Quick empty string button
    document.getElementById("quickEmptyStringBtn").addEventListener("click", () => {
        document.getElementById("testStringInput").value = "";
        testInputString();
    });

    // Download SVG buttons
    document.getElementById("downloadNfaSvgBtn").addEventListener("click", () => {
        downloadSvg("nfaSvgContainer", "nfa_diagram.svg");
    });

    document.getElementById("downloadDfaSvgBtn").addEventListener("click", () => {
        downloadSvg("dfaSvgContainer", "dfa_diagram.svg");
    });
}

// Fetch Sample Presets
async function fetchSamplePresets() {
    try {
        const response = await fetch("/api/samples");
        if (response.ok) {
            samplePresets = await response.json();
        }
    } catch (e) {
        console.warn("Could not fetch samples from API, using defaults:", e);
    }
}

// Load a specific sample preset
function loadSamplePreset(sampleKey) {
    const sample = samplePresets[sampleKey];
    if (!sample) return;

    const select = document.getElementById("sampleSelect");
    if (select && select.value !== sampleKey) {
        select.value = sampleKey;
    }

    document.getElementById("statesInput").value = sample.states.join(", ");
    document.getElementById("alphabetInput").value = sample.alphabet.join(", ");
    document.getElementById("startStateInput").value = sample.start_state;
    document.getElementById("finalStatesInput").value = sample.final_states.join(", ");

    const deadCheck = document.getElementById("includeDeadStateCheck");
    if (deadCheck) {
        deadCheck.checked = sample.include_dead_state !== undefined ? sample.include_dead_state : true;
    }

    // Clear and populate transition table
    const tbody = document.getElementById("transitionsBody");
    tbody.innerHTML = "";
    sample.transitions.forEach(t => {
        const toVal = Array.isArray(t.to) ? t.to.join(", ") : t.to;
        addTransitionRow(t.from, t.symbol, toVal);
    });

    // Render sample test string pills
    renderSampleTestPills(sample.test_strings || []);

    hideError();
    // Automatically convert on sample load for seamless UX
    convertNFA();
}

function renderSampleTestPills(testStrings) {
    const container = document.getElementById("sampleTestPills");
    container.innerHTML = "";
    testStrings.forEach(str => {
        const pill = document.createElement("button");
        pill.className = "test-pill";
        pill.type = "button";
        pill.innerText = str === "" ? 'ε (empty)' : `"${str}"`;
        pill.title = `Click to test: ${str === "" ? 'empty string' : str}`;
        pill.onclick = () => {
            document.getElementById("testStringInput").value = str;
            testInputString();
        };
        container.appendChild(pill);
    });
}

// Dynamic Transition Editor
function addTransitionRow(from = "", symbol = "", to = "") {
    const tbody = document.getElementById("transitionsBody");
    const tr = document.createElement("tr");
    tr.className = "editor-row";

    tr.innerHTML = `
        <td>
            <input type="text" class="text-input font-code trans-from" placeholder="e.g. q0" value="${escapeHtml(from)}">
        </td>
        <td>
            <div class="symbol-input-group">
                <input type="text" class="text-input font-code trans-sym" placeholder="e.g. 0 or ε" value="${escapeHtml(symbol)}">
                <button type="button" class="btn-eps" title="Insert ε (Epsilon)">ε</button>
            </div>
        </td>
        <td>
            <input type="text" class="text-input font-code trans-to" placeholder="e.g. q0, q1" value="${escapeHtml(to)}">
        </td>
        <td style="text-align: center;">
            <button type="button" class="btn-delete-row" title="Remove transition">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </td>
    `;

    // Hook epsilon button
    const epsBtn = tr.querySelector(".btn-eps");
    const symInput = tr.querySelector(".trans-sym");
    epsBtn.addEventListener("click", () => {
        symInput.value = "ε";
        symInput.focus();
    });

    // Hook delete button
    const delBtn = tr.querySelector(".btn-delete-row");
    delBtn.addEventListener("click", () => {
        tr.remove();
    });

    tbody.appendChild(tr);
}

function getTransitionsFromEditor() {
    const rows = document.querySelectorAll("#transitionsBody tr");
    const transitions = [];
    rows.forEach(tr => {
        const from = tr.querySelector(".trans-from").value.trim();
        const sym = tr.querySelector(".trans-sym").value.trim();
        const toStr = tr.querySelector(".trans-to").value.trim();

        if (from && sym && toStr) {
            const targets = toStr.split(",").map(s => s.trim()).filter(s => s);
            transitions.push({
                from: from,
                symbol: sym,
                to: targets
            });
        }
    });
    return transitions;
}

// Convert NFA to DFA
async function convertNFA() {
    hideError();
    const convertBtn = document.getElementById("convertBtn");
    const origBtnHtml = convertBtn.innerHTML;
    convertBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Converting...`;
    convertBtn.disabled = true;

    try {
        const states = parseCommaList(document.getElementById("statesInput").value);
        const alphabet = parseCommaList(document.getElementById("alphabetInput").value);
        const startState = document.getElementById("startStateInput").value.trim();
        const finalStates = parseCommaList(document.getElementById("finalStatesInput").value);
        const includeDeadState = document.getElementById("includeDeadStateCheck").checked;
        const transitions = getTransitionsFromEditor();

        // Basic client validation
        if (states.length === 0) {
            throw new Error("Please specify at least one state in Q.");
        }
        if (alphabet.length === 0) {
            throw new Error("Please specify at least one input symbol in Σ.");
        }
        if (!startState) {
            throw new Error("Start state q₀ is required.");
        }
        if (!states.includes(startState)) {
            throw new Error(`Start state '${startState}' is not in the set of states Q.`);
        }

        const payload = {
            states: states,
            alphabet: alphabet,
            start_state: startState,
            final_states: finalStates,
            transitions: transitions,
            include_dead_state: includeDeadState
        };

        const res = await fetch("/api/convert", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok || !data.success) {
            throw new Error(data.error || "Failed to convert NFA.");
        }

        currentNfaData = data.nfa;
        currentDfaData = data.dfa;
        currentRawTransitions = transitions;

        renderResults(data);

    } catch (err) {
        showError("Machine Validation Error", err.message);
    } finally {
        convertBtn.innerHTML = origBtnHtml;
        convertBtn.disabled = false;
    }
}

// Render Results and Diagrams
function renderResults(data) {
    const resultsSection = document.getElementById("resultsSection");
    resultsSection.style.display = "block";

    // 1. Render Diagrams
    renderDiagram("nfaSvgContainer", data.nfa.svg);
    renderDiagram("dfaSvgContainer", data.dfa.svg);

    // Diagram status bars
    const setElemText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    };

    setElemText("nfaStateCount", data.nfa.states.length);
    setElemText("nfaStartDisplay", data.nfa.start_state);
    setElemText("nfaFinalDisplay", data.nfa.final_states.length ? `{${data.nfa.final_states.join(", ")}}` : "None");
    const nfaEps = document.getElementById("nfaEpsBadge");
    if (nfaEps) nfaEps.style.display = data.nfa.has_epsilon ? "inline-flex" : "none";

    setElemText("dfaStateCount", data.dfa.states.length);
    setElemText("dfaStartDisplay", data.dfa.start_state_name);
    setElemText("dfaFinalDisplay", data.dfa.final_state_names.length ? data.dfa.final_state_names.join(", ") : "None");
    
    const hasDead = data.dfa.state_objects.some(s => s.is_dead);
    const dfaDead = document.getElementById("dfaDeadBadge");
    if (dfaDead) dfaDead.style.display = hasDead ? "inline-flex" : "none";

    // 2. Render Transition Tables
    renderNfaTable(data.nfa.table);
    renderDfaTable(data.dfa.table);

    // 3. Render Step-by-Step Construction
    renderSteps(data.steps);

    // 4. Update string testing alphabet hint
    setElemText("testAlphabetDisplay", `Σ = {${data.nfa.alphabet.join(", ")}}`);
    const testResultBanner = document.getElementById("testResultBanner");
    if (testResultBanner) testResultBanner.style.display = "none";

    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderDiagram(containerId, svgString) {
    const container = document.getElementById(containerId);
    if (!svgString) {
        container.innerHTML = `<p class="input-hint" style="text-align: center; padding: 2rem;">Diagram could not be rendered.</p>`;
        return;
    }
    container.innerHTML = svgString;
    resetZoomDiagram(containerId);
}

// Render NFA Transition Table
function renderNfaTable(tableData) {
    const table = document.getElementById("nfaDisplayTable");
    if (!tableData || !tableData.headers) {
        table.innerHTML = "";
        return;
    }

    let html = "<thead><tr>";
    tableData.headers.forEach(h => {
        html += `<th>${escapeHtml(h)}</th>`;
    });
    html += "</tr></thead><tbody>";

    tableData.rows.forEach(r => {
        let stateClass = "";
        if (r.is_start && r.is_final) stateClass = "state-cell-start state-cell-final";
        else if (r.is_start) stateClass = "state-cell-start";
        else if (r.is_final) stateClass = "state-cell-final";

        html += `<tr><td class="${stateClass}">${escapeHtml(r.display_state)}</td>`;
        
        tableData.headers.slice(1).forEach(sym => {
            const val = r.transitions[sym] || "∅";
            html += `<td>${escapeHtml(val)}</td>`;
        });
        html += `</tr>`;
    });

    html += "</tbody>";
    table.innerHTML = html;
}

// Render DFA Transition Table
function renderDfaTable(tableData) {
    const table = document.getElementById("dfaDisplayTable");
    if (!tableData || !tableData.headers) {
        table.innerHTML = "";
        return;
    }

    let html = "<thead><tr>";
    tableData.headers.forEach(h => {
        html += `<th>${escapeHtml(h)}</th>`;
    });
    html += "</tr></thead><tbody>";

    tableData.rows.forEach(r => {
        let stateClass = "";
        if (r.is_dead) stateClass = "state-cell-dead";
        else if (r.is_start && r.is_final) stateClass = "state-cell-start state-cell-final";
        else if (r.is_start) stateClass = "state-cell-start";
        else if (r.is_final) stateClass = "state-cell-final";

        html += `<tr>
            <td class="${stateClass}">${escapeHtml(r.display_name)}</td>
            <td><code>${escapeHtml(r.nfa_subset)}</code></td>
        `;

        // Symbols are in headers from index 2 to end - 1
        const symbolCols = tableData.headers.slice(2, -1);
        symbolCols.forEach(sym => {
            const target = r.transitions[sym] || "∅";
            html += `<td>${escapeHtml(target)}</td>`;
        });

        // Accepting column
        const accBadge = r.is_final ? 
            `<span class="badge badge-success">Yes</span>` : 
            `<span class="badge badge-rose" style="opacity:0.6;">No</span>`;
        html += `<td>${accBadge}</td></tr>`;
    });

    html += "</tbody>";
    table.innerHTML = html;
}

// Render Step-by-Step Walkthrough
function renderSteps(steps) {
    const container = document.getElementById("stepsContainer");
    container.innerHTML = "";

    steps.forEach(step => {
        const stepDiv = document.createElement("div");
        stepDiv.className = "step-item";

        let contentHtml = "";

        if (step.step_number === 1) {
            // Epsilon closures
            contentHtml = `<div class="pills-wrapper">`;
            step.data.forEach(item => {
                contentHtml += `<div class="step-grid-pill"><span>${escapeHtml(item.display)}</span></div>`;
            });
            contentHtml += `</div>`;
        } else if (step.step_number === 2) {
            // Initial DFA state
            contentHtml = `
                <div class="step-grid-pill" style="font-size: 0.95rem; border-color: rgba(99, 102, 241, 0.4);">
                    <i class="fa-solid fa-arrow-right" style="color: var(--accent-cyan);"></i>
                    <b>${escapeHtml(step.formula)}</b>
                </div>
            `;
        } else if (step.step_number === 3) {
            // Detailed transitions log
            contentHtml = `
                <div class="table-responsive">
                    <table class="data-table" style="font-size: 0.8rem;">
                        <thead>
                            <tr>
                                <th>DFA State</th>
                                <th>NFA Subset</th>
                                <th>Input Symbol</th>
                                <th>Move (∪ δ)</th>
                                <th>ε-closure(Move)</th>
                                <th>Next State</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            step.logs.forEach(log => {
                Object.keys(log.transitions).forEach(sym => {
                    const trans = log.transitions[sym];
                    contentHtml += `
                        <tr>
                            <td><b>${escapeHtml(log.dfa_state_name)}</b></td>
                            <td><code>{${log.nfa_subset.join(", ")}}</code></td>
                            <td><span class="step-char-pill">${escapeHtml(sym)}</span></td>
                            <td>${escapeHtml(trans.move)}</td>
                            <td><b>${escapeHtml(trans.closure)}</b></td>
                            <td><span class="badge badge-primary">${escapeHtml(trans.to_state_name)}</span></td>
                        </tr>
                    `;
                });
            });
            contentHtml += `</tbody></table></div>`;
        } else if (step.step_number === 4) {
            // Final states identification
            contentHtml = `
                <div style="margin-bottom: 0.75rem;">
                    <strong style="color: #6ee7b7; font-size: 0.85rem;"><i class="fa-solid fa-circle-check"></i> Accepting DFA States:</strong>
                    <div class="pills-wrapper" style="margin-top: 0.4rem;">
            `;
            step.final_states.forEach(fs => {
                contentHtml += `
                    <div class="step-grid-pill" style="border-color: rgba(16, 185, 129, 0.4);">
                        <b>${escapeHtml(fs.name)}</b>
                        <span style="color: var(--text-muted); font-size: 0.75rem;">(contains ${fs.contains_final.join(", ")})</span>
                    </div>
                `;
            });
            contentHtml += `</div></div><div>
                <strong style="color: #94a3b8; font-size: 0.85rem;">Non-Accepting DFA States:</strong>
                <div class="pills-wrapper" style="margin-top: 0.4rem;">
            `;
            step.non_final_states.forEach(nfs => {
                contentHtml += `<div class="step-grid-pill"><span>${escapeHtml(nfs.name)}</span></div>`;
            });
            contentHtml += `</div></div>`;
        } else if (step.step_number === 5) {
            // Summary
            contentHtml = `
                <div class="pills-wrapper">
                    <div class="step-grid-pill"><span>Total States: <b>${step.total_states}</b></span></div>
                    <div class="step-grid-pill"><span>Total Transitions: <b>${step.total_transitions}</b></span></div>
                    <div class="step-grid-pill"><span>Dead State Included: <b>${step.dead_state_included ? "Yes (∅)" : "No"}</b></span></div>
                    <div class="step-grid-pill" style="color: #34d399;"><span>Equivalence Confirmed</span></div>
                </div>
            `;
        }

        stepDiv.innerHTML = `
            <div class="step-header">
                <div class="step-number-badge">${step.step_number}</div>
                <div class="step-title">${escapeHtml(step.title)}</div>
            </div>
            <div class="step-desc">${escapeHtml(step.description)}</div>
            ${contentHtml}
        `;

        container.appendChild(stepDiv);
    });
}

// Toggle steps container visibility
function toggleStepsVisibility() {
    const container = document.getElementById("stepsContainer");
    const chevron = document.getElementById("stepsChevron");
    const btn = document.getElementById("toggleStepsBtn");

    if (container.style.display === "none") {
        container.style.display = "flex";
        chevron.className = "fa-solid fa-chevron-up";
        btn.innerHTML = `<i class="fa-solid fa-chevron-up" id="stepsChevron"></i> Collapse Steps`;
    } else {
        container.style.display = "none";
        chevron.className = "fa-solid fa-chevron-down";
        btn.innerHTML = `<i class="fa-solid fa-chevron-down" id="stepsChevron"></i> Expand Steps`;
    }
}

// Test String Execution
async function testInputString() {
    if (!currentNfaData || !currentDfaData) {
        showError("Action Required", "Please convert the NFA to DFA first.");
        return;
    }

    const testStr = document.getElementById("testStringInput").value.trim();
    const testBtn = document.getElementById("testStringBtn");
    const origBtnHtml = testBtn.innerHTML;
    testBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Testing...`;
    testBtn.disabled = true;

    try {
        const payload = {
            nfa: currentNfaData,
            dfa: currentDfaData,
            nfa_transitions: currentRawTransitions,
            string: testStr
        };

        const res = await fetch("/api/test-string", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok || !data.success) {
            throw new Error(data.error || "Simulation error");
        }

        renderTestResult(data);

    } catch (err) {
        showError("Simulation Error", err.message);
    } finally {
        testBtn.innerHTML = origBtnHtml;
        testBtn.disabled = false;
    }
}

// Render String Test Results and Traces
function renderTestResult(data) {
    const banner = document.getElementById("testResultBanner");
    banner.style.display = "block";

    const statusBadge = document.getElementById("testStatusBadge");
    const matchBadge = document.getElementById("testMatchBadge");
    const stringDisplay = document.getElementById("evaluatedStringDisplay");

    stringDisplay.innerText = `Evaluated: ${data.string_display}`;

    if (data.accepted) {
        statusBadge.className = "status-badge accepted";
        statusBadge.innerText = "ACCEPTED";
    } else {
        statusBadge.className = "status-badge rejected";
        statusBadge.innerText = "REJECTED";
    }

    if (data.match) {
        matchBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> Machines Agree (Language Match)`;
        matchBadge.style.color = "#38bdf8";
    } else {
        matchBadge.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> Mismatch Detected!`;
        matchBadge.style.color = "#f43f5e";
    }

    // Render NFA Trace
    const nfaStatus = document.getElementById("nfaTraceStatus");
    nfaStatus.className = `trace-status ${data.nfa_result.accepted ? "accepted" : "rejected"}`;
    nfaStatus.innerText = data.nfa_result.accepted ? "ACCEPTED" : "REJECTED";

    const nfaBody = document.getElementById("nfaTraceBody");
    nfaBody.innerHTML = "";
    (data.nfa_result.trace || []).forEach(step => {
        const row = document.createElement("div");
        row.className = "trace-step-row";
        row.innerHTML = `
            <span class="step-idx">#${step.step}</span>
            <span class="step-char-pill">${escapeHtml(step.char)}</span>
            <span class="step-state-target">${escapeHtml(step.display_states || step.explanation)}</span>
        `;
        nfaBody.appendChild(row);
    });

    // Render DFA Trace
    const dfaStatus = document.getElementById("dfaTraceStatus");
    dfaStatus.className = `trace-status ${data.dfa_result.accepted ? "accepted" : "rejected"}`;
    dfaStatus.innerText = data.dfa_result.accepted ? "ACCEPTED" : "REJECTED";

    const dfaBody = document.getElementById("dfaTraceBody");
    dfaBody.innerHTML = "";
    (data.dfa_result.trace || []).forEach(step => {
        const row = document.createElement("div");
        row.className = "trace-step-row";
        row.innerHTML = `
            <span class="step-idx">#${step.step}</span>
            <span class="step-char-pill">${escapeHtml(step.char)}</span>
            <span class="step-state-target">${escapeHtml(step.state_name || step.explanation)}</span>
        `;
        dfaBody.appendChild(row);
    });
}

// Diagram Zoom & Pan
function zoomDiagram(containerId, factor) {
    if (!zoomStates[containerId]) zoomStates[containerId] = 1;
    zoomStates[containerId] = Math.max(0.4, Math.min(3.0, zoomStates[containerId] * factor));
    applyZoom(containerId);
}

function resetZoomDiagram(containerId) {
    zoomStates[containerId] = 1;
    applyZoom(containerId);
}

function applyZoom(containerId) {
    const container = document.getElementById(containerId);
    const scale = zoomStates[containerId];
    container.style.transform = `scale(${scale})`;
}

// Download SVG file
function downloadSvg(containerId, filename) {
    const container = document.getElementById(containerId);
    const svgEl = container.querySelector("svg");
    if (!svgEl) {
        showError("Export Error", "No SVG diagram found to download.");
        return;
    }

    const svgXml = new XMLSerializer().serializeToString(svgEl);
    const blob = new Blob([svgXml], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Reset all inputs
function resetAllInputs() {
    document.getElementById("statesInput").value = "";
    document.getElementById("alphabetInput").value = "";
    document.getElementById("startStateInput").value = "";
    document.getElementById("finalStatesInput").value = "";
    document.getElementById("transitionsBody").innerHTML = "";
    document.getElementById("resultsSection").style.display = "none";
    currentNfaData = null;
    currentDfaData = null;
    hideError();
}

// Error Helpers
function showError(title, message) {
    const alert = document.getElementById("errorAlert");
    document.getElementById("errorTitle").innerText = title;
    document.getElementById("errorMessage").innerText = message;
    alert.style.display = "flex";
    alert.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideError() {
    document.getElementById("errorAlert").style.display = "none";
}

// Utility Helpers
function parseCommaList(str) {
    return (str || "").split(",").map(s => s.trim()).filter(s => s);
}

function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

