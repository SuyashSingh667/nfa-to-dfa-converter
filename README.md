# NFA to DFA Converter - Automata Studio

An interactive web application for Automata Theory & Computation. Converts any Non-Deterministic Finite Automaton (NFA, with or without &epsilon;-transitions) into its strictly equivalent minimal Deterministic Finite Automaton (DFA) using the mathematical Powerset / Subset Construction algorithm.

Styled in an authentic retro Windows / Lunospace aesthetic with sage floral damask wallpaper, beveled window chrome, and custom cursors.

---

## Features

- **Powerset / Subset Construction Algorithm**:
  - Handles &epsilon;-transitions with full &epsilon;-closure resolution.
  - Automatically generates compound DFA subsets (e.g. `{q0, q1, q2}`).
  - Identifies start states and accepting states dynamically.
  - Optional dead / trap state (`∅`) resolution for incomplete transition functions.

- **Dual Interactive Visualizations**:
  - Side-by-side vector SVG state diagrams for both Original NFA and Converted DFA.
  - Built-in pure-Python fallback layout engine rendering high-quality vector SVGs without requiring external Graphviz system binaries.
  - Interactive diagram controls: Zoom in, Zoom out, 1:1 Reset, and SVG download.

- **Step-by-Step Construction Log**:
  - Comprehensive mathematical trace log explaining every transition calculation and closure expansion step-by-step.

- **Dual Transition Matrices**:
  - Formal side-by-side transition tables comparing NFA and DFA state transition mappings.

- **Parallel Language Equivalence Simulator**:
  - Test input strings simultaneously on both the NFA and DFA.
  - Visual step-by-step state traversal trace for both machines.
  - Immediate acceptance verification and confirmation that both machines agree.

- **Pre-configured Automata Presets**:
  - Preset 1: Ends with `'01'`
  - Preset 2: Epsilon-NFA ($a^*b^*c^*$)
  - Preset 3: Contains substring `'00'` or `'11'`
  - Preset 4: Starts with `'a'`, ends with `'b'` (Dead State Required)
  - Preset 5: Contains substring `'01'`
  - Preset 6: Even number of 0s

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/nfa-to-dfa-converter.git
   cd nfa-to-dfa-converter
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python3 app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5001
   ```

---

## Running the Automated Test Suite

A comprehensive test suite verifies validation, &epsilon;-closures, powerset conversion, SVG generation, and string simulation equivalence:

```bash
python3 test_suite.py
```

---

## Project Structure

```
├── app.py              # Flask server and REST API endpoints (/api/convert, /api/test-string, /api/samples)
├── converter.py        # Core automata models (NFA, DFA, ε-closure, subset construction, simulator)
├── graph.py            # Graphviz DOT generator & pure-Python vector SVG fallback engine
├── test_suite.py       # Comprehensive unit and integration test suite
├── requirements.txt    # Python package dependencies
├── templates/
│   └── index.html      # Retro application interface
└── static/
    ├── style.css       # Retro Windows & Lunospace stylesheet
    ├── script.js       # Client frontend interaction logic
    ├── favicon.svg     # 32x32 retro window favicon
    └── cursor/         # Custom Black Bow Tooth cursor assets
```

---

## License

MIT License.
