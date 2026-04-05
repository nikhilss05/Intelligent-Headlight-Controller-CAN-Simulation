"""
Intelligent Headlight Controller — CAN Bus Simulation
======================================================
Node A (Body Control Module)  →  CAN Bus (ID 0x215)  →  Node B (Headlight Actuator)

Run:  pip install streamlit python-can --break-system-packages
      streamlit run app.py
"""

import streamlit as st
import can
import time
import random

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Intelligent Headlight Controller",
    page_icon="💡",
    layout="wide",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Outfit:wght@300;400;600;700;800&display=swap');

    /* Global */
    .stApp { background-color: #0a0e17; }
    h1, h2, h3 { font-family: 'Outfit', sans-serif !important; }

    /* Title banner */
    .title-banner {
        background: linear-gradient(135deg, #0f1923 0%, #1a2940 50%, #0f1923 100%);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .title-banner h1 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800;
        font-size: 2.2rem;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .title-banner p {
        font-family: 'Outfit', sans-serif;
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }

    /* Node cards */
    .node-card {
        background: linear-gradient(180deg, #111827 0%, #0d1117 100%);
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .node-header {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.15rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .node-a .node-header { color: #60a5fa; }
    .node-b .node-header { color: #a78bfa; }

    /* CAN frame display */
    .can-frame {
        background: #0c1220;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 1.2rem;
        font-family: 'JetBrains Mono', monospace;
        margin: 0.8rem 0;
    }
    .can-id {
        color: #fbbf24;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .byte-row {
        display: flex;
        gap: 10px;
        margin-top: 0.6rem;
        flex-wrap: wrap;
    }
    .byte-cell {
        background: #162032;
        border: 1px solid #2a4060;
        border-radius: 8px;
        padding: 0.5rem 0.9rem;
        text-align: center;
        min-width: 90px;
    }
    .byte-label {
        font-size: 0.65rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .byte-val {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-top: 2px;
    }
    .byte-hex {
        font-size: 0.7rem;
        color: #60a5fa;
        margin-top: 2px;
    }

    /* Status pill */
    .status-pill {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    .status-ok {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .status-fail {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .status-off {
        background: rgba(100, 116, 139, 0.15);
        color: #94a3b8;
        border: 1px solid rgba(100, 116, 139, 0.3);
    }

    /* Headlight visual */
    .headlight-visual {
        text-align: center;
        padding: 1.5rem;
        border-radius: 14px;
        margin: 0.8rem 0;
    }
    .hl-off {
        background: linear-gradient(180deg, #111827 0%, #0a0e17 100%);
        border: 1px solid #1e293b;
    }
    .hl-drl {
        background: linear-gradient(180deg, #1a2332 0%, #0f1923 100%);
        border: 1px solid #2a4060;
        box-shadow: 0 0 40px rgba(96, 165, 250, 0.1);
    }
    .hl-low {
        background: linear-gradient(180deg, #1a2332 0%, #0f1923 100%);
        border: 1px solid #c08420;
        box-shadow: 0 0 50px rgba(251, 191, 36, 0.15);
    }
    .hl-high {
        background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
        border: 1px solid #fbbf24;
        box-shadow: 0 0 80px rgba(251, 191, 36, 0.25);
    }
    .hl-corrupt {
        background: linear-gradient(180deg, #1f1215 0%, #0a0e17 100%);
        border: 1px solid #7f1d1d;
        box-shadow: 0 0 40px rgba(239, 68, 68, 0.1);
    }
    .hl-icon { font-size: 3rem; margin-bottom: 0.5rem; }
    .hl-mode {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        color: #e2e8f0;
    }
    .hl-bright {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.3rem;
    }

    /* Arrow */
    .can-arrow {
        text-align: center;
        padding: 0.5rem;
        font-size: 1.5rem;
        color: #334155;
        font-family: 'Outfit', sans-serif;
    }

    /* Log */
    .log-entry {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        margin-bottom: 4px;
    }
    .log-tx {
        background: rgba(96, 165, 250, 0.08);
        color: #60a5fa;
        border-left: 3px solid #60a5fa;
    }
    .log-rx-ok {
        background: rgba(34, 197, 94, 0.08);
        color: #4ade80;
        border-left: 3px solid #4ade80;
    }
    .log-rx-fail {
        background: rgba(239, 68, 68, 0.08);
        color: #f87171;
        border-left: 3px solid #f87171;
    }

    /* Info box */
    .info-box {
        background: #0c1220;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #94a3b8;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# NODE A — PRODUCER LOGIC (Body Control Module)
# ══════════════════════════════════════════════

def classify_light(lux: int) -> str:
    """Classify ambient light into categories."""
    if lux > 100:
        return "Bright"
    elif lux >= 20:
        return "Moderate"
    else:
        return "Dark"


def decide_headlight(switch_pos: int, lux: int) -> tuple:
    """Determine headlight command and intensity based on switch + sensor."""
    if switch_pos == 0:
        return 0, 0          # Off
    elif switch_pos == 1:
        return 2, 80         # Manual → Low Beam
    else:                     # Auto mode (switch_pos == 2)
        cat = classify_light(lux)
        if cat == "Bright":
            return 1, 50     # DRL
        elif cat == "Moderate":
            return 2, 80     # Low Beam
        else:
            return 3, 100    # High Beam


def pack_can_message(command: int, intensity: int) -> can.Message:
    """Pack command, intensity, and checksum into CAN frame ID 0x215."""
    checksum = command + intensity
    return can.Message(
        arbitration_id=0x215,
        data=[command, intensity, checksum, 0, 0, 0, 0, 0],
        is_extended_id=False,
    )


# ══════════════════════════════════════════════
# NODE B — CONSUMER LOGIC (Headlight Actuator)
# ══════════════════════════════════════════════

MODE_MAP = {0: "Off", 1: "Daytime Running Lights", 2: "Low Beam", 3: "High Beam"}


def verify_checksum(b0: int, b1: int, b2: int) -> bool:
    """Verify data integrity using checksum."""
    return (b0 + b1) == b2


def process_received(msg: can.Message, corrupt: bool = False):
    """Unpack and verify a received CAN message."""
    if msg.arbitration_id != 0x215:
        return None

    data = bytearray(msg.data)
    if corrupt:
        # Simulate corruption: flip a random bit in byte 1
        data[1] = (data[1] ^ random.randint(1, 15)) & 0xFF

    b0, b1, b2 = data[0], data[1], data[2]

    if verify_checksum(b0, b1, b2):
        mode = MODE_MAP.get(b0, "Unknown")
        return {
            "valid": True,
            "bytes": (b0, b1, b2),
            "mode": mode,
            "intensity": b1,
            "msg": f"Data Verified. Mode: {mode} at {b1}% Brightness.",
        }
    else:
        return {
            "valid": False,
            "bytes": (b0, b1, b2),
            "mode": None,
            "intensity": None,
            "msg": f"Data Corrupted! Checksum mismatch: {b0}+{b1}={b0+b1} ≠ {b2}. Message ignored.",
        }


# ══════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════

# Title
st.markdown("""
<div class="title-banner">
    <h1>💡 Intelligent Headlight Controller</h1>
    <p>CAN Bus Simulation  ·  Node A (BCM) → ID 0x215 → Node B (Actuator)</p>
</div>
""", unsafe_allow_html=True)

# Layout: 3 columns — Node A | CAN Bus | Node B
col_a, col_bus, col_b = st.columns([1, 0.8, 1], gap="medium")

# ─── NODE A (left column) ───
with col_a:
    st.markdown('<div class="node-card node-a"><div class="node-header">🔧 Node A — Body Control Module (Producer)</div>', unsafe_allow_html=True)

    lux = st.slider("🌞 Ambient Light (Lux)", min_value=0, max_value=500, value=20, step=1)
    switch_labels = {0: "0 — Off", 1: "1 — Manual On", 2: "2 — Auto Mode"}
    switch_pos = st.selectbox(
        "🔘 Manual Switch Position",
        options=[0, 1, 2],
        index=2,
        format_func=lambda x: switch_labels[x],
    )

    # Compute
    command, intensity = decide_headlight(switch_pos, lux)
    light_cat = classify_light(lux)
    checksum = command + intensity

    st.markdown(f"""
    <div class="info-box">
        <b>Decision Logic Trace:</b><br>
        Lux = {lux} → Category: <b>{light_cat}</b><br>
        Switch = {switch_pos} ({switch_labels[switch_pos].split('— ')[1]})<br>
        ──────────────────<br>
        Command  = <b>{command}</b> ({MODE_MAP.get(command, '?')})<br>
        Intensity = <b>{intensity}</b>%<br>
        Checksum = {command} + {intensity} = <b>{checksum}</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─── CAN BUS (middle column) ───
with col_bus:
    st.markdown('<div class="node-card">', unsafe_allow_html=True)
    st.markdown('<div class="node-header" style="color:#fbbf24;">📡 CAN Bus — ID 0x215</div>', unsafe_allow_html=True)

    msg = pack_can_message(command, intensity)

    # Inject corruption toggle
    corrupt = st.checkbox("⚡ Simulate data corruption", value=False)

    st.markdown(f"""
    <div class="can-frame">
        <div class="can-id">CAN ID: 0x215 &nbsp;|&nbsp; DLC: 3</div>
        <div class="byte-row">
            <div class="byte-cell">
                <div class="byte-label">Byte 0</div>
                <div class="byte-val">{msg.data[0]}</div>
                <div class="byte-hex">0x{msg.data[0]:02X} CMD</div>
            </div>
            <div class="byte-cell">
                <div class="byte-label">Byte 1</div>
                <div class="byte-val">{msg.data[1]}</div>
                <div class="byte-hex">0x{msg.data[1]:02X} INT</div>
            </div>
            <div class="byte-cell">
                <div class="byte-label">Byte 2</div>
                <div class="byte-val">{msg.data[2]}</div>
                <div class="byte-hex">0x{msg.data[2]:02X} CHK</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Raw hex dump
    hex_str = " ".join(f"{b:02X}" for b in msg.data)
    st.markdown(f"""
    <div class="info-box" style="margin-top:0.6rem;">
        <b>Raw Frame (hex):</b><br>
        [{hex_str}]
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="can-arrow">▼ ▼ ▼<br><span style="font-size:0.7rem;color:#475569;">TRANSMIT</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─── NODE B (right column) ───
with col_b:
    result = process_received(msg, corrupt=corrupt)

    st.markdown('<div class="node-card node-b"><div class="node-header">💡 Node B — Headlight Actuator (Consumer)</div>', unsafe_allow_html=True)

    if result:
        b0, b1, b2 = result["bytes"]

        # Checksum verification display
        chk_pass = result["valid"]
        chk_icon = "✅" if chk_pass else "❌"
        chk_class = "status-ok" if chk_pass else "status-fail"
        chk_label = "VERIFIED" if chk_pass else "CORRUPTED"

        st.markdown(f"""
        <div class="info-box">
            <b>Unpacked Bytes:</b><br>
            Byte 0 (Command)  = {b0}<br>
            Byte 1 (Intensity) = {b1}<br>
            Byte 2 (Checksum)  = {b2}<br>
            ──────────────────<br>
            Check: {b0} + {b1} = {b0 + b1} {'==' if chk_pass else '≠'} {b2}<br>
            {chk_icon} <span class="{chk_class}" style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.75rem;">{chk_label}</span>
        </div>
        """, unsafe_allow_html=True)

        # Headlight visual
        if not chk_pass:
            hl_cls = "hl-corrupt"
            hl_icon = "🚫"
            hl_mode = "DATA CORRUPTED"
            hl_bright = "Message discarded — no action taken"
        elif result["mode"] == "Off":
            hl_cls = "hl-off"
            hl_icon = "⬛"
            hl_mode = "OFF"
            hl_bright = "Headlights are off"
        elif result["mode"] == "Daytime Running Lights":
            hl_cls = "hl-drl"
            hl_icon = "🔵"
            hl_mode = "DAYTIME RUNNING LIGHTS"
            hl_bright = f"Brightness: {result['intensity']}%"
        elif result["mode"] == "Low Beam":
            hl_cls = "hl-low"
            hl_icon = "🟡"
            hl_mode = "LOW BEAM"
            hl_bright = f"Brightness: {result['intensity']}%"
        elif result["mode"] == "High Beam":
            hl_cls = "hl-high"
            hl_icon = "🔆"
            hl_mode = "HIGH BEAM"
            hl_bright = f"Brightness: {result['intensity']}%"
        else:
            hl_cls = "hl-off"
            hl_icon = "❓"
            hl_mode = "UNKNOWN"
            hl_bright = ""

        st.markdown(f"""
        <div class="headlight-visual {hl_cls}">
            <div class="hl-icon">{hl_icon}</div>
            <div class="hl-mode">{hl_mode}</div>
            <div class="hl-bright">{hl_bright}</div>
        </div>
        """, unsafe_allow_html=True)

        # Final output message
        if chk_pass and result["mode"] != "Off":
            st.markdown(f"""
            <div class="log-entry log-rx-ok">
                ✅ {result["msg"]}
            </div>
            """, unsafe_allow_html=True)
        elif chk_pass:
            st.markdown(f"""
            <div class="log-entry log-tx">
                ⬛ Headlights OFF. No CAN action required.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="log-entry log-rx-fail">
                ❌ {result["msg"]}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────
# Bottom section: full message log + reference table
# ──────────────────────────────
st.markdown("---")
col_log, col_ref = st.columns(2, gap="medium")

with col_log:
    st.markdown("#### 📋 Message Trace Log")
    ts = time.strftime("%H:%M:%S")
    hex_data = " ".join(f"0x{b:02X}" for b in msg.data[:3])

    st.markdown(f"""
    <div class="log-entry log-tx">
        [{ts}] TX → ID=0x215 | Data=[{hex_data}] | DLC=3
    </div>
    """, unsafe_allow_html=True)

    if result:
        if result["valid"]:
            st.markdown(f"""
            <div class="log-entry log-rx-ok">
                [{ts}] RX ← ID=0x215 | Checksum OK | Mode={result['mode']} | Intensity={result['intensity']}%
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="log-entry log-rx-fail">
                [{ts}] RX ← ID=0x215 | Checksum FAIL | {result['bytes'][0]}+{result['bytes'][1]}={result['bytes'][0]+result['bytes'][1]} ≠ {result['bytes'][2]} | DISCARDED
            </div>
            """, unsafe_allow_html=True)

with col_ref:
    st.markdown("#### 📖 Decision Logic Reference")
    ref_data = {
        "Switch": ["0 (Off)", "1 (Manual)", "2 (Auto)", "2 (Auto)", "2 (Auto)"],
        "Light": ["Any", "Any", "> 100 Lux", "20–100 Lux", "< 20 Lux"],
        "Command": ["0 (Off)", "2 (Low Beam)", "1 (DRL)", "2 (Low Beam)", "3 (High Beam)"],
        "Intensity": ["0%", "80%", "50%", "80%", "100%"],
    }
    st.table(ref_data)

st.markdown("""
<div style="text-align:center; padding:1.5rem; color:#475569; font-family:'Outfit',sans-serif; font-size:0.8rem;">
    Intelligent Headlight Controller · CAN 2.0A Simulation · 23ECPE16 Automotive Electronics
</div>
""", unsafe_allow_html=True)