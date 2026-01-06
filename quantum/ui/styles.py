"""
Quantum Market Suite - UI Styles

CSS constants and styling utilities for the dashboard.
"""

# Color palettes
DARK_COLORS = {
    "bg_primary": "#030303",
    "bg_secondary": "#0a0a0f",
    "bg_glass": "rgba(15, 15, 25, 0.7)",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "accent": "#818cf8",
    "accent_glow": "rgba(129, 140, 248, 0.3)",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "border": "rgba(255, 255, 255, 0.1)",
}

LIGHT_COLORS = {
    "bg_primary": "#f8fafc",
    "bg_secondary": "#ffffff",
    "bg_glass": "rgba(255, 255, 255, 0.7)",
    "text_primary": "#1e293b",
    "text_secondary": "#64748b",
    "accent": "#6366f1",
    "accent_glow": "rgba(99, 102, 241, 0.2)",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "border": "rgba(0, 0, 0, 0.1)",
}

# Grid layout CSS
GRID_LAYOUT_CSS = """
.quantum-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 1rem;
}

.quantum-card {
    background: var(--bg-glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.quantum-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.quantum-metric {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.quantum-metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.2;
}

.quantum-metric-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
}
"""

# Component-specific styles
SIDEBAR_CSS = """
.sidebar-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 1.5rem;
    text-align: center;
}

.sidebar-section {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

.sidebar-section-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
}
"""

TABLE_CSS = """
.quantum-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
}

.quantum-table th {
    background: var(--accent);
    color: white;
    padding: 1rem;
    text-align: left;
    font-weight: 600;
}

.quantum-table td {
    padding: 0.875rem 1rem;
    border-bottom: 1px solid var(--border);
}

.quantum-table tr:hover td {
    background: var(--bg-glass);
}
"""

BUTTON_CSS = """
.quantum-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-weight: 500;
    transition: all 0.3s ease;
    cursor: pointer;
    border: none;
}

.quantum-btn-primary {
    background: linear-gradient(135deg, var(--accent) 0%, #6366f1 100%);
    color: white;
    box-shadow: 0 4px 15px var(--accent-glow);
}

.quantum-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px var(--accent-glow);
}

.quantum-btn-secondary {
    background: var(--bg-glass);
    color: var(--text-primary);
    border: 1px solid var(--border);
}

.quantum-btn-secondary:hover {
    background: var(--bg-secondary);
}
"""

NOTEPAD_CSS = """
.quantum-notepad {
    background: var(--bg-glass);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    min-height: 200px;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
    resize: vertical;
}

.quantum-notepad:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-glow);
}
"""

# Animation keyframes
ANIMATIONS_CSS = """
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.animate-fade-in {
    animation: fadeIn 0.5s ease-out;
}

.animate-pulse {
    animation: pulse 2s infinite;
}

.loading-shimmer {
    background: linear-gradient(90deg, var(--bg-glass) 25%, var(--bg-secondary) 50%, var(--bg-glass) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}
"""


def get_full_css(theme: str = "dark") -> str:
    """Get complete CSS for the application."""
    return f"""
    {GRID_LAYOUT_CSS}
    {SIDEBAR_CSS}
    {TABLE_CSS}
    {BUTTON_CSS}
    {NOTEPAD_CSS}
    {ANIMATIONS_CSS}
    """
