"""Shared theme, file loaders, and UI helpers.

Every file-backed cache key includes modification metadata. Pages must use these
helpers instead of reading project data directly.
"""

from __future__ import annotations

import base64
import html
import json
import unicodedata
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
PROCESSED = DATA / "processed"

ORANGE = "#F36B21"
ORANGE_DARK = "#C84C0C"
NAVY = "#071521"
NAVY_2 = "#0B1F30"
PANEL = "#0D2233"
INK = "#F4F7FA"
MUTED = "#91A4B5"
GRID = "#20394B"

PLOT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": MUTED, "size": 12},
    "margin": {"l": 12, "r": 12, "t": 38, "b": 12},
}


def _file_key(path: Path) -> tuple[str, int, int]:
    resolved = path.resolve()
    if not resolved.exists():
        return str(resolved), 0, 0
    stat = resolved.stat()
    return str(resolved), stat.st_mtime_ns, stat.st_size


@st.cache_data(show_spinner=False)
def _read_json_cached(path_str: str, mtime_ns: int, size: int) -> Any:
    del mtime_ns, size
    path = Path(path_str)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def load_json(path: Path) -> Any:
    """Load JSON with path, nanosecond mtime, and size in the cache key."""
    return _read_json_cached(*_file_key(path))


@st.cache_data(show_spinner=False)
def _read_parquet_cached(path_str: str, mtime_ns: int, size: int) -> pd.DataFrame:
    del mtime_ns, size
    path = Path(path_str)
    return pd.read_parquet(path) if path.exists() else pd.DataFrame()


def load_parquet(path: Path) -> pd.DataFrame:
    """Load Parquet with file modification metadata in the cache key."""
    return _read_parquet_cached(*_file_key(path))


@st.cache_data(show_spinner=False)
def _read_image_cached(path_str: str, mtime_ns: int, size: int) -> str:
    del mtime_ns, size
    path = Path(path_str)
    if not path.exists():
        return ""
    mime = {
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "image/jpeg")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def image_data_uri(path: Path) -> str:
    """Load an image as a data URI with modification-aware caching."""
    return _read_image_cached(*_file_key(path))


def directory_key(path: Path, pattern: str = "*") -> tuple[tuple[str, int, int], ...]:
    """Stable directory cache key from relative names, mtimes, and file sizes."""
    if not path.exists():
        return ()
    items = []
    for file in sorted(p for p in path.glob(pattern) if p.is_file()):
        stat = file.stat()
        items.append((file.relative_to(path).as_posix(), stat.st_mtime_ns, stat.st_size))
    return tuple(items)


def normalize_name(value: str) -> str:
    """Conservative display-name normalization; never resolves identity by itself."""
    normalized = unicodedata.normalize("NFKC", str(value)).strip()
    return " ".join(normalized.split())


def innings_to_outs(value: str | int | float) -> int:
    """Convert baseball innings such as ``2394 2/3`` to outs."""
    if isinstance(value, int):
        return value * 3
    text = str(value).strip()
    if not text:
        raise ValueError("innings cannot be empty")
    if " " in text:
        whole, fraction = text.split(maxsplit=1)
    else:
        whole, fraction = text, "0"
    fraction_outs = {"0": 0, "1/3": 1, "2/3": 2}.get(fraction)
    if fraction_outs is None:
        raise ValueError(f"invalid baseball innings: {value}")
    return int(whole) * 3 + fraction_outs


def format_innings(outs: int) -> str:
    whole, remainder = divmod(int(outs), 3)
    return str(whole) if remainder == 0 else f"{whole} {remainder}/3"


def metric_cards(items: Iterable[tuple[str, str, str]]) -> str:
    cards = []
    for label, value, note in items:
        cards.append(
            '<div class="metric-card">'
            f'<div class="metric-label">{html.escape(label)}</div>'
            f'<div class="metric-value">{html.escape(value)}</div>'
            f'<div class="metric-note">{html.escape(note)}</div></div>'
        )
    return '<div class="metric-grid">' + "".join(cards) + "</div>"


CSS = """
<style>
:root{--orange:#F36B21;--orange-dark:#C84C0C;--navy:#071521;--navy2:#0B1F30;
      --panel:#0D2233;--ink:#F4F7FA;--muted:#91A4B5;--grid:#20394B;}
[data-testid="stAppViewContainer"]{background:
  radial-gradient(900px 520px at 74% -12%,rgba(243,107,33,.16),transparent 62%),
  linear-gradient(180deg,#06121d 0%,#071521 100%);}
[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:1.35rem;max-width:1480px;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#06131f,#081a28);
  border-right:1px solid var(--grid);}
.side-brand{position:fixed;left:1rem;top:.9rem;width:14.5rem;padding:.8rem .7rem 1rem;
  border-bottom:1px solid var(--grid);z-index:5;background:#06131f;}
.side-eyebrow{color:var(--orange);font-size:.67rem;font-weight:800;letter-spacing:.2em;}
.side-title{color:var(--ink);font-weight:900;font-size:1.05rem;margin:.3rem 0;}
.side-sub{color:var(--muted);font-size:.73rem;line-height:1.55;}
[data-testid="stSidebarNav"]{padding-top:8.2rem;}
[data-testid="stSidebarNav"] li{margin:.14rem .55rem;border-radius:8px;overflow:hidden;}
[data-testid="stSidebarNav"] a{min-height:2.8rem;border-radius:8px;}
[data-testid="stSidebarNav"] a[aria-current="page"]{background:linear-gradient(90deg,#e95208,#ff7627)!important;
  color:white!important;font-weight:800;box-shadow:0 8px 22px rgba(232,82,8,.2);}
.hero{position:relative;overflow:hidden;border:1px solid var(--grid);border-radius:16px;
  padding:2.4rem 2.7rem;min-height:250px;display:flex;flex-direction:column;justify-content:center;
  background:linear-gradient(112deg,#091c2b 0%,#071521 55%,#4b1907 130%);margin-bottom:1.25rem;}
.hero:before{content:"";position:absolute;inset:0;background:
  repeating-linear-gradient(132deg,transparent 0 70px,rgba(243,107,33,.045) 71px 73px);}
.hero:after{content:"";position:absolute;right:-55px;top:-100px;width:340px;height:450px;
  border:34px solid rgba(243,107,33,.1);transform:rotate(20deg);border-radius:48% 20% 52% 18%;}
.hero-kicker,.hero h1,.hero-copy,.accent-rule{position:relative;z-index:1;}
.hero-kicker{color:var(--orange);font-size:.7rem;letter-spacing:.22em;font-weight:850;}
.hero h1{color:var(--ink);font-size:clamp(2.15rem,4.2vw,4rem);letter-spacing:-.045em;
  margin:.35rem 0 .55rem;line-height:1.03;}
.hero-copy{color:#c3d0da;max-width:720px;font-size:.97rem;line-height:1.7;}
.accent-rule{width:92px;height:5px;border-radius:8px;background:var(--orange);margin-top:1.1rem;}
.section{color:var(--ink);font-weight:850;font-size:1rem;margin:1.8rem 0 .75rem;
  display:flex;align-items:center;gap:.65rem;}
.section:before{content:"";width:22px;height:5px;border-radius:4px;background:var(--orange);}
.lede{color:var(--muted);font-size:.88rem;line-height:1.75;margin-bottom:1rem;}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem;}
.metric-card{background:linear-gradient(145deg,var(--panel),#091b29);border:1px solid var(--grid);
  border-top:3px solid var(--orange);border-radius:12px;padding:1rem 1.1rem;min-height:105px;}
.metric-label{color:var(--muted);font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;}
.metric-value{color:var(--ink);font-size:1.72rem;font-weight:900;margin:.28rem 0 .15rem;}
.metric-note{color:var(--muted);font-size:.72rem;}
.museum-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.85rem;}
.museum-card{position:relative;overflow:hidden;border-radius:15px;border:1px solid var(--grid);
  background:linear-gradient(155deg,#10293c,#081724);padding:1.25rem;min-height:220px;}
.museum-card:after{content:attr(data-number);position:absolute;right:-3px;bottom:-30px;
  color:rgba(243,107,33,.12);font-size:9rem;font-weight:950;line-height:1;}
.museum-no{color:var(--orange);font-size:2.6rem;font-weight:950;line-height:1;}
.museum-name{color:var(--ink);font-size:1.12rem;font-weight:850;margin:.55rem 0 .2rem;}
.museum-role{color:var(--muted);font-size:.72rem;letter-spacing:.08em;}
.museum-line{height:1px;background:var(--grid);margin:.9rem 0;}
.museum-stat{color:#c9d5de;font-size:.78rem;line-height:1.7;position:relative;z-index:1;}
.timeline-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;}
.timeline-card{border:1px solid var(--grid);border-left:4px solid var(--orange);border-radius:12px;
  background:linear-gradient(145deg,var(--panel),#091925);padding:1rem 1.1rem;min-height:135px;}
.timeline-year{color:var(--orange);font-size:.67rem;letter-spacing:.14em;font-weight:850;}
.timeline-title{color:var(--ink);font-weight:820;margin:.35rem 0;}
.timeline-body{color:var(--muted);font-size:.78rem;line-height:1.65;}
.source-note{border-top:1px solid var(--grid);color:#71889a;font-size:.69rem;line-height:1.7;
  margin-top:2rem;padding-top:.85rem;}
.status-pill{display:inline-block;color:var(--orange);border:1px solid rgba(243,107,33,.45);
  border-radius:99px;padding:.2rem .55rem;font-size:.66rem;font-weight:800;letter-spacing:.08em;}

/* High-density command-center home */
.dc-topbar{display:flex;align-items:center;justify-content:space-between;margin:.1rem 0 .9rem;}
.dc-title{color:var(--ink);font-size:1.45rem;font-weight:920;letter-spacing:-.025em;}
.dc-title i{color:var(--orange);font-style:normal;}
.dc-badge{border:1px solid var(--grid);border-radius:7px;color:var(--muted);padding:.42rem .7rem;
  font-size:.68rem;letter-spacing:.09em;}
.dc-grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:.65rem;}
.dc-panel{position:relative;overflow:hidden;border:1px solid var(--grid);border-radius:12px;
  background:linear-gradient(145deg,#0b2132,#081725);min-width:0;}
.dc-hero{grid-column:span 7;min-height:330px;padding:2rem 2.15rem;display:flex;flex-direction:column;
  justify-content:center;background:radial-gradient(520px 300px at 82% 48%,rgba(243,107,33,.27),transparent 68%),
  linear-gradient(118deg,#0a2132 0%,#071521 58%,#461707 145%);}
.dc-hero:before{content:"E";position:absolute;right:3.2rem;top:50%;transform:translateY(-52%) rotate(-8deg);
  font-size:15rem;line-height:1;font-weight:950;font-style:italic;color:rgba(243,107,33,.16);
  text-shadow:0 0 60px rgba(243,107,33,.25);}
.dc-hero:after{content:"";position:absolute;right:-20%;bottom:-65%;width:90%;height:105%;
  border:2px solid rgba(243,107,33,.2);border-radius:50%;box-shadow:0 0 0 18px rgba(243,107,33,.035),
  0 0 0 42px rgba(243,107,33,.025);}
.dc-kicker{position:relative;color:var(--orange);font-size:.73rem;font-weight:850;letter-spacing:.13em;}
.dc-hero h1{position:relative;color:var(--ink);font-size:clamp(2.1rem,3.4vw,3.35rem);line-height:1.04;
  letter-spacing:-.05em;margin:.45rem 0 .35rem;max-width:620px;}
.dc-hero-sub{position:relative;color:var(--orange);font-size:1rem;font-weight:850;letter-spacing:.04em;}
.dc-record{position:relative;display:flex;align-items:center;gap:1.1rem;margin:1.45rem 0 1.3rem;}
.dc-mark{font-size:3.1rem;color:var(--orange);font-weight:950;font-style:italic;line-height:1;}
.dc-vline{width:1px;height:42px;background:var(--grid);}
.dc-record-main{color:var(--ink);font-weight:850;font-size:1rem;}
.dc-record-sub{color:var(--muted);font-size:.72rem;margin-top:.18rem;}
.dc-actions{position:relative;display:flex;gap:.6rem;}
.dc-btn{display:inline-flex;align-items:center;border-radius:7px;padding:.68rem 1rem;font-size:.76rem;
  font-weight:800;border:1px solid var(--grid);color:var(--ink);background:rgba(7,21,33,.55);}
.dc-btn-primary{background:var(--orange);border-color:var(--orange);color:#fff;}
.dc-btn:hover{border-color:var(--orange);color:#fff;transform:translateY(-1px);}
.dc-btn,.dc-link{text-decoration:none!important;transition:.16s ease;cursor:pointer;}
.dc-live{margin-top:.65rem;padding:1rem 1.1rem;display:grid;grid-template-columns:1.1fr 1fr 1fr .7fr;gap:1rem;align-items:center;}
.dc-live-main{display:flex;align-items:center;gap:.9rem;}
.dc-live-dot{width:.58rem;height:.58rem;border-radius:50%;background:#ff5a16;box-shadow:0 0 0 .3rem rgba(255,90,22,.12);}
.dc-live-title{font-size:1rem;font-weight:900;color:var(--ink);}.dc-live-title small{display:block;color:var(--muted);font-size:.67rem;font-weight:500;margin-top:.2rem;}
.dc-match{text-align:center;border-left:1px solid var(--line);}.dc-match b{display:block;font-size:1.05rem;color:var(--ink);}.dc-match span{font-size:.67rem;color:var(--muted);}
.dc-live-meta{text-align:right;font-size:.68rem;color:var(--muted);}.dc-live-meta b{display:block;color:var(--orange);font-size:.78rem;margin-bottom:.2rem;}
.dc-summary{grid-column:span 5;min-height:330px;padding:1.35rem 1.45rem;}
.dc-summary-top{display:grid;grid-template-columns:1fr 1.55fr;gap:1rem;padding-bottom:1.05rem;
  border-bottom:1px solid var(--grid);}
.dc-rank{border-right:1px solid var(--grid);}
.dc-label{color:#c7d1d9;font-size:.73rem;font-weight:750;}
.dc-rank-num{color:var(--orange);font-size:5.4rem;font-weight:950;line-height:.95;margin:.45rem 0 .1rem;}
.dc-rank-num small{font-size:1.1rem;color:var(--ink);margin-left:.2rem;}
.dc-muted{color:var(--muted);font-size:.68rem;}
.dc-big-record{color:var(--ink);font-size:1.65rem;font-weight:900;letter-spacing:-.04em;margin:.75rem 0 .65rem;white-space:nowrap;}
.dc-big-record span{color:var(--muted);font-size:.78rem;font-weight:500;margin-left:.25rem;}
.dc-rate{display:flex;align-items:center;gap:.7rem;color:var(--orange);font-size:1.45rem;font-weight:900;}
.dc-progress{height:6px;border-radius:5px;background:#213747;flex:1;overflow:hidden;}
.dc-progress i{display:block;height:100%;background:var(--orange);border-radius:5px;}
.dc-summary-bottom{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem;padding-top:1.05rem;}
.dc-mini b{display:block;color:var(--ink);font-size:1.22rem;margin-top:.28rem;}
.dc-mini span{color:var(--muted);font-size:.67rem;}
.dc-card{padding:1rem 1.05rem;min-height:248px;}
.dc-card-title{color:var(--ink);font-size:.82rem;font-weight:850;margin-bottom:.7rem;
  display:flex;justify-content:space-between;align-items:center;}
.dc-card-title span{color:var(--muted);font-size:.62rem;font-weight:500;}
.dc-season{grid-column:span 3;}.dc-legends{grid-column:span 3;}.dc-pitch{grid-column:span 3;}
.dc-museum{grid-column:span 3;min-height:248px;padding:1.2rem;
  background:radial-gradient(230px 190px at 80% 25%,rgba(243,107,33,.2),transparent 72%),
  linear-gradient(145deg,#241209,#0a1925 70%);border-color:rgba(243,107,33,.38);}
.dc-table{width:100%;border-collapse:collapse;font-size:.69rem;color:#c8d3dc;}
.dc-table th{text-align:left;color:var(--muted);font-weight:500;padding:.35rem .25rem;border-bottom:1px solid var(--grid);}
.dc-table td{padding:.47rem .25rem;border-bottom:1px solid rgba(32,57,75,.48);}
.dc-table tr.on{background:linear-gradient(90deg,rgba(243,107,33,.32),transparent);color:white;}
.dc-table strong{color:var(--orange);}
.dc-person{display:grid;grid-template-columns:1.5rem 1fr auto;align-items:center;gap:.55rem;
  padding:.58rem 0;border-bottom:1px solid rgba(32,57,75,.55);}
.dc-person-no{color:var(--orange);font-weight:900;}.dc-person-name{color:var(--ink);font-size:.74rem;font-weight:750;}
.dc-person-name small{display:block;color:var(--muted);font-size:.59rem;font-weight:500;margin-top:.12rem;}
.dc-person-stat{color:var(--orange);font-size:1.02rem;font-weight:900;}
.dc-attendance{grid-column:span 5;min-height:220px;}.dc-timeline{grid-column:span 4;min-height:220px;}
.dc-sources{grid-column:span 3;min-height:220px;}
.dc-statbar{display:grid;grid-template-columns:5.2rem 1fr 3.8rem;gap:.6rem;align-items:center;margin:.7rem 0;}
.dc-statbar label{color:var(--muted);font-size:.66rem;}.dc-statbar b{color:var(--ink);font-size:.74rem;text-align:right;}
.dc-statbar div{height:5px;background:#203747;border-radius:4px;overflow:hidden;}.dc-statbar i{display:block;height:100%;background:var(--orange);}
.dc-museum-no{font-size:3.4rem;font-weight:950;color:var(--orange);letter-spacing:.06em;margin:.6rem 0;}
.dc-museum-copy{color:#cbd5dd;font-size:.73rem;line-height:1.65;max-width:220px;}
.dc-link{color:var(--orange);font-size:.68rem;font-weight:800;margin-top:.85rem;}
.dc-event{display:grid;grid-template-columns:3.2rem 1fr;gap:.6rem;padding:.5rem 0;border-bottom:1px solid rgba(32,57,75,.5);}
.dc-event b{color:var(--orange);font-size:.68rem;}.dc-event span{color:#c9d3db;font-size:.68rem;line-height:1.5;}
.dc-source-line{padding:.48rem 0;border-bottom:1px solid rgba(32,57,75,.5);}
.dc-source-line b{display:block;color:var(--ink);font-size:.68rem;}.dc-source-line span{color:var(--muted);font-size:.59rem;}
@media(max-width:1050px){.metric-grid,.museum-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:700px){.metric-grid,.museum-grid,.timeline-grid{grid-template-columns:1fr;}
  .hero{padding:1.7rem 1.4rem;}.block-container{padding-left:1rem;padding-right:1rem;}}
@media(max-width:1100px){.dc-hero,.dc-summary{grid-column:span 12}.dc-season,.dc-legends,.dc-pitch,.dc-museum{grid-column:span 6}
  .dc-attendance,.dc-timeline,.dc-sources{grid-column:span 12}.dc-live{grid-template-columns:1fr 1fr}.dc-live-meta{text-align:left}}
@media(max-width:700px){.dc-season,.dc-legends,.dc-pitch,.dc-museum{grid-column:span 12}.dc-summary-top{grid-template-columns:1fr 1.4fr}
  .dc-hero{padding:1.55rem}.dc-hero:before{font-size:10rem;right:-1rem}.dc-topbar{align-items:flex-start;gap:.5rem}.dc-title{font-size:1.1rem}
  .dc-live{grid-template-columns:1fr}.dc-match{text-align:left;border-left:0;border-top:1px solid var(--line);padding-top:.7rem}}
</style>
"""


def setup_page() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.sidebar.markdown(
        """
        <div class="side-brand">
          <div class="side-eyebrow">RIDE THE STORM</div>
          <div class="side-title">EAGLES DATA CENTER</div>
          <div class="side-sub">기록을 계산하고, 역사를 보존하는<br>한화 이글스 데이터 박물관</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-kicker">{html.escape(kicker)}</div>
          <h1>{html.escape(title)}</h1>
          <div class="hero-copy">{html.escape(copy)}</div>
          <div class="accent-rule"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_footer(lines: Iterable[str]) -> None:
    joined = "<br>".join(html.escape(line) for line in lines)
    st.markdown(f'<div class="source-note">{joined}</div>', unsafe_allow_html=True)
