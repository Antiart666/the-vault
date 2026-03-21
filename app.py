import os
import streamlit as st

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Vault of Antichrister",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS – clean, modern, reader-friendly design ────────────────────────
st.markdown(
    """
    <style>
    /* ---- Global font & background ---- */
    html, body, [class*="css"] {
        font-family: 'Georgia', 'Times New Roman', serif;
        background-color: #0e0e0e;
        color: #e8e0d5;
    }

    /* ---- Main content area ---- */
    .main .block-container {
        max-width: 860px;
        padding: 2.5rem 3rem 4rem 3rem;
        margin: auto;
    }

    /* ---- Page title ---- */
    h1 {
        font-size: 2.6rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: #f5f0e8;
        border-bottom: 1px solid #444;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }

    /* ---- Section headings ---- */
    h2 {
        font-size: 1.6rem;
        color: #d4c9b8;
        margin-top: 2rem;
        margin-bottom: 0.75rem;
    }

    h3 {
        font-size: 1.2rem;
        color: #c0b49f;
    }

    /* ---- Long-form text readability ---- */
    p, .stText {
        font-size: 1.05rem;
        line-height: 1.85;
        color: #d9d0c5;
        max-width: 780px;
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background-color: #161616;
        border-right: 1px solid #2a2a2a;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-size: 1.05rem;
        padding: 0.3rem 0;
        cursor: pointer;
        color: #c0b49f;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        color: #f5f0e8;
    }

    /* ---- File / article list buttons ---- */
    .stButton button {
        background-color: transparent;
        border: 1px solid #3a3a3a;
        color: #c0b49f;
        border-radius: 4px;
        width: 100%;
        text-align: left;
        padding: 0.55rem 1rem;
        margin-bottom: 0.3rem;
        font-size: 0.95rem;
        transition: background-color 0.15s ease, color 0.15s ease;
    }

    .stButton button:hover {
        background-color: #1e1e1e;
        color: #f5f0e8;
        border-color: #666;
    }

    /* ---- Article content container ---- */
    .article-content {
        background-color: #131313;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 2rem 2.5rem;
        margin-top: 1rem;
        white-space: pre-wrap;
        font-size: 1.05rem;
        line-height: 1.9;
        color: #ddd5c8;
    }

    /* ---- Divider ---- */
    hr {
        border: none;
        border-top: 1px solid #2a2a2a;
        margin: 1.5rem 0;
    }

    /* ---- Sidebar logo / title ---- */
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f5f0e8;
        letter-spacing: 0.05em;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #2a2a2a;
    }

    /* ---- Home page intro ---- */
    .home-intro {
        font-size: 1.1rem;
        line-height: 1.9;
        color: #d4c9b8;
        max-width: 760px;
    }

    /* ---- Category badge ---- */
    .category-badge {
        display: inline-block;
        background-color: #1e1e1e;
        border: 1px solid #3a3a3a;
        color: #a09080;
        font-size: 0.8rem;
        padding: 0.2rem 0.6rem;
        border-radius: 3px;
        margin-bottom: 1rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Constants ─────────────────────────────────────────────────────────────────
CATEGORIES = {
    "Hem": None,
    "Recensioner": "recensioner",
    "Artiklar": "artiklar",
    "Uppsats": "uppsats",
    "Intervjuer": "intervjuer",
    "Filmhistoria": "filmhistoria",
    "Pressklipp": "pressklipp",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Helper functions ──────────────────────────────────────────────────────────

def list_files(folder: str) -> list[str]:
    """Return sorted .txt filenames (without extension) from *folder*."""
    folder_path = os.path.join(BASE_DIR, folder)
    if not os.path.isdir(folder_path):
        return []
    return sorted(
        f[:-4] for f in os.listdir(folder_path) if f.endswith(".txt")
    )


def read_file(folder: str, filename: str) -> str:
    """Read and return the content of a .txt file in *folder*."""
    file_path = os.path.join(BASE_DIR, folder, filename + ".txt")
    if not os.path.isfile(file_path):
        return "_Filen kunde inte hittas._"
    with open(file_path, encoding="utf-8") as fh:
        return fh.read()


def format_title(slug: str) -> str:
    """Convert a filename slug to a human-readable title."""
    return slug.replace("-", " ").title()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sidebar-title">🎬 The Vault of Antichrister</div>', unsafe_allow_html=True)
    selected_page = st.radio(
        "Navigering",
        list(CATEGORIES.keys()),
        label_visibility="collapsed",
    )

# ── Main header ───────────────────────────────────────────────────────────────

st.title("The Vault of Antichrister")

# ── Page rendering ────────────────────────────────────────────────────────────

if selected_page == "Hem":
    st.markdown(
        """
        <div class="home-intro">
        <p>Välkommen till <strong>The Vault of Antichrister</strong> – ett arkiv tillägnat Lars von Triers filmografi
        och den europeiska arthouse-cinematradition han tillhör.</p>

        <p>Här samlas recensioner, essäer, intervjuer, historiska kompendier och pressklipp från
        internationell och skandinavisk filmpress. Materialet erbjuder djupgående analyser av von Triers
        mest provocerande och konstnärligt betydelsefulla verk.</p>

        <p>Använd menyn till vänster för att navigera mellan arkivets avdelningar.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Avdelningar i arkivet")

    cols = st.columns(3)
    category_items = [(k, v) for k, v in CATEGORIES.items() if v is not None]
    for i, (name, folder) in enumerate(category_items):
        with cols[i % 3]:
            count = len(list_files(folder))
            st.metric(label=name, value=f"{count} dokument")

else:
    folder = CATEGORIES[selected_page]

    # ── Session state for selected article ────────────────────────────────────
    state_key = f"selected_{folder}"
    if state_key not in st.session_state:
        st.session_state[state_key] = None

    files = list_files(folder)

    if not files:
        st.info(f"Inga dokument hittades i kategorin **{selected_page}**.")
    else:
        col_list, col_content = st.columns([1, 2], gap="large")

        with col_list:
            st.subheader(selected_page)
            st.markdown("<hr>", unsafe_allow_html=True)
            for filename in files:
                if st.button(format_title(filename), key=f"btn_{folder}_{filename}"):
                    st.session_state[state_key] = filename

        with col_content:
            chosen = st.session_state[state_key]
            if chosen is None:
                st.markdown(
                    f"<p style='color:#888; font-style:italic; margin-top:3rem;'>"
                    f"Välj ett dokument från listan till vänster för att läsa det."
                    f"</p>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="category-badge">{selected_page}</div>',
                    unsafe_allow_html=True,
                )
                st.subheader(format_title(chosen))
                content = read_file(folder, chosen)
                st.markdown(
                    f'<div class="article-content">{content}</div>',
                    unsafe_allow_html=True,
                )
