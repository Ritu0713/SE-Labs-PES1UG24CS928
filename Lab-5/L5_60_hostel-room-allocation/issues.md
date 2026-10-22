# Identified Issues and Fixes

The following table documents the static analysis findings and functional issues identified in `hostel_allocation.py` using **Bandit**, **Pylint**, and **Flake8**, prioritized by High and Medium severity.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| Flask Debug Enabled (`B201`) | Vulnerability (High) | 80 | Flask application run with `debug=True`, exposing Werkzeug interactive debugger and remote code execution (RCE) risk. | Set `debug=False` in `app.run()` to prevent unauthorized debug console access. |
| Insecure YAML Deserialization (`B506`) | Vulnerability (Medium) | 21 | `yaml.load(text, Loader=yaml.Loader)` allows arbitrary Python object instantiation and code execution. | Replaced with `yaml.safe_load(text)` to restrict deserialization to standard data types. |
| Insecure Logging Listener (`B612`) | Vulnerability (Medium) | 72 | `logging.config.listen(9999)` opens an unauthenticated socket listening for logging configurations, vulnerable to RCE. | Removed insecure socket listener; configured safe logging or returned `None`. |
| Mutable Default Argument (`W0102`) | Bug (Medium) | 29 | `preferred=[]` as default parameter creates shared mutable state across repeated function calls. | Changed default parameter to `preferred=None` and initialized `preferred = []` within the function body. |
| Hardcoded Password (`B106`) | Vulnerability (Low) | 66 | Database password `"Hostel@123"` hardcoded directly into the script. | Used `os.getenv("WARDEN_DB_PASSWORD", ...)` to retrieve credentials securely from environment variables. |
| Weak Random Number Generator (`B311`) | Security (Low) | 56 | Standard `random.sample` is pseudo-random and not cryptographically secure for lottery allocations. | Used `secrets.SystemRandom().sample(...)` (`random.SystemRandom()`) for CSPRNG randomness. |
| Room Over-Allocation Bug | Bug (Logic) | 34 | Condition `len(occupants) > capacity` allowed rooms to accept one occupant beyond maximum capacity (e.g., 3 in a room of 2). | Changed condition to `>= room["capacity"]` to strictly enforce room bed limits. |
| Gender Segregation Ignored | Bug (Logic) | 29, 32-38 | `gender` parameter was unused (`W0613`); female students were allocated to male hostel blocks. | Added check `if room["gender"] != gender: continue` to ensure proper block-gender matching. |
| Incomplete Room Eviction | Bug (Logic) | 41-45 | `vacateRoom` deleted student from `allocations` dictionary but left their ID in `rooms[room_no]["occupants"]`. | Added logic to locate the room and remove `student_id` from `rooms[room_no]["occupants"]`. |
| Reversed Seniority Ordering | Bug (Logic) | 53 | `priorityOrder` sorted ascending (`reverse=False`), prioritizing freshers (Year 1) over seniors (Year 4). | Added `reverse=True` in `sorted(..., key=lambda s: s["year"])` so seniors are placed first. |
| Flawed Vacant Bed Calculation | Bug (Logic) | 58-63 | `vacantBeds` only counted completely unoccupied rooms, ignoring partially filled rooms. | Summed `capacity - len(occupants)` across all rooms using dictionary values. |
| Non-PEP 8 Naming Conventions (`C0103`) | Code Quality | Multiple (20, 29, 41, etc.) | Function names used `camelCase` (`loadConfig`, `allocateRoom`, etc.) instead of PEP 8 `snake_case`. | Renamed all functions to standard `snake_case` (e.g., `load_config`, `allocate_room`). |
| Missing Docstrings (`C0114`, `C0116`) | Documentation | 1, 20, 29, etc. | Missing module and function docstrings lowered Pylint score to 5.84/10. | Added descriptive PEP 257 docstrings for the module and all functions, achieving 10.00/10. |
| Unidiomatic Type Check (`C0123`, `E721`) | Code Smell / Style | 30 | `type(year) != int` is unidiomatic and does not support inheritance. | Replaced with `not isinstance(year, int)`. |
| Unused Imports (`W0611`, `F401`) | Code Smell | 1, 2 | `os` and `sys` imported but unused in original code. | Retained `os` for secure credential access, removed unused `sys`, and added `html` for escaping. |
| Formatting & Blank Line Violations (`E302`, `E305`, `E501`) | Style (PEP 8) | Multiple | Missing 2 blank lines between top-level functions and lines exceeding 79 characters. | Formatted code to adhere strictly to PEP 8 whitespace and 79-character line limits. |
