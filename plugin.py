"""
LTX Director — Wan2GP Plugin  (v1.2.9)
==============================
Changes in v1.2.9:
  - Generate Here progress now shows in ONE place only — the status area above
    the model selector. The duplicate progress readout at the bottom of the tab
    is gone; the bottom status line is reserved for Apply / Preview messages.
Changes in v1.2.8:
  - FIX (Generate Here did nothing after "admitted"): the handler chained
    submit_task().result(), which blocked the plugin worker BEFORE the WebUI
    queue could be pumped — so the job was admitted but never ran. Reworked to
    match WanGP's own video-process plugin: submit the task, then poll
    job.done while draining job.events for progress, and only call result()
    once the job is finished. The queue now pumps and generation actually runs.
  - NEW progress/status bar: while generating, the status area shows the live
    phase and a step-based progress bar (current/total steps), updated from the
    job's event stream, similar to the Video Generator's status.
  - NEW Category + "Resolution Budget (Pixels will be reallocated to preserve
    Inputs W/H ratio)" controls in Advanced → Misc, mirroring the Video
    Generator. The Category dropdown filters the resolution list; both are
    populated from the model via WanGP's own resolution helpers.
Changes in v1.2.7:
  - FIX (Sync froze the whole page): clicking "⟲ Sync values from current
    model" could lock every clickable element until a refresh. The sync handler
    could raise (or emit a malformed dropdown-choices update) into the event
    chain, which freezes the Gradio client. Both switch_model and
    refresh_advanced_from_model are now fully wrapped so they can NEVER raise —
    on any error they return a correctly-shaped no-op + a status message. All
    dropdown choices fed to updates are sanitised to clean (label, value)
    tuples first.
  - FIX (Quality tab disappeared): when sync ran without a resolvable model, the
    visibility logic hid model-gated tabs (incl. Quality). Sync now leaves tab
    and field visibility UNCHANGED when it can't resolve the active model, and
    only retargets visibility when the model is known. The Quality tab no longer
    vanishes.
Changes in v1.2.6:
  - FIX (page freeze / dead clicks): loading or recovering a saved job before
    touching anything could freeze EVERY clickable element until a page
    refresh. Cause: two handlers were registered on main_tabs.select, so they
    fired on every tab change across the whole app and ran heavy API calls
    (get_current_model_settings / get_model_def) synchronously; colliding with
    the restore flow errored the event chain and locked the Gradio client.
    Both tab-select auto-sync handlers are removed. The Advanced fields and
    LoRA / spatial dropdowns are now populated at build time and via the
    explicit "⟲ Sync values from current model" button, so they work
    immediately regardless of whether you restore first.
  - FIX (Generate Here: "Invalid filename ... You must provide at least one
    Reference Image"): the API queue needs image_refs / image_start as FILE
    PATHS, not PIL objects. Reference images are now written to temp PNGs and
    passed as paths for the Generate Here path (Apply to Generator still uses
    in-memory images).
  - Spatial Upsampling choices are also seeded at build time for the initial
    model, and perturbation_layers gained allow_custom_value.
Changes in v1.2.5:
  - FIX (Generate Here failed): the API queue rejected the task with
    "Settings must contain 'model_type'". The settings dict from
    get_current_model_settings didn't always include model_type, so it's now
    set explicitly from the active/selected model (with base_model_type filled
    from the model_def) before submitting.
  - Post Processing → Spatial Upsampling now lists the REAL options: method and
    scale choices are pulled live from WanGP's upsampler API
    (postprocessing.upsamplers) for the selected model, including model VAE
    upsamplers, instead of a short hard-coded list.
  - Plugin list entry cleaned up: the description is now a short "what it does"
    line (no per-version changelog), matching plugin_info.json.
Changes in v1.2.4:
  - FIX (crash): the LoRA strength sliders used Gradio's @gr.render to build
    sliders dynamically, which registered event handlers that aren't part of
    the session's queue config under WanGP's plugin event-wrapping — moving a
    slider raised "KeyError: <n>" in gradio/queueing.py and 500'd the request.
    Replaced with a FIXED POOL of pre-built slider rows (12 LoRAs x 3 phases)
    that are shown / hidden / relabelled by static handlers — no dynamic event
    creation, so it no longer crashes. Behaviour is the same: one slider per
    guidance phase per selected LoRA, writing "1;1 1;1"-style multipliers.
  - FIX (warning): every Advanced dropdown that receives a live model value now
    sets allow_custom_value=True, silencing the "value ... is not in the list
    of choices" warnings when a model reports an option this clone doesn't list.
Changes in v1.2.3:
  - LoRAs are now folder-grouped like the original: the selector uses WanGP's
    native HierarchySelector (the same widget the Video Generator uses), built
    from the model's LoRA folder, so sub-folders are preserved instead of a
    flat list. Falls back to a flat multiselect dropdown only if that widget
    can't be imported.
  - Multipliers string format corrected to match WanGP and read left-to-right:
    LoRAs are separated by SPACES on one line, phases within a LoRA by ';'.
    Two LoRAs at two phases now reads "1;1 1;1" (was newline-separated before).
    Selecting LoRAs auto-seeds this box with the default grid, preserving any
    values already typed for LoRAs that stay selected; parsing accepts both the
    space and newline forms.
Changes in v1.2.2:
  - LoRAs tab reworked so it actually works: the Activated LoRAs list is now
    filled at tab-build time for the current model (and refreshed on model
    switch / sync) from the model's LoRA folder via the get_lora_dir global,
    so the dropdown opens with real choices and you can select as many as you
    want.
  - NEW per-LoRA strength sliders (default ON, hideable): a "Show strength
    sliders" checkbox whose state is SAVED to config and restored next
    session. When on, each selected LoRA gets one slider PER guidance phase —
    1 phase = 1 bar, 2 phases = 2 bars, 3 = 3 — driven by the General tab's
    Guidance Phases value. Sliders (0.0–2.0, default 1.0) write a WanGP-format
    multipliers string ("1.0;0.8" per line, ';' separating phases) into the
    still-editable LoRAs Multipliers box; existing text seeds the sliders so
    toggling doesn't lose values.
  - activated_loras + loras_multipliers are now passed into Generate Here so
    LoRA selections and strengths actually reach generation.
  - Confirmed joyai_echo is correctly treated as an LTX-2 (22B-class) finetune
    in the model dropdown.
Changes in v1.2.1:
  - FIX: the Advanced → LoRAs dropdown was empty and didn't open. It now
    fills from the selected model's LoRA folder (via the get_lora_dir global,
    the same source the Downloads plugin uses) whenever you switch models /
    sync, and is filterable like the original.
  - FIX: the Post Processing → Spatial Upsampling dropdown showed no options;
    it now offers the common methods (None / Lanczos / Lanczos x1.5 / x2) with
    a scale selector, and accepts custom values.
  - LAYOUT: Save/Load buttons are now aligned. The Session rows use equal-height
    rows with bottom-aligned buttons (📂 Browse / 💾 Save, 🔄 Recover / ⟲ Sync
    Windows, 📄 Browse File / 📥 Load Path) so they line up with their inputs
    instead of staggering.
  - LAYOUT: "🗑 Clear Timeline" moved directly under the timeline, ahead of the
    Generate / Apply / Preview actions.
  - Removed the "1:1 clone…" helper caption from the Advanced section.
Changes in v1.2.0:
  - NEW in-tab MODEL SELECTOR: a dropdown listing every LTX model the running
    WanGP exposes — both the LTX-Video (ltxv_13B) and LTX-2 (ltx2_19B /
    ltx2_22B / ltx2_22B_edit_anything / joyai_echo) families, plus any
    finetunes — populated live from the plugin API. Picking one switches the
    active WanGP model (writes model_choice_target the same way the Video
    Generator does). A ⟲ Refresh button re-scans available models.
  - ADVANCED section is now a model-reactive 1:1 CLONE of the Video
    Generator's Advanced form for LTX models, built in a new ltx_advanced.py.
    All 8 tabs are present (General, LoRAs, Steps Skipping, Post Processing,
    Audio, Quality, Sliding Window, Misc.) with the full LTX field union, and
    the fields/tabs shown adapt to the selected model exactly as WanGP does:
    e.g. LTX-Video 13B hides negative prompt / guidance phases / Quality tab,
    while LTX-2 22B shows guidance phases, audio + embedded guidance,
    perturbation, CFG-star, self-refiner, distilled-step samplers, etc.
    Visibility is derived from each model's model_def flags, so it stays
    correct across models and WanGP updates instead of being hard-coded.
  - Advanced values now feed generation by key (every managed key is written
    straight into the WanGP settings dict), replacing the previous fixed
    nine-field set.
  - UI FIX: the Load Session drop-zone was rendering dark-on-dark and looked
    invisible. Injected scoped CSS gives it (and the model row / advanced tab
    container) WanGP's native bordered, theme-aware surface so it's clearly
    visible in both light and dark themes.
Changes in v1.1.0:
  - NEW "🎬 Generate Here": generate the video directly from the LTX Director
    tab via WanGP's plugin generation API (api.submit_task) — no more
    transferring to the Video Generator tab and hunting for its Generate
    button. The job is queued into the live WebUI queue and the finished
    clip plays inline in a new result player on this tab. The original
    "▶ Apply to Generator" workflow is unchanged and still available; the
    old JS Apply+Generate relay is kept as a fallback for older WanGP builds
    that lack the plugin gen API (the Generate Here button auto-disables
    there with an explanatory note).
  - NEW "⚙ Advanced generation settings" accordion mirroring the Video
    Generator's Advanced controls as native widgets: inference steps, seed,
    guidance scale, flow shift, resolution, generations-per-run, negative
    prompt, and sliding-window size/overlap. Values auto-sync from the
    current model on tab open (and via "⟲ Sync from current model"), and are
    merged into the settings used by both Generate Here and Apply.
  - LAYOUT overhaul to reduce clutter as features grow: primary actions
    (Generate Here / Apply / Preview / Stop) now sit in one clear row right
    under the timeline; the save/load/recover controls moved into a
    collapsed "💾 Session" accordion; Advanced lives in its own collapsed
    accordion. Less scrolling, clearer hierarchy.
  - Internal: settings-building logic refactored into one shared
    _assemble_settings() used by both Apply and Generate Here, so the two
    paths can never drift apart.
Changes in v1.0.15:
  - Save folder "📂 Browse…" button is now reliably visible: the save
    controls were split into two rows (Save / Load) and the button given a
    real min-width instead of scale=0, which Gradio could collapse to
    nothing in a crowded row. It opens the same native OS folder picker the
    Load side uses. Load-side buttons sized to match.
  - Removed the redundant "✓ Apply" button from the timeline toolbar. It
    only re-ran the auto-commit that already fires on every edit, and its
    label wrongly implied it sent settings to the generator — the real
    transfer is the "▶ Apply to Generator" button below the timeline.
Changes in v1.0.14:
  - Sliding-window (PW) prompt format corrected to WanGP's expected shape:
    time-coded lines are KEPT and grouped per window, with a BLANK LINE
    between windows, e.g.
        [15.02s:19.00s] do something
        [19.00s:19.99s] do something
        <blank line>
        [20.00s:21.02s] do something
    Segments are assigned to the window containing their START frame
    (starts inside an overlap region go to the later window); the global
    prompt becomes the first line of every window paragraph; empty windows
    repeat the previous paragraph so the window↔paragraph mapping never
    shifts. Time tags now use the segment's ACTUAL timeline times in both
    PW and FG modes.
  - Duplicate-install detector: if the old wan2gp-whatdreamscost folder is
    still present alongside the renamed one, every element ID exists twice
    and Apply reads the wrong (empty) hidden fields — prompts silently stop
    transferring. The bridge now detects this and shows a red banner with
    the fix (delete the old folder, restart Wan2GP).
Changes in v1.0.13:
  - Distribution folder renamed: wan2gp-whatdreamscost → "Wan2GP - LTX
    Director" (verified safe with WanGP's importlib-based plugin loader).
    IMPORTANT when upgrading: DELETE the old wan2gp-whatdreamscost folder
    (two copies would load two tabs with clashing element IDs and break
    the JS bridge), MOVE ltx_director_autosave.zip / .json and
    ltx_director_config.json from the old folder into the new one so
    Recover Last and your saved settings survive, and re-enable the
    plugin under its new name in WanGP's plugin manager.
Changes in v1.0.12:
  - Load/Save status messages now include the running plugin version, so a
    stale install (old code still loaded because Wan2GP wasn't restarted)
    is immediately visible instead of masquerading as a recurring bug.
Changes in v1.0.11:
  - FIXED loading large legacy sessions. Diagnosis: the session .json was
    fine on disk (50 MB, valid) but GRADIO'S UPLOAD CACHE delivered a
    0-byte copy to the server — the same root cause behind both the
    earlier "Expecting value: char 0" error and the "empty (0 bytes)"
    message. Fixes:
      * NEW "Load from path" row: paste a file path (or 📄 Browse File…
        native picker) and the session is read DIRECTLY from disk — no
        browser upload, works for any size, immune to the cache bug.
        Pre-filled with the legacy autosave path when one exists; last
        used path remembered in config.
      * 0-byte uploads now retry briefly (flush race) then explain the
        cache problem and point to the path loader instead of failing
        with a generic parser error.
Changes in v1.0.10:
  - FIXED "Load failed: Expecting value: line 1 column 1 (char 0)" on
    legacy .json sessions. Root cause: a UTF-8 BOM at the start of the
    file (added silently by Windows Notepad "UTF-8 with BOM", PowerShell
    redirects, and some editors) reached json.loads. The loader now
    handles UTF-8 BOM, UTF-16 (Notepad "Unicode"), double-encoded legacy
    autosaves, zip sessions misnamed as .json (detected by PK magic),
    empty files, and missing files — each with a clear diagnostic message
    showing what the file actually starts with instead of a cryptic
    parser error. List-style file objects from newer Gradio versions are
    handled too, and JSON inside session zips / the config file is read
    BOM-tolerantly as well.
Changes in v1.0.9:
  - LTX 2.3 frame-grid snapping for sliding windows (verified against
    wgp.py's ltxv slider definitions: size min 41 step 8, overlap min 1
    step 8). The LTX VAE compresses time 8 frames per latent, so window
    size and overlap must be 8k+1 values; typed values now snap to the
    nearest valid one with a status note (e.g. 415 → 417, 15 → 17), and
    each window after the first contributes size − overlap NEW frames
    (417/17 → 400). Snapping is applied identically in the toolbar, the
    generator sync, session restore, Preview, and Apply (midpoint rounding
    matched between JS and Python).
  - Toolbar readout "→ N win × M new" and per-band labels (W2 +400) show
    the windows count and the new-frame contribution at a glance; Preview
    reports it too.
Changes in v1.0.8:
  - NEW: Choose where sessions are saved. A "Save folder" field writes the
    zip directly to that folder (created if needed, remembered between runs
    in ltx_director_config.json), and "📂 Browse…" opens the NATIVE OS
    folder picker (run in a subprocess with a timeout so it can never hang
    the UI; on headless/remote servers it degrades to typing the path).
    The browser download link is still always offered, and the project name
    is remembered too. Autosave keeps its fixed location, unchanged.
Changes in v1.0.7:
  - FIXED "Save failed: 'str' object has no attribute 'get'": the browser
    bridge double-encoded the timeline JSON (JSON.stringify of an already
    stringified blob). Fixed at the source AND all Python consumers now
    unwrap double-encoded payloads defensively (_parse_timeline), so stale
    sessions from older builds still load. This also repairs the bridge's
    fps/duration hidden-box sync, which the same bug had silently broken.
  - NEW: Project name field — saved files are now named
    <project>_<YYYY-MM-DD>_<HH-MM-SS>.zip; the project name is stored in
    the session and restored on Load / Recover; names are sanitized for
    filesystem safety
Changes in v1.0.6:
  - Sliding-window settings now SYNC FROM the Video Generator: on opening
    the LTX Director tab (and via the "⟲ Sync Window Settings" button) the
    timeline toolbar adopts the generator's Sliding Window Size / Window
    Frames Overlap values; Apply continues to push timeline → generator
  - Branded header: version number + "created by The-ShadowWalker" with logo
    (tab name unchanged)
Changes in v1.0.5:
  - Sliding-window relay now matches WanGP exactly (verified against wgp.py):
      * settings keys: sliding_window_size / sliding_window_overlap
        (Advanced → Sliding Window tab) are set from the timeline toolbar
      * "How to Process each Line of the Text Prompt" is set automatically:
          PW ("Each Paragraph Separated by an Empty line will be used for a
              new Sliding Window of the same Video Generation") when
              video_length > sliding_window_size
          FG ("All the Lines are Part of the Same Prompt") otherwise
      * In PW mode the prompt is rebuilt as ONE PARAGRAPH PER WINDOW
        (blank-line separated); empty windows repeat the previous paragraph
        so window→paragraph mapping never shifts
  - Audio playback: Play now actually plays sound (Web Audio engine with
    per-clip scheduling, trim offsets, seek-resync, loop restart)
  - Real waveforms: peaks are computed from the decoded audio in source
    space per pixel column, so zooming in reveals true waveform detail
  - Session save is now a .zip: timeline.json + assets/, with every unique
    image/audio file stored EXACTLY ONCE (sha256 content dedup) no matter
    how many timeline placements reference it; load accepts .zip and
    legacy .json; autosave/recover use the zip format too
Changes in v1.0.4:
  - FIXED zoom: segment widths used the position converter (subtracts view
    origin) — they shrank to slivers while the ruler moved
  - FIXED zoomed hit-testing, ruler tick density, drag rounding jitter
  - Sliding-window bands, overlap highlight, boundary warnings with
    Trim / Move / Split / Split-All fixes
"""

import os
import json
import math
import base64
import io as _io
import tempfile
import traceback
import logging
from pathlib import Path

import gradio as gr

from shared.utils.plugins import WAN2GPPlugin

log = logging.getLogger(__name__)

PlugIn_Id   = "LTXDirector"
PlugIn_Name = "LTX Director"

PLUGIN_VERSION = "1.2.9"

PLUGIN_DIR       = Path(__file__).parent
MH_LOGO_PATH     = PLUGIN_DIR / "assets" / "mh_logo.jpg"
CONFIG_PATH      = PLUGIN_DIR / "ltx_director_config.json"


def _load_config() -> dict:
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return {}


def _save_config(cfg: dict) -> None:
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception as exc:
        log.warning("Could not persist config: %s", exc)
AUTOSAVE_PATH    = PLUGIN_DIR / "ltx_director_autosave.json"        # legacy (read-only fallback)
AUTOSAVE_ZIP     = PLUGIN_DIR / "ltx_director_autosave.zip"


# ---------------------------------------------------------------------------
# ZIP session format
# ---------------------------------------------------------------------------
# A session .zip contains:
#   timeline.json            — full payload; media replaced by refs
#   assets/img_<hash>.<ext>  — each unique image stored EXACTLY ONCE
#   assets/aud_<hash>.<ext>  — each unique audio clip stored exactly once
# Segments reference media via "imageRef"/"audioRef" (the in-zip path), so an
# image reused at five places on the timeline is stored a single time and the
# JSON carries all five placements.

import hashlib as _hashlib
import zipfile as _zipfile
import copy as _copy

_MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "png",  "image/png"),
    (b"\xff\xd8\xff",      "jpg",  "image/jpeg"),
    (b"GIF87a",            "gif",  "image/gif"),
    (b"GIF89a",            "gif",  "image/gif"),
    (b"RIFF",              "webp", "image/webp"),   # RIFF....WEBP
    (b"ID3",               "mp3",  "audio/mpeg"),
    (b"\xff\xfb",          "mp3",  "audio/mpeg"),
    (b"\xff\xf3",          "mp3",  "audio/mpeg"),
    (b"OggS",              "ogg",  "audio/ogg"),
    (b"fLaC",              "flac", "audio/flac"),
]

def _sniff(data: bytes, kind: str):
    """Return (ext, mime) from magic bytes; fall back per media kind."""
    for magic, ext, mime in _MAGIC:
        if data.startswith(magic):
            if ext == "webp" and data[8:12] != b"WEBP":
                continue
            return ext, mime
    if data[4:8] == b"ftyp":                      # mp4/m4a container
        return ("m4a", "audio/mp4") if kind == "audio" else ("mp4", "video/mp4")
    if data.startswith(b"RIFF") and data[8:12] == b"WAVE":
        return "wav", "audio/wav"
    return ("png", "image/png") if kind == "image" else ("mp3", "audio/mpeg")

def _b64_to_bytes(b64str: str) -> bytes:
    if "," in b64str:
        b64str = b64str.split(",", 1)[1]
    return base64.b64decode(b64str)

def _bytes_to_data_uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def _write_session_zip(zip_path, payload: dict) -> dict:
    """
    Write the session as a zip. Media (imageB64/audioB64) is extracted into
    assets/, DEDUPLICATED by sha256 content hash, and replaced in the JSON by
    imageRef/audioRef. Returns stats {images, audio, bytes_saved}.
    """
    payload = _copy.deepcopy(payload)
    tl = payload.get("timeline", {}) or {}
    seen: dict = {}            # sha256 → (ref, nbytes)
    stats = {"images": 0, "audio": 0, "dup_hits": 0, "bytes_saved": 0}

    def extern(seg: dict, b64_key: str, ref_key: str, kind: str, zf):
        b64 = seg.get(b64_key, "")
        if not b64:
            return
        try:
            raw = _b64_to_bytes(b64)
        except Exception:
            return                          # leave inline if undecodable
        h = _hashlib.sha256(raw).hexdigest()[:16]
        if h in seen:
            stats["dup_hits"]  += 1
            stats["bytes_saved"] += seen[h][1]
        else:
            ext, _mime = _sniff(raw, kind)
            ref = f"assets/{'img' if kind=='image' else 'aud'}_{h}.{ext}"
            zf.writestr(ref, raw)
            seen[h] = (ref, len(raw))
            stats["images" if kind == "image" else "audio"] += 1
        seg[ref_key] = seen[h][0]
        seg.pop(b64_key, None)

    with _zipfile.ZipFile(zip_path, "w", _zipfile.ZIP_DEFLATED) as zf:
        for seg in tl.get("segments", []):
            extern(seg, "imageB64", "imageRef", "image", zf)
        for seg in tl.get("audioSegments", []):
            extern(seg, "audioB64", "audioRef", "audio", zf)
        zf.writestr("timeline.json", json.dumps(payload, indent=2))
    return stats


def _read_session_zip(zip_path) -> dict:
    """Read a session zip and reinstate inline base64 data URIs from refs."""
    with _zipfile.ZipFile(zip_path, "r") as zf:
        payload = json.loads(zf.read("timeline.json").decode("utf-8-sig"))
        tl = payload.get("timeline", {}) or {}
        cache: dict = {}       # ref → data URI (an asset may be referenced N times)

        def intern(seg: dict, ref_key: str, b64_key: str, kind: str):
            ref = seg.get(ref_key, "")
            if not ref:
                return
            if ref not in cache:
                try:
                    raw = zf.read(ref)
                except KeyError:
                    log.warning("Session zip missing asset: %s", ref)
                    return
                _ext, mime = _sniff(raw, kind)
                cache[ref] = _bytes_to_data_uri(raw, mime)
            seg[b64_key] = cache[ref]
            seg.pop(ref_key, None)

        for seg in tl.get("segments", []):
            intern(seg, "imageRef", "imageB64", "image")
        for seg in tl.get("audioSegments", []):
            intern(seg, "audioRef", "audioB64", "audio")
    return payload


_FOLDER_PICKER_CODE = (
    "import tkinter as tk\n"
    "from tkinter import filedialog\n"
    "r = tk.Tk(); r.withdraw()\n"
    "try: r.attributes('-topmost', True)\n"
    "except Exception: pass\n"
    "print(filedialog.askdirectory(title='Choose where to save LTX Director sessions') or '')\n"
)

_FILE_PICKER_CODE = (
    "import tkinter as tk\n"
    "from tkinter import filedialog\n"
    "r = tk.Tk(); r.withdraw()\n"
    "try: r.attributes('-topmost', True)\n"
    "except Exception: pass\n"
    "print(filedialog.askopenfilename(title='Choose an LTX Director session',"
    " filetypes=[('LTX sessions','*.zip *.json'),('All files','*.*')]) or '')\n"
)

def _run_native_picker(code: str) -> tuple:
    """Run a tkinter dialog in a SUBPROCESS (timeout 120s) so it can never
    freeze the Gradio worker. Returns (path_or_None, error_or_None)."""
    import subprocess, sys as _sys
    try:
        proc = subprocess.run(
            [_sys.executable, "-c", code],
            capture_output=True, text=True, timeout=120,
        )
        if proc.returncode != 0:
            return None, "Native picker unavailable on this system — type the path instead."
        path = (proc.stdout or "").strip()
        if not path:
            return None, None        # user cancelled — not an error
        return path, None
    except subprocess.TimeoutExpired:
        return None, "Picker timed out."
    except Exception as exc:
        return None, f"Picker unavailable ({exc}) — type the path instead."

def _pick_folder_native() -> tuple:
    """Native OS folder picker (see _run_native_picker)."""
    return _run_native_picker(_FOLDER_PICKER_CODE)

def _pick_file_native() -> tuple:
    """Native OS file-open picker for session files."""
    return _run_native_picker(_FILE_PICKER_CODE)


def _safe_project_name(name: str) -> str:
    """Sanitize a project name for use in filenames."""
    name = (name or "").strip() or "ltx_project"
    out = []
    for ch in name:
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        elif ch in " .":
            out.append("_")
        # anything else dropped
    safe = "".join(out).strip("_") or "ltx_project"
    return safe[:60]


def _read_text_smart(p: Path) -> str:
    """
    Read a text file tolerating real-world encodings:
      - UTF-8 with BOM (Windows Notepad "UTF-8 with BOM", PowerShell
        redirects, some editors) — the BOM otherwise lands in json.loads
        and fails with "Expecting value: line 1 column 1 (char 0)"
      - UTF-16 LE/BE with BOM (Notepad "Unicode")
      - plain UTF-8, with latin-1 as a last-resort fallback
    """
    raw = p.read_bytes()
    if not raw:
        raise ValueError(f"'{p.name}' is empty (0 bytes).")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _load_session_any(path) -> dict:
    """Load a session from .zip (new) or .json (legacy). Detects zips by
    CONTENT (PK magic), not just extension, and gives diagnostic errors."""
    p = Path(str(path))
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    # A 0-byte file here almost always means GRADIO'S UPLOAD CACHE served an
    # empty copy (a known failure mode with large uploads / stale cache
    # entries) — the original on disk is usually fine. Retry briefly in case
    # the upload is still flushing, then point the user at the path loader
    # which reads the file directly and bypasses the upload entirely.
    import time as _time
    for _ in range(4):
        if p.stat().st_size > 0:
            break
        _time.sleep(0.4)
    if p.stat().st_size == 0:
        raise ValueError(
            f"The uploaded copy of '{p.name}' arrived EMPTY (0 bytes) — this is a "
            f"browser/Gradio upload-cache problem with large files, not a problem "
            f"with your file. Use the 'Load from path' field instead: paste the "
            f"file's full path on this computer (or click 📄 Browse File…) and it "
            f"will be read directly from disk."
        )

    head = b""
    try:
        with open(p, "rb") as fh:
            head = fh.read(4)
    except Exception:
        pass

    # Zip session — by magic bytes, extension, or zipfile probe
    if head.startswith(b"PK") or str(p).lower().endswith(".zip") or _zipfile.is_zipfile(str(p)):
        return _read_session_zip(str(p))

    # Legacy JSON session
    text = _read_text_smart(p).strip()
    if not text:
        raise ValueError(f"'{p.name}' contains no data.")
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as e:
        preview = text[:60].replace("\n", "\\n")
        raise ValueError(
            f"'{p.name}' is not valid JSON ({e.msg} at char {e.pos}). "
            f"File starts with: {preview!r}"
        ) from None
    # A double-encoded legacy autosave is a JSON *string* — unwrap it
    if isinstance(loaded, str):
        try:
            loaded = json.loads(loaded)
        except Exception:
            raise ValueError(f"'{p.name}' decodes to a string, not a session object.")
    if not isinstance(loaded, dict):
        raise ValueError(f"'{p.name}' does not contain a session object (got {type(loaded).__name__}).")
    return loaded


# ---------------------------------------------------------------------------
# Audio mixing
# ---------------------------------------------------------------------------

def _parse_timeline(tdata) -> dict:
    """
    Parse timeline JSON robustly. The browser bridge historically
    double-encoded the payload (JSON.stringify of an already-stringified
    blob), so json.loads could yield a *string* instead of a dict. Unwrap
    up to 3 layers; always return a dict.
    """
    data = tdata
    for _ in range(3):
        if isinstance(data, dict):
            return data
        if isinstance(data, str):
            s = data.strip()
            if not s:
                return {}
            try:
                data = json.loads(s)
            except Exception:
                return {}
        else:
            return {}
    return data if isinstance(data, dict) else {}


def _build_combined_audio(timeline_data_str: str, duration_frames: int, frame_rate: float):
    try:
        import torch, av
    except ImportError:
        return None

    target_sr = 44100
    total_samples = max(1, int(math.ceil(duration_frames / max(frame_rate, 1) * target_sr)))
    empty = {"waveform": torch.zeros((1, 2, total_samples), dtype=torch.float32), "sample_rate": target_sr}

    if not timeline_data_str:
        return empty
    data = _parse_timeline(timeline_data_str)
    audio_segs = data.get("audioSegments", [])
    if not audio_segs:
        return empty

    import torch
    out = torch.zeros((2, total_samples), dtype=torch.float32)

    for seg in audio_segs:
        b64 = seg.get("audioB64", "")
        if not b64:
            continue
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        try:
            audio_bytes = base64.b64decode(b64)
            buf = _io.BytesIO(audio_bytes)
            clip_frames = []
            with av.open(buf) as container:
                stream = container.streams.audio[0]
                resampler = av.AudioResampler(format="fltp", layout="stereo", rate=target_sr)
                for frame in container.decode(stream):
                    for rf in resampler.resample(frame):
                        clip_frames.append(torch.from_numpy(rf.to_ndarray()))
                for rf in resampler.resample(None):
                    clip_frames.append(torch.from_numpy(rf.to_ndarray()))
            if not clip_frames:
                continue
            waveform = torch.cat(clip_frames, dim=1)
            trim_start_f = float(seg.get("trimStart", 0))
            length_f     = float(seg.get("length", 1))
            start_f      = float(seg.get("start", 0))
            src_start = int(trim_start_f / frame_rate * target_sr)
            src_end   = min(src_start + int(length_f / frame_rate * target_sr), waveform.shape[1])
            actual_len = src_end - src_start
            if actual_len <= 0:
                continue
            clip = waveform[:, src_start:src_end]
            dst_start = int(start_f / frame_rate * target_sr)
            if dst_start >= out.shape[1]:
                continue
            dst_end = min(dst_start + actual_len, out.shape[1])
            clip = clip[:, : dst_end - dst_start]
            out[:, dst_start:dst_end] += clip
        except Exception as e:
            log.warning("Audio mix error: %s", e)

    return {"waveform": out.unsqueeze(0), "sample_rate": target_sr}


# ---------------------------------------------------------------------------
# Prompt relay builder
# ---------------------------------------------------------------------------

def _snap_ltx_frames(v, minimum: int = 1, maximum: int = None) -> int:
    """
    Snap a frame count to the nearest valid LTX 2.3 value: 8k+1.
    The LTX VAE compresses time 8 frames per latent, so window size
    (min 41), overlap (1..97) and total frame counts must all be 8k+1
    — matching WanGP's Sliding Window sliders (min 41 step 8 / min 1 step 8).
    New frames per window = size - overlap, always a multiple of 8
    (e.g. 417 - 17 = 400).
    """
    try:
        v = int(v)
    except Exception:
        v = minimum
    # floor(x + 0.5) == JS Math.round — keeps Python and the toolbar JS
    # identical at exact midpoints (Python's round() banker-rounds)
    snapped = math.floor((v - 1) / 8 + 0.5) * 8 + 1
    snapped = max(minimum, snapped)
    if maximum is not None:
        snapped = min(maximum, snapped)
    return snapped


def _snap_window_pair(win_size: int, win_overlap: int) -> tuple:
    """Snap (size, overlap) to valid LTX values with overlap < size."""
    ws = _snap_ltx_frames(win_size, 41)
    ov = _snap_ltx_frames(win_overlap, 1, 97)
    while ov >= ws and ov > 1:
        ov -= 8
    ov = max(1, ov)
    return ws, ov


def _compute_windows(total_frames: int, win_size: int, win_overlap: int):
    """Python mirror of the JS getWindows(): [{i, start, end}] per sliding window."""
    ws = max(8, int(win_size or 0))
    ov = max(0, min(int(win_overlap or 0), ws - 1))
    stride = ws - ov
    out, s, i = [], 0, 0
    while s < total_frames and i < 500:
        out.append({"i": i, "start": s, "end": min(s + ws, total_frames)})
        if s + ws >= total_frames:
            break
        s += stride
        i += 1
    return out


def _build_prompt_relay(timeline_json: str, global_prompt: str, fps: float,
                        total_frames: int = 0, win_size: int = 0, win_overlap: int = 0):
    """
    Build the prompt for WanGP.

    Returns (combined, local_prompts, segment_lengths, has_segs, prompt_mode):

    prompt_mode is the value for WanGP's "How to Process each Line of the
    Text Prompt" dropdown (settings key: multi_prompts_gen_type):
      "PW" — Each Paragraph Separated by an Empty line will be used for a new
             Sliding Window of the same Video Generation
             (used when total_frames > sliding_window_size: combined is one
              paragraph per window, separated by blank lines)
      "FG" — All the Lines are Part of the Same Prompt
             (used when the video fits in a single window)
    """
    data = _parse_timeline(timeline_json)

    segments = sorted(data.get("segments", []), key=lambda s: s.get("start", 0))
    if not segments:
        return global_prompt, "", "", False, "FG"

    prompts, lengths = [], []
    cursor, pending_gap = 0, 0

    for seg in segments:
        seg_start  = int(seg.get("start", 0))
        seg_length = int(seg.get("length", 1))
        prompt = (seg.get("prompt") or "").strip() or global_prompt.strip()

        if seg_start > cursor:
            gap = seg_start - cursor
            if lengths:
                lengths[-1] += gap
            else:
                pending_gap += gap

        lengths.append(seg_length + pending_gap)
        prompts.append(prompt)
        pending_gap = 0
        cursor = seg_start + seg_length

    local_prompts   = " | ".join(p or global_prompt.strip() or "video" for p in prompts)
    segment_lengths = ",".join(str(l) for l in lengths)

    def _time_line(seg) -> str:
        """One time-coded line with the segment's ACTUAL timeline times."""
        s = int(seg.get("start", 0))
        e = s + int(seg.get("length", 1))
        return f"[{s / max(fps, 1):.2f}s:{e / max(fps, 1):.2f}s] {(seg.get('prompt') or '').strip()}"

    gp = global_prompt.strip()

    # ── Sliding-window mode: time-coded lines GROUPED BY WINDOW, with a
    # BLANK LINE between windows (WanGP "PW": each paragraph separated by an
    # empty line = one sliding window). Example with a ~20s window:
    #   [15.02s:19.00s] do something
    #   [19.00s:19.99s] do something
    #   <blank>
    #   [20.00s:21.02s] do something
    use_windows = win_size > 0 and total_frames > win_size
    if use_windows:
        windows = _compute_windows(total_frames, win_size, win_overlap)
        stride  = max(1, win_size - max(0, min(win_overlap, win_size - 1)))
        n_win   = len(windows)

        groups = [[] for _ in range(n_win)]
        for seg in segments:
            if not (seg.get("prompt") or "").strip():
                continue
            start = int(seg.get("start", 0))
            if start >= total_frames:
                continue
            # A segment belongs to the window whose stride slot contains its
            # START frame (segments starting in an overlap region go to the
            # LATER window, matching how new content is generated).
            w_idx = min(n_win - 1, max(0, start // stride))
            groups[w_idx].append(_time_line(seg))

        paragraphs = []
        prev_text  = gp or "video"
        for lines_in_win in groups:
            if lines_in_win:
                body = "\n".join(lines_in_win)
                text = (gp + "\n" + body) if gp else body
                prev_text = text
            else:
                # An empty paragraph would shift every later window's mapping,
                # so repeat the previous window's text for continuity.
                text = prev_text
            paragraphs.append(text)

        combined = "\n\n".join(paragraphs)
        return combined, local_prompts, segment_lengths, True, "PW"

    # ── Single-window mode: time-coded lines, all part of one prompt ──────
    lines = [gp] if gp else []
    for seg in segments:
        if (seg.get("prompt") or "").strip():
            lines.append(_time_line(seg))

    combined = "\n".join(lines) if lines else (prompts[0] if prompts else "")
    return combined, local_prompts, segment_lengths, True, "FG"


# ---------------------------------------------------------------------------
# Plugin
# ---------------------------------------------------------------------------

class LTXDirectorPlugin(WAN2GPPlugin):
    def __init__(self):
        super().__init__()
        self.api            = None
        self._wangp_session = None
        self.has_gen_api    = False
        self._selected_model_type = ""
        self.name        = PlugIn_Name
        self.version     = PLUGIN_VERSION
        self.description = (
            "Timeline editor for LTX video generation: drag images, write "
            "per-segment prompts, and place audio clips on one canvas to direct "
            "LTX video output."
        )

    def setup_ui(self) -> None:
        self.request_component("state")
        self.request_component("refresh_form_trigger")
        self.request_component("main_tabs")
        self.request_component("generate_btn")
        # For the in-tab model selector: model_choice_target is the hidden Text
        # box WanGP watches to switch the active model; goto_model_type formats
        # the "<model_type>|<timestamp>" value that triggers the switch.
        self.request_component("model_choice_target")
        self.request_global("get_current_model_settings")
        self.request_global("get_lora_dir")
        self.add_custom_js(self._build_bridge_js())
        self.add_tab(
            tab_id=PlugIn_Id,
            label=PlugIn_Name,
            component_constructor=self.create_ui,
        )

    def create_ui(self, api=None, *args, **kwargs):
        # When the running WanGP build exposes the plugin generation API, the
        # PluginManager injects a GradioWanGPSession as the first positional arg
        # and runs this constructor inside session.plugin_ui_context(). Any
        # gr.Button.click whose handler references this session is then auto-
        # wrapped to queue the gen into the live WebUI queue and stream progress
        # — that is what powers the new "▶ Generate Here" button. On older builds
        # api is None and we fall back to the JS "Apply + Generate" bridge.
        # Store the injected session under BOTH a friendly name and the exact
        # attribute name (_wangp_session) that WanGP's plugin_ui_context uses to
        # detect api-driven button handlers. The detector wraps a gr.Button.click
        # only if its handler references self._wangp_session (or _api), so the
        # generate_here handler below reads self._wangp_session specifically.
        self.api = api
        self._wangp_session = api
        self.has_gen_api = api is not None

        gr.HTML(self._build_header_html())
        gr.Markdown(
            "Place **image keyframes**, **text prompts**, and **audio clips** on the timeline. "
            "Changes are **auto-saved** every few seconds so a page freeze won't lose your work."
        )

        # ── Hidden state fields written by iframe via postMessage ──────────
        with gr.Row(visible=False):
            timeline_data_box   = gr.Textbox(value="{}", elem_id="wdc_timeline_data")
            local_prompts_box   = gr.Textbox(value="",   elem_id="wdc_local_prompts")
            segment_lengths_box = gr.Textbox(value="",   elem_id="wdc_segment_lengths")
            guide_strength_box  = gr.Textbox(value="",   elem_id="wdc_guide_strength")
            frame_count_box     = gr.Textbox(value="121", elem_id="wdc_frame_count")
            fps_box      = gr.Number(value=24,    precision=0, elem_id="wdc_fps")
            duration_box = gr.Number(value=5.0,               elem_id="wdc_duration")
            frames_box   = gr.Number(value=121,   precision=0, elem_id="wdc_frames")
            epsilon_box  = gr.Number(value=0.001,             elem_id="wdc_epsilon")
            # Single-blob restore payload: the ENTIRE session dict written by
            # load_session / recover_last so the bridge JS can push it all into
            # the iframe in one shot without racing individual field updates.
            restore_payload_box = gr.Textbox(value="", elem_id="wdc_restore_payload")
            # Window-settings sync payload: written by sync_window_settings(),
            # pushed into the iframe by a JS .then() so the timeline toolbar
            # matches the Video Generator's Sliding Window tab.
            winsync_payload_box = gr.Textbox(value="", elem_id="wdc_winsync_payload")

        # ── Global prompt ──────────────────────────────────────────────────
        global_prompt_box = gr.Textbox(
            label="Global prompt (applies to entire video)",
            placeholder="high quality, cinematic…",
            lines=2,
        )

        # ── Timeline iframe ────────────────────────────────────────────────
        gr.HTML(
            value=self._build_editor_html(),
            elem_id="wdc_timeline_wrapper",
        )

        # Clear sits directly under the timeline, ahead of the action buttons.
        with gr.Row(elem_id="wdc-clear-row"):
            clear_btn_v = gr.Button("🗑 Clear Timeline", variant="secondary",
                                    scale=1, elem_id="wdc-clear-btn", min_width=160)

        _cfg = _load_config()

        # ═══════════════════════════════════════════════════════════════════
        #  PRIMARY ACTIONS  — the two ways to turn the timeline into a video.
        #  Both kept side by side so neither workflow is removed:
        #    • Apply to Generator → transfers settings to the Video Generator
        #      tab (the original behavior).
        #    • Generate Here      → queues the gen directly via the WanGP plugin
        #      API and streams the result into the inline player below, so you
        #      never have to leave this tab.
        # ═══════════════════════════════════════════════════════════════════
        with gr.Row(elem_id="wdc-primary-actions"):
            generate_here_btn = gr.Button(
                "🎬 Generate Here", variant="primary", scale=3,
                elem_id="wdc-generate-here-btn",
                interactive=self.has_gen_api,
            )
            apply_btn_v   = gr.Button("▶ Apply to Generator", variant="secondary", scale=2, elem_id="wdc-apply-btn")
            preview_btn_v = gr.Button("👁 Preview Schedule",   variant="secondary", scale=1, elem_id="wdc-preview-btn")
            cancel_here_btn = gr.Button(
                "⏹ Stop", variant="stop", scale=1,
                elem_id="wdc-cancel-here-btn", visible=self.has_gen_api,
            )

        if not self.has_gen_api:
            gr.Markdown(
                "ℹ️ *Direct **Generate Here** needs a WanGP build with the plugin "
                "generation API. On this build, use **Apply to Generator** then "
                "Generate on the Video Generator tab.*",
                elem_id="wdc-no-api-note",
            )

        # ── Inline result player (filled live by Generate Here) ────────────
        gen_status_md = gr.Markdown(visible=False, elem_id="wdc-gen-status")
        result_video  = gr.Video(
            label="Result", visible=False, interactive=False,
            elem_id="wdc-result-video", autoplay=True,
        )

        # ═══════════════════════════════════════════════════════════════════
        #  🎚 MODEL  +  ⚙ ADVANCED GENERATION SETTINGS
        #  The model dropdown lists every LTX model (LTX-Video + LTX-2 families
        #  and their finetunes) and switches the live WanGP model when changed.
        #  The Advanced section is a 1:1 clone of WanGP's Advanced form for LTX
        #  models, built once with the full field union and made model-reactive:
        #  selecting a model shows exactly the fields WanGP shows for it.
        # ═══════════════════════════════════════════════════════════════════
        # Import the model-reactive Advanced clone. Try relative (loaded as a
        # package by WanGP), then fall back to absolute (folder on sys.path).
        try:
            from . import ltx_advanced as _adv
        except Exception:
            import importlib, sys as _sys
            _sys.path.insert(0, str(PLUGIN_DIR))
            _adv = importlib.import_module("ltx_advanced")

        _ltx_models = self._list_ltx_models()
        _model_choices = [(m["label"], m["model_type"]) for m in _ltx_models]
        _model_value = _model_choices[0][1] if _model_choices else None
        if _model_value:
            self._selected_model_type = _model_value

        with gr.Row(elem_id="wdc-model-row"):
            model_selector = gr.Dropdown(
                choices=_model_choices, value=_model_value,
                label="🎚 Model (LTX only)", scale=4,
                elem_id="wdc-model-selector", interactive=self.has_gen_api,
                info="Switches the active WanGP model. Lists LTX-Video and LTX-2 models.",
            )
            refresh_models_btn = gr.Button(
                "⟲ Refresh", variant="secondary", scale=1,
                elem_id="wdc-refresh-models-btn", min_width=110,
            )
        model_status = gr.Markdown(elem_id="wdc-model-status")
        if not self.has_gen_api:
            gr.Markdown(
                "ℹ️ *Model switching needs the WanGP plugin API; on this build "
                "choose the model on the Video Generator tab.*",
                elem_id="wdc-model-note",
            )

        with gr.Accordion("⚙ Advanced generation settings", open=False, elem_id="wdc-advanced"):
            _initial_loras = self._list_loras_for_model(_model_value) if _model_value else []
            _init_sp_methods, _init_sp_ratios = (
                self._spatial_choices_for_model(_model_value) if _model_value else (None, None))
            adv_map, adv_tabs = _adv.build_advanced_ui(
                show_lora_sliders=bool(_cfg.get("lora_show_sliders", True)),
                initial_loras=_initial_loras,
                initial_spatial_methods=_init_sp_methods,
                initial_spatial_ratios=_init_sp_ratios)
            with gr.Row():
                refresh_adv_btn = gr.Button(
                    "⟲ Sync values from current model", variant="secondary",
                    elem_id="wdc-refresh-adv-btn", min_width=240,
                )
            adv_status = gr.Markdown(elem_id="wdc-adv-status")

        # Canonical ordered component list + tab list (used as handler I/O).
        adv_order = _adv.ADV_FIELD_ORDER
        adv_components = [adv_map[k] for k in adv_order if k in adv_map]
        adv_keys       = [k for k in adv_order if k in adv_map]
        adv_tab_keys   = list(adv_tabs.keys())
        adv_tab_comps  = [adv_tabs[k] for k in adv_tab_keys]
        loras_component = adv_map.get("loras_choices")
        _loras_is_hierarchy = bool(adv_map.get("_loras_is_hierarchy"))

        def _lora_update(loras, reset=False):
            """Build the correct Gradio update for the LoRA selector, which may
            be WanGP's HierarchySelector (needs a folder hierarchy) or a plain
            multiselect dropdown (needs choices)."""
            if _loras_is_hierarchy:
                try:
                    from shared.gradio.hierarchy_selector import build_choices_hierarchy as _bch
                    upd = {"hierarchy": _bch(list(loras or []))}
                except Exception:
                    upd = {}
            else:
                upd = {"choices": list(loras or [])}
            if reset:
                upd["value"] = []
            return gr.update(**upd)

        # ═══════════════════════════════════════════════════════════════════
        #  💾 SESSION  (save / load / recover — collapsed to declutter)
        # ═══════════════════════════════════════════════════════════════════
        with gr.Accordion("💾 Session — save, load & recover", open=False, elem_id="wdc-session"):
            # Save row — inputs on the left, action buttons grouped on the right.
            with gr.Row(equal_height=True, elem_id="wdc-save-row"):
                project_name_box = gr.Textbox(
                    label="Project name", value=_cfg.get("project_name", "ltx_project"), scale=3,
                    elem_id="wdc-project-name", max_lines=1,
                )
                save_folder_box = gr.Textbox(
                    label="Save folder", value=_cfg.get("save_folder", ""), scale=5,
                    elem_id="wdc-save-folder", max_lines=1,
                    placeholder="Leave empty for browser download only",
                )
                browse_btn = gr.Button("📂 Browse", variant="secondary", scale=1,
                                       elem_id="wdc-browse-btn", min_width=120)
                save_btn = gr.Button("💾 Save", variant="primary", scale=1,
                                     elem_id="wdc-save-btn", min_width=120)

            # Load row — upload box + action buttons aligned.
            with gr.Row(equal_height=True, elem_id="wdc-load-row"):
                load_file   = gr.File(label="Load Session (.zip / .json)", file_types=[".zip", ".json"], scale=5, elem_id="wdc-load-file")
                recover_btn = gr.Button("🔄 Recover Last", variant="secondary", scale=1,
                                        elem_id="wdc-recover-btn", min_width=140)
                winsync_btn = gr.Button("⟲ Sync Windows", variant="secondary", scale=1,
                                        elem_id="wdc-winsync-btn", min_width=140)
                dl_file     = gr.File(label="Download", visible=False, scale=1, elem_id="wdc-dl-file")

            # Load-from-path row — path box + browse/load buttons aligned.
            with gr.Row(equal_height=True, elem_id="wdc-loadpath-row"):
                load_path_box = gr.Textbox(
                    label="Load from path (reads directly from disk — for large sessions)",
                    value=_cfg.get("load_path", str(AUTOSAVE_PATH) if AUTOSAVE_PATH.exists() else ""),
                    placeholder=str(AUTOSAVE_PATH),
                    scale=6, max_lines=1, elem_id="wdc-load-path",
                )
                browse_file_btn = gr.Button("📄 Browse File", variant="secondary", scale=1,
                                            elem_id="wdc-browse-file-btn", min_width=140)
                load_path_btn   = gr.Button("📥 Load Path", variant="primary", scale=1,
                                            elem_id="wdc-load-path-btn", min_width=140)

        save_status = gr.Markdown()

        # ── Sync sliding-window settings: Video Generator → timeline ───────
        # On tab open (and on demand) the timeline toolbar adopts the values
        # currently shown in the generator's Advanced → Sliding Window tab,
        # so both sides always agree. Apply pushes timeline → generator.

        _WINSYNC_PUSH_JS = (
            "() => { try {"
            "  const root = window.gradioApp ? window.gradioApp() : (document.querySelector('gradio-app') || document);"
            "  const el = root.querySelector('#wdc_winsync_payload textarea, #wdc_winsync_payload input');"
            "  if (!el || !el.value) return;"
            "  const data = JSON.parse(el.value);"
            "  const fr = document.getElementById('wdc-timeline-iframe');"
            "  if (fr && fr.contentWindow) {"
            "    fr.contentWindow.postMessage({ source: 'wdc_parent', cmd: 'set_window_settings', data: data }, '*');"
            "  }"
            "} catch(e) { console.warn('[LTXDirector] winsync push error:', e); } }"
        )

        def sync_window_settings(state):
            """Read sliding window size/overlap from the generator settings."""
            try:
                settings = self.get_current_model_settings(state)
                ws = settings.get("sliding_window_size", None)
                ov = settings.get("sliding_window_overlap", None)
                if ws is None:
                    return "", "⚠️ Current model has no sliding window settings."
                payload = json.dumps({
                    "slidingWindowSize":    int(ws),
                    "slidingWindowOverlap": int(ov or 0),
                })
                return payload, f"⟲ Window settings synced from generator: size **{int(ws)}f**, overlap **{int(ov or 0)}f**."
            except Exception as e:
                log.warning("Window sync failed: %s", e)
                return "", f"⚠️ Window sync failed: {e}"

        winsync_btn.click(
            fn=sync_window_settings,
            inputs=[self.state],
            outputs=[winsync_payload_box, save_status],
        ).then(fn=None, inputs=[], outputs=[], js=_WINSYNC_PUSH_JS)

        # Note: window settings sync runs via the explicit "⟲ Sync Windows"
        # button. We deliberately do NOT auto-sync on tab-select — registering
        # heavy handlers on main_tabs.select fires them on every tab change
        # across the whole app, which could error mid-restore and freeze the
        # page (requiring a refresh). The manual button is reliable instead.

        # Hidden trigger buttons (Python handlers). apply/preview/clear are
        # fired by the JS bridge after it pulls fresh state from the iframe;
        # generate_here_trigger is fired the same way for the direct-gen path.
        apply_btn           = gr.Button("apply_trigger",         visible=False, elem_id="wdc-apply-trigger")
        generate_btn        = gr.Button("generate_trigger",      visible=False, elem_id="wdc-generate-trigger")
        generate_here_btn_h = gr.Button("generate_here_trigger", visible=False, elem_id="wdc-generate-here-trigger")
        preview_btn         = gr.Button("preview_trigger",       visible=False, elem_id="wdc-preview-trigger")
        clear_btn           = gr.Button("clear_trigger",         visible=False, elem_id="wdc-clear-trigger")

        schedule_md = gr.Markdown(visible=False)
        status_md   = gr.Markdown()

        # ── Save / Load / Recover handlers ────────────────────────────────

        def save_session(tdata, global_p, fps_val, dur_val, epsilon_val, project_name, save_folder):
            """Write the session zip. If a save folder is set, the file is
            written there directly; the browser download link is always
            offered as well. Autosave (fixed location) is untouched."""
            try:
                from datetime import datetime
                safe  = _safe_project_name(project_name)
                stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                fname = f"{safe}_{stamp}.zip"

                payload = {
                    "version": PLUGIN_VERSION,
                    "project_name": (project_name or "").strip() or "ltx_project",
                    "saved_at": stamp,
                    "global_prompt": global_p,
                    "fps": int(fps_val or 24),
                    "duration_sec": float(dur_val or 5.0),
                    "epsilon": float(epsilon_val or 0.001),
                    "timeline": _parse_timeline(tdata),
                }
                # Autosave zip — fixed location, unchanged behavior
                stats = _write_session_zip(AUTOSAVE_ZIP, payload)

                # User-chosen folder (optional)
                folder_msg = ""
                folder = (save_folder or "").strip()
                if folder:
                    try:
                        folder = os.path.expandvars(os.path.expanduser(folder))
                        os.makedirs(folder, exist_ok=True)
                        target = os.path.join(folder, fname)
                        _write_session_zip(target, payload)
                        folder_msg = f"  \n📁 Written to `{target}`"
                        _save_config({**_load_config(),
                                      "save_folder": folder,
                                      "project_name": (project_name or "").strip() or "ltx_project"})
                    except Exception as fe:
                        folder_msg = f"  \n⚠️ Could not write to folder `{folder}`: {fe} (download link below still works)"
                else:
                    _save_config({**_load_config(),
                                  "project_name": (project_name or "").strip() or "ltx_project"})

                # Browser download copy — named file in a fresh temp dir
                out_dir  = tempfile.mkdtemp(prefix="ltx_director_save_")
                out_path = os.path.join(out_dir, fname)
                _write_session_zip(out_path, payload)

                dedup_note = ""
                if stats["dup_hits"]:
                    saved_mb = stats["bytes_saved"] / 1048576
                    dedup_note = f" Deduplicated {stats['dup_hits']} reused asset placement(s) (saved {saved_mb:.1f} MB)."
                return (
                    gr.update(value=out_path, visible=True),
                    f"✅ Saved **{fname}** — {stats['images']} unique image(s), "
                    f"{stats['audio']} unique audio clip(s).{dedup_note}{folder_msg}",
                )
            except Exception as e:
                log.error("Save error: %s", traceback.format_exc())
                return gr.update(visible=False), f"❌ Save failed: {e}  \n*LTX Director v{PLUGIN_VERSION}*"

        def browse_for_folder(current):
            """Open the native OS folder picker (subprocess, never blocks UI thread state)."""
            path, err = _pick_folder_native()
            if path:
                _save_config({**_load_config(), "save_folder": path})
                return path, f"📂 Save folder set to `{path}`."
            if err:
                return current or "", f"⚠️ {err}"
            return current or "", ""          # user cancelled — keep as-is

        browse_btn.click(
            fn=browse_for_folder,
            inputs=[save_folder_box],
            outputs=[save_folder_box, save_status],
        )

        def _load_from_path(path, source_label=""):
            """Shared loader returning the 9 load outputs for a disk path."""
            try:
                payload = _load_session_any(path)
                tdata = json.dumps(payload.get("timeline", {}))
                fps_v = int(payload.get("fps", 24))
                dur_v = float(payload.get("duration_sec", 5.0))
                fcount = max(1, round(dur_v * fps_v)) + 1
                # Full payload blob for the bridge to push into iframe in one shot
                restore_blob = json.dumps(payload)
                return (
                    tdata,
                    payload.get("global_prompt", ""),
                    fps_v,
                    dur_v,
                    float(payload.get("epsilon", 0.001)),
                    fcount,
                    payload.get("project_name", "ltx_project"),
                    f"✅ Session loaded{source_label}.  \n*LTX Director v{PLUGIN_VERSION}*",
                    restore_blob,
                )
            except Exception as e:
                return "{}", "", 24, 5.0, 0.001, 121, gr.update(), f"❌ Load failed: {e}  \n*LTX Director v{PLUGIN_VERSION}*", ""

        def load_session(file_obj):
            """Load a saved session uploaded via the browser."""
            if file_obj is None:
                return "{}", "", 24, 5.0, 0.001, 121, gr.update(), "⚠️ No file selected.", ""
            # Gradio passes different types depending on version:
            # dict {"name"/"path":...}, NamedString, tempfile wrapper,
            # plain str, or a LIST of any of those.
            if isinstance(file_obj, (list, tuple)):
                if not file_obj:
                    return "{}", "", 24, 5.0, 0.001, 121, gr.update(), "⚠️ No file selected.", ""
                file_obj = file_obj[0]
            if isinstance(file_obj, dict):
                path = file_obj.get("path") or file_obj.get("name") or str(file_obj)
            elif hasattr(file_obj, "name"):
                path = file_obj.name
            elif hasattr(file_obj, "path"):
                path = file_obj.path
            else:
                path = str(file_obj)
            return _load_from_path(path)

        def load_session_from_path(path_text):
            """Load a session DIRECTLY from a path on this computer — no
            browser upload involved, so it works for any file size and is
            immune to Gradio's upload-cache problems."""
            path = os.path.expandvars(os.path.expanduser((path_text or "").strip().strip('"')))
            if not path:
                return "{}", "", 24, 5.0, 0.001, 121, gr.update(), "⚠️ Enter a file path first (or click 📄 Browse File…).", ""
            res = _load_from_path(path, source_label=" from path")
            if res[7].startswith("✅"):
                _save_config({**_load_config(), "load_path": path})
            return res

        def browse_for_file(current):
            """Native OS file picker for sessions (subprocess, can't hang UI)."""
            path, err = _pick_file_native()
            if path:
                return path, f"📄 Selected `{path}` — click **📥 Load from Path**."
            if err:
                return current or "", f"⚠️ {err}"
            return current or "", ""

        def recover_last():
            """Restore the last auto-save (.zip preferred, legacy .json fallback)."""
            src = AUTOSAVE_ZIP if AUTOSAVE_ZIP.exists() else (
                  AUTOSAVE_PATH if AUTOSAVE_PATH.exists() else None)
            if src is None:
                return "{}", "", 24, 5.0, 0.001, 121, gr.update(), "⚠️ No auto-save found.", ""
            try:
                payload = _load_session_any(src)
                tdata = json.dumps(payload.get("timeline", {}))
                fps_v = int(payload.get("fps", 24))
                dur_v = float(payload.get("duration_sec", 5.0))
                fcount = max(1, round(dur_v * fps_v)) + 1
                age = ""
                try:
                    import time
                    age_sec = time.time() - src.stat().st_mtime
                    if age_sec < 3600:
                        age = f" ({int(age_sec//60)}m ago)"
                    else:
                        age = f" ({int(age_sec//3600)}h ago)"
                except Exception:
                    pass
                restore_blob = json.dumps(payload)
                return (
                    tdata,
                    payload.get("global_prompt", ""),
                    fps_v,
                    dur_v,
                    float(payload.get("epsilon", 0.001)),
                    fcount,
                    payload.get("project_name", "ltx_project"),
                    f"✅ Recovered auto-save{age}.",
                    restore_blob,
                )
            except Exception as e:
                return "{}", "", 24, 5.0, 0.001, 121, gr.update(), f"❌ Recovery failed: {e}", ""

        save_btn.click(
            fn=save_session,
            inputs=[timeline_data_box, global_prompt_box, fps_box, duration_box, epsilon_box,
                    project_name_box, save_folder_box],
            outputs=[dl_file, save_status],
        )
        load_file.change(
            fn=load_session,
            inputs=[load_file],
            outputs=[timeline_data_box, global_prompt_box, fps_box, duration_box,
                     epsilon_box, frames_box, project_name_box, save_status, restore_payload_box],
        ).then(
            fn=None,
            inputs=[],
            outputs=[],
            js="() => { try {   const root = window.gradioApp ? window.gradioApp() : (document.querySelector('gradio-app') || document);   const el = root.querySelector('#wdc_restore_payload textarea, #wdc_restore_payload input');   if (!el || !el.value) return;   const payload = JSON.parse(el.value);   const fr = document.getElementById('wdc-timeline-iframe');   if (fr && fr.contentWindow) {     fr.contentWindow.postMessage({ source: 'wdc_parent', cmd: 'restore', data: payload }, '*');   } } catch(e) { console.warn('[LTXDirector] restore push error:', e); } }",
        )
        browse_file_btn.click(
            fn=browse_for_file,
            inputs=[load_path_box],
            outputs=[load_path_box, save_status],
        )
        load_path_btn.click(
            fn=load_session_from_path,
            inputs=[load_path_box],
            outputs=[timeline_data_box, global_prompt_box, fps_box, duration_box,
                     epsilon_box, frames_box, project_name_box, save_status, restore_payload_box],
        ).then(
            fn=None,
            inputs=[],
            outputs=[],
            js="() => { try {   const root = window.gradioApp ? window.gradioApp() : (document.querySelector('gradio-app') || document);   const el = root.querySelector('#wdc_restore_payload textarea, #wdc_restore_payload input');   if (!el || !el.value) return;   const payload = JSON.parse(el.value);   const fr = document.getElementById('wdc-timeline-iframe');   if (fr && fr.contentWindow) {     fr.contentWindow.postMessage({ source: 'wdc_parent', cmd: 'restore', data: payload }, '*');   } } catch(e) { console.warn('[LTXDirector] restore push error:', e); } }",
        )
        recover_btn.click(
            fn=recover_last,
            inputs=[],
            outputs=[timeline_data_box, global_prompt_box, fps_box, duration_box,
                     epsilon_box, frames_box, project_name_box, save_status, restore_payload_box],
        ).then(
            fn=None,
            inputs=[],
            outputs=[],
            js="() => { try {   const root = window.gradioApp ? window.gradioApp() : (document.querySelector('gradio-app') || document);   const el = root.querySelector('#wdc_restore_payload textarea, #wdc_restore_payload input');   if (!el || !el.value) return;   const payload = JSON.parse(el.value);   const fr = document.getElementById('wdc-timeline-iframe');   if (fr && fr.contentWindow) {     fr.contentWindow.postMessage({ source: 'wdc_parent', cmd: 'restore', data: payload }, '*');   } } catch(e) { console.warn('[LTXDirector] restore push error:', e); } }",
        )

        # ── Preview / Apply / Generate / Clear ────────────────────────────

        def preview_schedule(tdata, global_p, fps, duration_sec):
            parsed = _parse_timeline(tdata)
            _fps  = float(fps or parsed.get("fps", 24) or 24)
            _dur  = float(duration_sec or parsed.get("durationSec", 5) or 5)
            _tf   = max(1, round(_dur * _fps)) + 1
            _ws   = int(parsed.get("slidingWindowSize", 0) or 0)
            _ov   = int(parsed.get("slidingWindowOverlap", 0) or 0)
            if _ws > 0:
                _ws, _ov = _snap_window_pair(_ws, _ov)

            combined, locals_str, lengths_str, has_segs, prompt_mode = _build_prompt_relay(
                tdata, global_p, _fps, total_frames=_tf, win_size=_ws, win_overlap=_ov
            )
            if not has_segs:
                return gr.update(value="⚠️ Timeline is empty — add some segments first.", visible=True)

            mode_label = (
                "Each Paragraph → new Sliding Window (`PW`)" if prompt_mode == "PW"
                else "All the Lines are Part of the Same Prompt (`FG`)"
            )
            win_info = ""
            if prompt_mode == "PW":
                n_win = len(_compute_windows(_tf, _ws, _ov))
                win_info = (f"**Sliding windows:** {n_win} × {_ws}f, overlap {_ov}f — "
                            f"**{_ws - _ov} new frames** per window after the first\n\n")

            lines = [
                "### 📋 Schedule",
                f"**{len(parsed.get('segments',[]))} video segment(s)** · **{len(parsed.get('audioSegments',[]))} audio clip(s)**",
                "",
                f"**Prompt mode:** {mode_label}",
                "",
                win_info + "**Prompt relay:**",
                f"```\n{combined}\n```",
                "",
                "**Segment lengths (frames):** `" + (lengths_str or "—") + "`",
            ]
            return gr.update(value="\n".join(lines), visible=True)

        def _assemble_settings(tdata, global_p, fps, duration_sec, epsilon,
                               project_name, state, adv_vals=None,
                               lora_sel=None, lora_mult=None, as_paths=False):
            """Build the WanGP settings dict from the timeline (shared by both
            'Apply to Generator' and 'Generate Here'). Returns
            (settings, summary_parts, info_dict) or raises on empty timeline.

            adv_vals, when provided, is the tuple of Advanced-clone widget
            values in adv_keys order; it's zipped into a dict and every present
            key overrides the model's current settings.
            """
            from PIL import Image as _PILImage

            # Map positional advanced values to their setting keys.
            adv = {}
            if adv_vals:
                adv = {k: v for k, v in zip(adv_keys, adv_vals)}

            _tparsed_pre = _parse_timeline(tdata)
            if not fps or float(fps) <= 0:
                fps = _tparsed_pre.get("fps", 24)
            if not duration_sec or float(duration_sec) <= 0:
                duration_sec = _tparsed_pre.get("durationSec", 5.0)

            _fps_val     = int(fps or 24)
            total_frames = max(1, round(float(duration_sec or 5) * _fps_val)) + 1

            # Sliding window settings: Advanced override (if set) else timeline,
            # snapped to LTX 2.3's valid 8k+1 grid.
            _win_size = int(_tparsed_pre.get("slidingWindowSize", 0) or 0)
            _win_ovl  = int(_tparsed_pre.get("slidingWindowOverlap", 0) or 0)
            if adv:
                _adv_ws = int(adv.get("sliding_window_size", 0) or 0)
                _adv_ov = int(adv.get("sliding_window_overlap", 0) or 0)
                if _adv_ws > 0:
                    _win_size, _win_ovl = _adv_ws, _adv_ov
            if _win_size > 0:
                _win_size, _win_ovl = _snap_window_pair(_win_size, _win_ovl)

            combined, locals_str, lengths_str, has_segs, prompt_mode = _build_prompt_relay(
                tdata, global_p, float(_fps_val),
                total_frames=total_frames, win_size=_win_size, win_overlap=_win_ovl,
            )
            if not has_segs:
                raise ValueError("Timeline is empty — add segments before generating.")

            parsed     = _tparsed_pre
            segments   = parsed.get("segments", [])
            audio_segs = parsed.get("audioSegments", [])

            settings = self.get_current_model_settings(state)
            settings["prompt"] = combined
            settings["multi_prompts_gen_type"] = prompt_mode

            # The WanGP API queue requires model_type in the task params. The
            # settings dict from get_current_model_settings doesn't always carry
            # it, so set it explicitly from the active model (state, or the
            # plugin's selected model, or the model_def of either).
            _mt = self._state_model_type(state)
            if not _mt:
                _mt = getattr(self, "_selected_model_type", "") or ""
            if _mt:
                settings["model_type"] = _mt
                try:
                    if self._wangp_session is not None:
                        _md = self._wangp_session.get_model_def(_mt) or {}
                        if _md.get("architecture"):
                            settings.setdefault("base_model_type", _md["architecture"])
                except Exception:
                    pass

            # Reference images + KFI
            ref_images, img_segs_sorted = [], sorted(
                [s for s in segments if s.get("imageB64")],
                key=lambda s: s.get("start", 0)
            )
            for seg in img_segs_sorted:
                b64 = seg.get("imageB64", "")
                if "," in b64:
                    b64 = b64.split(",", 1)[1]
                try:
                    pil = _PILImage.open(_io.BytesIO(base64.b64decode(b64))).convert("RGB")
                    ref_images.append(pil)
                except Exception as exc:
                    log.warning("Image decode failed: %s", exc)

            if ref_images:
                if as_paths:
                    # The API queue serializes image_refs/image_start as FILE
                    # PATHS, not PIL objects. Write each reference image to a
                    # temp PNG and pass the paths.
                    ref_paths = []
                    for pil in ref_images:
                        tmp = tempfile.NamedTemporaryFile(
                            suffix=".png", delete=False, prefix="wdc_imgref_")
                        pil.save(tmp.name, "PNG"); tmp.flush(); tmp.close()
                        ref_paths.append(tmp.name)
                    settings["image_refs"]  = ref_paths
                    settings["image_start"] = [ref_paths[0]]
                else:
                    settings["image_refs"]  = ref_images
                    settings["image_start"] = [ref_images[0]]
                settings["video_prompt_type"] = "KFI"
                positions = ["1"] + [str(int(s.get("start", 0))) for s in img_segs_sorted[1:]]
                settings["frames_positions"] = " ".join(positions)
            else:
                for k in ("image_refs","image_start","video_prompt_type","frames_positions"):
                    settings.pop(k, None)

            settings["video_length"] = total_frames
            settings["force_fps"]    = str(_fps_val)

            if _win_size > 0:
                settings["sliding_window_size"]    = _win_size
                settings["sliding_window_overlap"] = _win_ovl

            # ── Merge Advanced-clone overrides ─────────────────────────────
            # Every key the Advanced clone manages is written straight into
            # settings (these are real WanGP setting keys). sliding_window_* and
            # force_fps are handled above/below from the timeline, so skip them
            # here unless the user set a window size in Advanced.
            if adv:
                _skip = {"sliding_window_size", "sliding_window_overlap",
                         "video_length", "force_fps",
                         "loras_choices", "loras_multipliers", "lora_show_sliders"}
                for k, vv in adv.items():
                    if k in _skip or vv is None:
                        continue
                    settings[k] = vv
                # If Advanced set a window size, honor the snapped pair set above.
                if _win_size > 0:
                    settings["sliding_window_size"]    = _win_size
                    settings["sliding_window_overlap"] = _win_ovl

            # ── LoRAs: activated list + multipliers string ─────────────────
            if lora_sel:
                settings["activated_loras"]   = list(lora_sel)
                settings["loras_multipliers"] = str(lora_mult or "")
            elif lora_mult is not None and str(lora_mult).strip():
                settings["loras_multipliers"] = str(lora_mult)

            # Audio
            audio_path = None
            if audio_segs:
                try:
                    mixed = _build_combined_audio(tdata, total_frames, float(fps or 24))
                    if mixed is not None:
                        import soundfile as _sf
                        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False, prefix="wdc_audio_")
                        wf = mixed["waveform"].squeeze(0)
                        _sf.write(tmp.name, wf.numpy().T, mixed["sample_rate"])
                        audio_path = tmp.name
                except Exception:
                    pass
                if audio_path is None:
                    first_b64 = audio_segs[0].get("audioB64", "")
                    if first_b64:
                        if "," in first_b64:
                            first_b64 = first_b64.split(",", 1)[1]
                        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, prefix="wdc_audio_")
                        tmp.write(base64.b64decode(first_b64)); tmp.flush()
                        audio_path = tmp.name

            if audio_path:
                settings["audio_guide"]       = audio_path
                settings["audio_prompt_type"] = "A"
            else:
                settings.pop("audio_guide",       None)
                settings.pop("audio_prompt_type", None)

            # Auto-save (zip with deduplicated assets)
            try:
                from datetime import datetime as _dt
                payload = {
                    "version": PLUGIN_VERSION,
                    "project_name": (project_name or "").strip() or "ltx_project",
                    "saved_at": _dt.now().strftime("%Y-%m-%d_%H-%M-%S"),
                    "global_prompt": global_p,
                    "fps": _fps_val,
                    "duration_sec": float(duration_sec or 5),
                    "epsilon": float(epsilon or 0.001),
                    "timeline": parsed,
                }
                _write_session_zip(AUTOSAVE_ZIP, payload)
            except Exception:
                pass

            # Human-readable summary
            n_segs, n_audio, n_imgs = len(segments), len(audio_segs), len(ref_images)
            parts = [f"**{n_segs} segment(s)**"]
            if n_imgs:
                parts.append(f"**{n_imgs} image(s)** @ [{settings.get('frames_positions','')}] KFI")
            if n_audio:
                parts.append(f"**{n_audio} audio clip(s)**")
            if prompt_mode == "PW":
                n_win = len(_compute_windows(total_frames, _win_size, _win_ovl))
                parts.append(f"**{n_win} sliding windows** ({_win_size}f / ovl {_win_ovl}f, mode PW)")
            else:
                parts.append("**single window** (mode FG)")

            return settings, parts, {
                "total_frames": total_frames, "fps": _fps_val,
            }

        def apply_to_generator(tdata, global_p, fps, duration_sec, epsilon, project_name, state):
            import time as _time
            try:
                settings, parts, _ = _assemble_settings(
                    tdata, global_p, fps, duration_sec, epsilon, project_name, state
                )
                msg = (f"✅ Applied — {', '.join(parts)}.  \n"
                       f"Switch to **Video Generator** and click Generate.")
                gr.Info("LTX Director → Generator: settings transferred.")
                return msg, gr.update(value=str(_time.time()))
            except ValueError as ve:
                return f"⚠️ {ve}", gr.update()
            except Exception as e:
                log.error("Apply error: %s", traceback.format_exc())
                return f"❌ Error: {e}", gr.update()

        def apply_and_generate(tdata, global_p, fps, duration_sec, epsilon, project_name, state):
            msg, refresh = apply_to_generator(tdata, global_p, fps, duration_sec, epsilon, project_name, state)
            # The JS bridge clicks the Generate button after this returns.
            return msg, refresh

        def generate_here(tdata, global_p, fps, duration_sec, epsilon, project_name,
                          state, *adv_vals):
            """Direct generation via the WanGP plugin API. Because this handler
            references self.api, plugin_ui_context() auto-wraps the click to
            queue the job into the live WebUI queue. We yield status + the
            finished video into the inline player. Outputs:
            (gen_status_md, result_video, status_md).

            adv_vals = (*adv_components, loras_choices, loras_multipliers).
            """
            # Peel the two LoRA fields off the end (bound after *adv_components).
            lora_sel, lora_mult = None, None
            adv_core = adv_vals
            if len(adv_vals) >= 2:
                lora_sel = adv_vals[-2]
                lora_mult = adv_vals[-1]
                adv_core = adv_vals[:-2]

            if not self.has_gen_api or self._wangp_session is None:
                yield (
                    gr.update(value="⚠️ This WanGP build has no plugin generation "
                                    "API — use **Apply to Generator** instead.",
                              visible=True),
                    gr.update(visible=False),
                    gr.update(),
                )
                return

            try:
                settings, parts, info = _assemble_settings(
                    tdata, global_p, fps, duration_sec, epsilon, project_name,
                    state, adv_vals=adv_core, lora_sel=lora_sel, lora_mult=lora_mult,
                    as_paths=True,
                )
            except ValueError as ve:
                yield (gr.update(value=f"⚠️ {ve}", visible=True),
                       gr.update(visible=False), gr.update())
                return
            except Exception as e:
                log.error("Generate-here assemble error: %s", traceback.format_exc())
                yield (gr.update(value=f"❌ Error preparing settings: {e}", visible=True),
                       gr.update(visible=False), gr.update())
                return

            yield (
                gr.update(value=f"🎬 Queued — {', '.join(parts)}.", visible=True),
                gr.update(visible=False),
                gr.update(value="🎬 Submitting to WanGP…"),
            )

            # Submit the task and get the job handle. CRITICAL: we do NOT chain
            # .result() here — that would block this generator before the plugin
            # wrapper can pump the WebUI queue (the job would be admitted but
            # never run). Instead we submit, then poll job.done, draining the
            # job's event stream for progress, exactly like WanGP's own video
            # process plugin. The wrapper pumps the queue while we poll.
            import time as _t
            try:
                job = self._wangp_session.submit_task(settings)
            except Exception as e:
                log.error("Generate-here submit error: %s", traceback.format_exc())
                yield (gr.update(value=f"❌ Could not submit: {e}", visible=True),
                       gr.update(visible=False),
                       gr.update(value="❌ Submit failed."))
                return

            last_status = ""
            cur_step = tot_step = None
            while not getattr(job, "done", False):
                # Drain any progress events without blocking.
                try:
                    stream = getattr(job, "events", None)
                    if stream is not None:
                        ev = stream.get(timeout=0.25)
                        if ev is not None:
                            data = getattr(ev, "data", None)
                            if data is not None:
                                st = getattr(data, "status", None) or getattr(data, "phase", None)
                                cs = getattr(data, "current_step", None)
                                ts = getattr(data, "total_steps", None)
                                pr = getattr(data, "progress", None)
                                if cs is not None: cur_step = cs
                                if ts is not None: tot_step = ts
                                if st: last_status = str(st)
                    else:
                        _t.sleep(0.25)
                except Exception:
                    _t.sleep(0.25)

                if cur_step is not None and tot_step:
                    bar = self._progress_bar(cur_step, tot_step)
                    status_line = f"🎬 {last_status or 'Generating'} — step {cur_step}/{tot_step}\n\n{bar}"
                else:
                    status_line = f"🎬 {last_status or 'Generating'}…"
                yield (gr.update(value=status_line, visible=True),
                       gr.update(visible=False),
                       gr.update(value=status_line))

            # Job finished — fetch the result (already done, returns immediately).
            try:
                result = job.result(timeout=1.0)
            except Exception as e:
                log.error("Generate-here result error: %s", traceback.format_exc())
                yield (gr.update(value=f"❌ Generation error: {e}", visible=True),
                       gr.update(visible=False),
                       gr.update(value="❌ Generation error."))
                return

            # Resolve an output file path from the result.
            video_path = None
            try:
                if getattr(result, "artifacts", None):
                    for art in result.artifacts:
                        if getattr(art, "path", None):
                            video_path = art.path
                            break
                if video_path is None and getattr(result, "generated_files", None):
                    video_path = result.generated_files[-1]
            except Exception:
                pass

            if getattr(result, "cancelled", False):
                yield (gr.update(value="⏹ Generation cancelled.", visible=True),
                       gr.update(visible=False),
                       gr.update(value="⏹ Cancelled."))
                return

            if not getattr(result, "success", False) or not video_path:
                errs = "; ".join(str(e) for e in getattr(result, "errors", []) or [])
                yield (gr.update(value=f"❌ No output produced. {errs}".strip(), visible=True),
                       gr.update(visible=False),
                       gr.update(value="❌ No output produced."))
                return

            yield (
                gr.update(value=f"✅ Done — {', '.join(parts)}.", visible=True),
                gr.update(value=video_path, visible=True),
                gr.update(value="✅ Generation complete."),
            )

        def cancel_here():
            try:
                if self._wangp_session is not None:
                    self._wangp_session.cancel()
                return gr.update(value="⏹ Stopping…", visible=True)
            except Exception as e:
                return gr.update(value=f"⚠️ Could not cancel: {e}", visible=True)

        def clear_timeline():
            return "{}", "", "", "", gr.update(visible=False), "🗑 Timeline cleared."

        def _clean_choices(ch):
            """Coerce a choices list into the (label, value) 2-tuple form Gradio
            requires. Returns None if there's nothing usable. Guards against the
            upsampler API returning richer tuples that would crash a dropdown
            update and freeze the client."""
            if not ch:
                return None
            out = []
            for item in ch:
                try:
                    if isinstance(item, (list, tuple)):
                        if len(item) >= 2:
                            out.append((str(item[0]), item[1]))
                        elif len(item) == 1:
                            out.append((str(item[0]), item[0]))
                    else:
                        out.append((str(item), item))
                except Exception:
                    continue
            return out or None

        def refresh_advanced_from_model(state):
            """Populate the Advanced widgets from the current model's live
            settings, and set per-field visibility to match the model. Returns
            updates in adv_keys order, then tab updates, then a lora update and
            a status line. Wrapped so it can NEVER raise into the event chain
            (a raising handler here freezes the whole Gradio client)."""
            _noop = (*[gr.update() for _ in adv_keys],
                     *[gr.update() for _ in adv_tab_keys],
                     gr.update())
            try:
                try:
                    s = self.get_current_model_settings(state) or {}
                except Exception as e:
                    return (*_noop, f"⚠️ Could not read model settings: {e}")

                mt = self._state_model_type(state) or getattr(self, "_selected_model_type", "")
                model_def = {}
                try:
                    if mt and self._wangp_session is not None:
                        model_def = self._wangp_session.get_model_def(mt) or {}
                except Exception:
                    model_def = {}

                # If we couldn't resolve the model, DON'T change visibility —
                # hiding tabs (e.g. Quality) on an empty model_def is what made
                # tabs disappear. Only retarget visibility when we know the model.
                have_model = bool(model_def)
                vis  = _adv.resolve_visibility(model_def) if have_model else {}
                tvis = _adv.tab_visibility(vis) if have_model else {}

                _sp_methods, _sp_ratios = (None, None)
                try:
                    _sp_methods, _sp_ratios = self._spatial_choices_for_model(mt)
                    _sp_methods = _clean_choices(_sp_methods)
                    _sp_ratios  = _clean_choices(_sp_ratios)
                except Exception:
                    _sp_methods, _sp_ratios = None, None

                def val(key):
                    v = s.get(key, None)
                    extra = {}
                    if key == "spatial_upsampling_method" and _sp_methods:
                        extra["choices"] = _sp_methods
                    elif key == "spatial_upsampling_ratio" and _sp_ratios:
                        extra["choices"] = _sp_ratios
                    if have_model:
                        extra["visible"] = vis.get(key, True)
                    if v is None:
                        return gr.update(**extra)
                    return gr.update(value=v, **extra)

                field_updates = [val(k) for k in adv_keys]
                if have_model:
                    tab_updates = [gr.update(visible=tvis.get(k, True)) for k in adv_tab_keys]
                else:
                    tab_updates = [gr.update() for _ in adv_tab_keys]

                try:
                    loras = self._list_loras_for_model(mt)
                    lora_update = _lora_update(loras)
                except Exception:
                    lora_update = gr.update()

                msg = ("⟲ Advanced synced to the selected model."
                       if have_model else
                       "⟲ Synced. (Select a model above to retarget which fields show.)")
                return (*field_updates, *tab_updates, lora_update, msg)
            except Exception as e:
                log.warning("refresh_advanced_from_model failed safely: %s", e)
                return (*_noop, f"⚠️ Sync skipped: {e}")

        def switch_model(model_type, state):
            """Switch the live WanGP model via model_choice_target, then resync
            the Advanced clone to the newly selected model. Wrapped so it can
            never raise into the event chain."""
            _noop_tail = (*[gr.update() for _ in adv_keys],
                          *[gr.update() for _ in adv_tab_keys], gr.update())
            if not model_type:
                return (gr.update(), "⚠️ No model selected.", *_noop_tail)
            try:
                import time as _t
                target_val = f"{model_type}|{_t.time()}"
                self._selected_model_type = model_type

                model_def = {}
                try:
                    if self._wangp_session is not None:
                        model_def = self._wangp_session.get_model_def(model_type) or {}
                except Exception:
                    model_def = {}
                have_model = bool(model_def)
                vis  = _adv.resolve_visibility(model_def) if have_model else {}
                tvis = _adv.tab_visibility(vis) if have_model else {}

                _sp_methods, _sp_ratios = (None, None)
                try:
                    _sp_methods, _sp_ratios = self._spatial_choices_for_model(model_type)
                    _sp_methods = _clean_choices(_sp_methods)
                    _sp_ratios  = _clean_choices(_sp_ratios)
                except Exception:
                    _sp_methods, _sp_ratios = None, None

                defaults = {}
                try:
                    if self._wangp_session is not None:
                        defaults = self._wangp_session.get_default_settings(model_type) or {}
                except Exception:
                    defaults = {}

                def val(key):
                    v = defaults.get(key, None)
                    extra = {}
                    if key == "spatial_upsampling_method" and _sp_methods:
                        extra["choices"] = _sp_methods
                    elif key == "spatial_upsampling_ratio" and _sp_ratios:
                        extra["choices"] = _sp_ratios
                    if have_model:
                        extra["visible"] = vis.get(key, True)
                    if v is None:
                        return gr.update(**extra)
                    return gr.update(value=v, **extra)

                field_updates = [val(k) for k in adv_keys]
                if have_model:
                    tab_updates = [gr.update(visible=tvis.get(k, True)) for k in adv_tab_keys]
                else:
                    tab_updates = [gr.update() for _ in adv_tab_keys]

                try:
                    loras = self._list_loras_for_model(model_type)
                    lora_update = _lora_update(loras, reset=True)
                except Exception:
                    lora_update = gr.update()

                name = next((m["label"] for m in _ltx_models
                             if m["model_type"] == model_type), model_type)
                return (target_val, f"✅ Switched to **{name}**.",
                        *field_updates, *tab_updates, lora_update)
            except Exception as e:
                log.warning("switch_model failed safely: %s", e)
                return (gr.update(), f"⚠️ Switch skipped: {e}", *_noop_tail)

        def refresh_model_list():
            models = self._list_ltx_models()
            choices = [(m["label"], m["model_type"]) for m in models]
            val = choices[0][1] if choices else None
            return gr.update(choices=choices, value=val), f"⟲ Found {len(choices)} LTX model(s)."

        # ── Direct generation (only meaningful when the API is present) ────
        if self.has_gen_api:
            # generate_here yields a 3rd status value; we route it to a hidden
            # sink so the progress only shows in the top status (gen_status_md),
            # above the model selector — not duplicated in the bottom status.
            _gen_status_sink = gr.Markdown(visible=False, elem_id="wdc-gen-status-sink")
            generate_here_btn_h.click(
                fn=generate_here,
                inputs=[timeline_data_box, global_prompt_box, fps_box, duration_box,
                        epsilon_box, project_name_box, self.state, *adv_components,
                        adv_map["loras_choices"], adv_map["loras_multipliers"]],
                outputs=[gen_status_md, result_video, _gen_status_sink],
            )
            cancel_here_btn.click(fn=cancel_here, inputs=[], outputs=[gen_status_md])

            # Model selector → switch live model + retarget Advanced visibility
            model_selector.change(
                fn=switch_model,
                inputs=[model_selector, self.state],
                outputs=[self.model_choice_target, model_status,
                         *adv_components, *adv_tab_comps, loras_component],
            )
            refresh_models_btn.click(
                fn=refresh_model_list, inputs=[],
                outputs=[model_selector, model_status],
            )

        refresh_adv_btn.click(
            fn=refresh_advanced_from_model,
            inputs=[self.state],
            outputs=[*adv_components, *adv_tab_comps, loras_component, adv_status],
        )

        # ── Category ↔ Resolution Budget (mirrors the Video Generator) ─────
        _res_group = adv_map.get("resolution_group")
        _res_comp  = adv_map.get("resolution")
        if _res_group is not None and _res_comp is not None:
            # Populate both at build time for the initial model.
            try:
                groups, group_res, sel_group, sel_val = \
                    self._resolution_choices_for_model(_model_value)
                if groups:
                    _res_group.choices = groups
                    _res_group.value = sel_group
                if group_res:
                    _res_comp.choices = group_res
                    if sel_val:
                        _res_comp.value = sel_val
            except Exception as exc:
                log.info("Initial resolution population skipped: %s", exc)

            def _on_category_change(selected_group, state):
                """Filter the Resolution Budget list to the chosen Category."""
                try:
                    import wgp as _wgp
                except Exception:
                    return gr.update()
                try:
                    mt = self._state_model_type(state) or self._selected_model_type
                    model_def = (self._wangp_session.get_model_def(mt) or {}) \
                        if (self._wangp_session is not None and mt) else {}
                    model_resolutions = model_def.get("resolutions", None)
                    choices, _ = _wgp.get_resolution_choices(None, model_resolutions)
                    if model_resolutions is None:
                        filtered = [r for r in choices
                                    if _wgp.categorize_resolution(r[1]) == selected_group]
                    else:
                        filtered = model_resolutions
                    val = filtered[0][1] if filtered else None
                    return gr.update(choices=filtered, value=val)
                except Exception as exc:
                    log.info("Category change skipped: %s", exc)
                    return gr.update()

            _res_group.change(
                fn=_on_category_change,
                inputs=[_res_group, self.state],
                outputs=[_res_comp], show_progress="hidden",
            )

        # ── LoRA strength sliders (fixed pool, queue-safe) ─────────────────
        _mult_comp   = adv_map.get("loras_multipliers")
        _phases_comp = adv_map.get("guidance_phases")
        _show_comp   = adv_map.get("lora_show_sliders")
        _pool        = adv_map.get("_lora_sliders", [])
        _rows        = adv_map.get("_lora_slider_rows", [])
        _labels      = adv_map.get("_lora_slider_labels", [])
        _col         = adv_map.get("_lora_sliders_col")
        _max_rows    = adv_map.get("_lora_max_rows", 0)
        _max_phases  = adv_map.get("_lora_max_phases", 0)

        # Targets the layout handler updates: column, all rows, all labels, all
        # pool sliders (matches layout_lora_sliders' return order).
        _layout_outputs = [_col, *_rows, *_labels, *_pool] if _col is not None else []

        def _layout_sliders(selected, phases, show, current):
            return _adv.layout_lora_sliders(
                selected, phases, show, current, _max_rows, _max_phases)

        # Re-layout the pool whenever the selection, phase count, or toggle
        # changes. All registered statically at build time (no @gr.render).
        if _col is not None and loras_component is not None and _phases_comp is not None:
            _layout_inputs = [loras_component, _phases_comp, _show_comp, _mult_comp]

            def _collect_mult(selected, phases, *vals):
                return _adv.collect_lora_multipliers(selected, phases, _max_phases, *vals)
            _collect_inputs = [loras_component, _phases_comp, *_pool]

            # Selection / phase / toggle change → re-layout the pool, THEN
            # rebuild the multipliers string from the freshly-set slider values.
            for _trigger in (loras_component, _phases_comp, _show_comp):
                _trigger.change(
                    fn=_layout_sliders, inputs=_layout_inputs,
                    outputs=_layout_outputs, show_progress="hidden",
                ).then(
                    fn=_collect_mult, inputs=_collect_inputs,
                    outputs=[_mult_comp], show_progress="hidden",
                )

            # Moving any slider updates the multipliers string immediately.
            for _s in _pool:
                _s.change(fn=_collect_mult, inputs=_collect_inputs,
                          outputs=[_mult_comp], show_progress="hidden")

        # Persist the "show strength sliders" toggle so it's remembered next run.
        _lora_show_cb = adv_map.get("lora_show_sliders")
        if _lora_show_cb is not None:
            def _persist_lora_sliders(show):
                try:
                    _save_config({**_load_config(), "lora_show_sliders": bool(show)})
                except Exception as exc:
                    log.warning("Could not persist lora_show_sliders: %s", exc)
                return gr.update()
            _lora_show_cb.change(
                fn=_persist_lora_sliders, inputs=[_lora_show_cb], outputs=[adv_status],
            )

        # Advanced is populated at build time (loras + spatial choices) and via
        # the explicit "⟲ Sync values from current model" button. We do NOT
        # auto-sync on main_tabs.select: that handler fires on every tab change
        # app-wide and runs heavy API calls, which could error during a restore
        # and freeze every clickable element until a page refresh.

        preview_btn.click(
            fn=preview_schedule,
            inputs=[timeline_data_box, global_prompt_box, fps_box, duration_box],
            outputs=[schedule_md],
        )
        apply_btn.click(
            fn=apply_to_generator,
            inputs=[timeline_data_box, global_prompt_box, fps_box, duration_box, epsilon_box, project_name_box, self.state],
            outputs=[status_md, self.refresh_form_trigger],
        )
        generate_btn.click(
            fn=apply_and_generate,
            inputs=[timeline_data_box, global_prompt_box, fps_box, duration_box, epsilon_box, project_name_box, self.state],
            outputs=[status_md, self.refresh_form_trigger],
        )
        clear_btn.click(
            fn=clear_timeline,
            inputs=[],
            outputs=[timeline_data_box, local_prompts_box, segment_lengths_box,
                     guide_strength_box, schedule_md, status_md],
        )

        schedule_md.render() if False else None   # keep reference
        return [schedule_md, status_md]

    # ── Model helpers ───────────────────────────────────────────────────────

    # LTX families to surface in the model dropdown (LTX-Video + LTX-2).
    _LTX_FAMILIES = ["ltxv", "ltx2", "LTX Video", "LTX-2"]

    def _list_ltx_models(self) -> list:
        """Return [{model_type, label, family}] for every LTX model the running
        WanGP exposes (LTX-Video and LTX-2 families, including finetunes).
        Falls back to a static list if the API isn't available."""
        out = []
        try:
            if self._wangp_session is not None:
                defs = self._wangp_session.list_model_defs(family=self._LTX_FAMILIES) or []
                for d in defs:
                    mt = str(d.get("model_type", "")).strip()
                    if not mt:
                        continue
                    name = d.get("name") or mt
                    arch = d.get("architecture", "")
                    fam = "LTX-2" if str(arch).startswith("ltx2") or "ltx2" in mt else "LTX Video"
                    out.append({"model_type": mt, "label": f"{name}  ·  {fam}", "family": fam})
        except Exception as exc:
            log.warning("Could not list LTX models from API: %s", exc)

        if not out:
            # Static fallback covering the known LTX base types.
            for mt, name, fam in [
                ("ltxv_13B", "LTX Video 0.9.8 13B", "LTX Video"),
                ("ltx2_19B", "LTX-2 19B", "LTX-2"),
                ("ltx2_22B", "LTX-2 22B (2.3)", "LTX-2"),
                ("ltx2_22B_edit_anything", "LTX-2 22B Edit Anything", "LTX-2"),
                ("joyai_echo", "JoyAI Echo (LTX-2)", "LTX-2"),
            ]:
                out.append({"model_type": mt, "label": f"{name}  ·  {fam}", "family": fam})
        return out

    def _state_model_type(self, state) -> str:
        """Best-effort read of the currently active model_type from state."""
        try:
            if isinstance(state, dict):
                return str(state.get("model_type", "") or "")
            mt = getattr(state, "get", None)
            if callable(mt):
                return str(state.get("model_type", "") or "")
        except Exception:
            pass
        return ""

    def _resolution_choices_for_model(self, model_type: str):
        """Return (groups, group_resolutions, selected_group, selected_value)
        for the Category + Resolution Budget dropdowns, using WanGP's own
        resolution helpers. Returns (None,...) if unavailable."""
        try:
            import wgp as _wgp
        except Exception:
            try:
                import importlib
                _wgp = importlib.import_module("wgp")
            except Exception:
                return None, None, None, None
        try:
            model_def = {}
            if self._wangp_session is not None and model_type:
                model_def = self._wangp_session.get_model_def(model_type) or {}
            model_resolutions = model_def.get("resolutions", None)
            cur = None
            try:
                s = self.get_current_model_settings(self.state) if hasattr(self, "state") else {}
            except Exception:
                s = {}
            cur = (s or {}).get("resolution") if isinstance(s, dict) else None
            choices, cur = _wgp.get_resolution_choices(cur, model_resolutions)
            groups, group_res, sel_group = _wgp.group_resolutions(model_def, choices, cur)
            return groups, group_res, sel_group, cur
        except Exception as exc:
            log.info("Resolution choices unavailable: %s", exc)
            return None, None, None, None

    def _progress_bar(self, cur, tot, width: int = 24) -> str:
        """Render a simple text progress bar for the status line."""
        try:
            frac = max(0.0, min(1.0, float(cur) / float(tot))) if tot else 0.0
        except Exception:
            frac = 0.0
        filled = int(round(frac * width))
        return f"`{'█' * filled}{'░' * (width - filled)}` {int(frac * 100)}%"

    def _spatial_choices_for_model(self, model_type: str):
        """Return (method_choices, ratio_choices) for the Post Processing
        Spatial Upsampling dropdowns, pulled live from WanGP's upsampler API so
        all real options (incl. model VAE upsamplers) are available. Returns
        (None, None) if the API can't be reached."""
        try:
            from postprocessing import upsamplers as _ups
        except Exception:
            return None, None
        try:
            model_def = {}
            if self._wangp_session is not None and model_type:
                model_def = self._wangp_session.get_model_def(model_type) or {}
            try:
                vae_choices = _ups.query_model_vae_method_choices(model_type, model_def, 0)
            except Exception:
                vae_choices = []
            state = _ups.dropdown_state("", image_outputs=False, vae_choices=vae_choices)
            def _san(ch):
                if not ch:
                    return None
                out = []
                for it in ch:
                    if isinstance(it, (list, tuple)) and len(it) >= 2:
                        out.append((str(it[0]), it[1]))
                return out or None
            return _san(state.get("method_choices")), _san(state.get("ratio_choices"))
        except Exception as exc:
            log.info("Spatial upsampling choices unavailable: %s", exc)
            return None, None

    def _list_loras_for_model(self, model_type: str) -> list:
        """Return available LoRA filenames for a model by listing its LoRA
        directory (via the get_lora_dir global). Empty list if unavailable."""
        names = []
        try:
            get_dir = getattr(self, "get_lora_dir", None)
            if get_dir is None or not model_type:
                return []
            lora_dir = get_dir(model_type)
            if not lora_dir or not os.path.isdir(lora_dir):
                return []
            for root, _dirs, files in os.walk(lora_dir):
                for f in files:
                    if f.lower().endswith((".safetensors", ".pt", ".ckpt")):
                        rel = os.path.relpath(os.path.join(root, f), lora_dir)
                        names.append(rel)
            names.sort()
        except Exception as exc:
            log.warning("Could not list LoRAs for %s: %s", model_type, exc)
        return names

    # ── Header (branding) ──────────────────────────────────────────────────

    def _build_header_html(self) -> str:
        """🎬 LTX Director v<version> · created by The-ShadowWalker (with MH logo)."""
        logo_html = ""
        try:
            if MH_LOGO_PATH.exists():
                b64 = base64.b64encode(MH_LOGO_PATH.read_bytes()).decode("ascii")
                logo_html = (
                    f'<img src="data:image/jpeg;base64,{b64}" alt="The-ShadowWalker" '
                    f'style="width:34px;height:34px;border-radius:50%;'
                    f'object-fit:cover;box-shadow:0 0 6px rgba(0,0,0,.6);" />'
                )
        except Exception as exc:
            log.warning("Could not embed MH logo: %s", exc)

        return (
            '<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;'
            'padding:2px 0 6px 0;">'
            f'<h2 style="margin:0;font-size:1.45em;">🎬 LTX Director '
            f'<span style="font-size:.55em;font-weight:600;opacity:.65;'
            f'vertical-align:middle;">v{PLUGIN_VERSION}</span></h2>'
            '<span style="display:inline-flex;align-items:center;gap:7px;'
            'font-size:.85em;opacity:.85;">created by'
            f'{logo_html}'
            '<b>The-ShadowWalker</b></span>'
            '</div>'
        )

    # ── Iframe builder ─────────────────────────────────────────────────────

    def _build_editor_html(self) -> str:
        encoded = base64.b64encode(TIMELINE_EDITOR_HTML.encode("utf-8")).decode("ascii")
        return (
            f'<iframe id="wdc-timeline-iframe" '
            f'src="data:text/html;charset=utf-8;base64,{encoded}" '
            f'style="width:100%;height:540px;border:none;border-radius:6px;" '
            f'sandbox="allow-scripts allow-same-origin allow-forms allow-downloads">'
            f'</iframe>'
        )

    # ── JS Bridge ──────────────────────────────────────────────────────────

    def _build_bridge_js(self) -> str:
        return r"""
// ── LTX Director bridge v1.1.0 ──────────────────────────────────────────
(function() {
  console.log("[LTXDirector] Bridge v1.1 loaded");

  // Inject scoped styles so the Load drop-zone and other plugin widgets use
  // WanGP's native bordered / lighter-surface look instead of rendering
  // dark-on-dark (the drop box was invisible against the page background).
  function wdcInjectStyles() {
    if (document.getElementById("wdc-style")) return;
    var css = document.createElement("style");
    css.id = "wdc-style";
    css.textContent = [
      /* Load Session drop-zone: visible border + surface that adapts to theme */
      "#wdc-load-file { border: 1px dashed var(--border-color-primary, #555) !important;",
      "  background: var(--background-fill-secondary, #2b2b2b) !important;",
      "  border-radius: 8px !important; transition: border-color .15s, background .15s; }",
      "#wdc-load-file:hover { border-color: var(--color-accent, #3a9a54) !important;",
      "  background: var(--background-fill-primary, #333) !important; }",
      "#wdc-load-file .wrap, #wdc-load-file .file-preview { color: var(--body-text-color, #ddd) !important; }",
      /* Make the dashed upload area itself obvious */
      "#wdc-load-file [data-testid='block-label'], #wdc-load-file label { color: var(--body-text-color, #ddd) !important; }",
      /* Model row + advanced tabs sit cleanly within the page */
      "#wdc-model-selector { min-width: 280px; }",
      "#wdc-adv-tabs { border: 1px solid var(--border-color-primary, #444); border-radius: 8px; padding: 4px; }",
      "#wdc-primary-actions { gap: 8px; }",
      /* Bottom-align Save/Load action buttons with their taller inputs */
      "#wdc-save-row, #wdc-load-row, #wdc-loadpath-row { align-items: flex-end !important; }",
      "#wdc-save-row button, #wdc-load-row button, #wdc-loadpath-row button { margin-bottom: 0 !important; }",
      "#wdc-clear-row { justify-content: flex-start; margin: 4px 0; }"
    ].join("\n");
    (document.head || document.documentElement).appendChild(css);
  }
  wdcInjectStyles();
  setTimeout(wdcInjectStyles, 1500);
  setTimeout(wdcInjectStyles, 5000);

  // Duplicate-install guard: if BOTH the old (wan2gp-whatdreamscost) and the
  // renamed (Wan2GP - LTX Director) plugin folders are installed, every
  // element ID exists twice — the bridge then writes timeline data into ONE
  // tab's hidden fields while Apply reads the OTHER tab's (empty) fields,
  // so nothing transfers to the generator. Detect it loudly.
  function wdcCheckDuplicates() {
    var root0 = window.gradioApp ? window.gradioApp() : (document.querySelector("gradio-app") || document);
    var n = root0.querySelectorAll("#wdc_timeline_data").length;
    if (n > 1 && !document.getElementById("wdc-dup-banner")) {
      console.error("[LTXDirector] " + n + " plugin instances detected — prompts will NOT transfer. Delete the old plugin folder and restart Wan2GP.");
      var b = document.createElement("div");
      b.id = "wdc-dup-banner";
      b.textContent = "⚠ LTX Director is installed " + n + " times (old + renamed folder?). Prompts will NOT transfer to the generator. Delete the old plugin folder and restart Wan2GP.";
      b.style.cssText = "position:fixed;top:0;left:0;right:0;z-index:99999;background:#7a1f1f;color:#ffd9d9;font:13px sans-serif;padding:8px 14px;text-align:center;";
      document.body.appendChild(b);
    }
  }
  setTimeout(wdcCheckDuplicates, 4000);
  setTimeout(wdcCheckDuplicates, 12000);

  function wdcRoot() {
    if (window.gradioApp) return window.gradioApp();
    const app = document.querySelector("gradio-app");
    return app ? (app.shadowRoot || app) : document;
  }

  function wdcSet(elemId, value) {
    const root = wdcRoot();
    const el = root.querySelector(
      "#" + elemId + " textarea, #" + elemId + " input[type='text'], #" + elemId + " input:not([type='hidden'])"
    );
    if (!el) { console.warn("[LTXDirector] element not found:", elemId); return; }
    const proto  = el.tagName === "TEXTAREA"
                   ? window.HTMLTextAreaElement.prototype
                   : window.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
    setter && setter.call(el, value);
    el.dispatchEvent(new Event("input",  { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function wdcClickTrigger(elemId) {
    const root = wdcRoot();
    const btn = root.querySelector("#" + elemId + " button") || root.querySelector("#" + elemId);
    if (btn) btn.click();
    else console.warn("[LTXDirector] trigger not found:", elemId);
  }

  // Click the main Wan2GP Generate button (no elem_id, find by text content)
  function wdcClickGenerate() {
    const root = wdcRoot();
    // Try common selectors — the generate tab button has text "Generate"
    const candidates = Array.from(root.querySelectorAll("button")).filter(b => {
      const t = (b.textContent || "").trim();
      return t === "Generate" && !b.closest("[id*='ltx'], [id*='wdc']");
    });
    if (candidates.length > 0) {
      candidates[0].click();
      console.log("[LTXDirector] Clicked Generate button");
    } else {
      console.warn("[LTXDirector] Generate button not found — switch to Video Generator tab manually");
    }
  }

  // Also switch to the generate tab first, then click Generate
  function wdcSwitchToGenerateAndRun() {
    const root = wdcRoot();
    // Find the "Video Generator" or first tab button in the main tabs
    const tabBtns = Array.from(root.querySelectorAll("button[role='tab']"));
    const genTab = tabBtns.find(b => {
      const t = (b.textContent || "").trim().toLowerCase();
      return t.includes("video") && t.includes("gen") || t === "generate";
    });
    if (genTab && !genTab.classList.contains("selected")) {
      genTab.click();
      // Give the tab a moment to render, then click generate
      setTimeout(wdcClickGenerate, 600);
    } else {
      wdcClickGenerate();
    }
  }

  function wdcSendToIframe(cmd) {
    const fr = document.getElementById("wdc-timeline-iframe");
    if (fr && fr.contentWindow) {
      fr.contentWindow.postMessage({ source: "wdc_parent", cmd: cmd }, "*");
    }
  }

  // INBOUND: iframe posts state on every change
  window.addEventListener("message", function(e) {
    const d = e.data;
    if (!d || d.source !== "wdc_ltx_director") return;
    if (d.timeline_data   !== undefined) {
      // The iframe may send a pre-stringified payload OR a raw object.
      // Never stringify twice — that double-encodes the JSON and breaks
      // every Python json.loads() consumer downstream.
      var tlStr, tlObj;
      if (typeof d.timeline_data === "string") {
        tlStr = d.timeline_data;
        try { tlObj = JSON.parse(tlStr); } catch(e) { tlObj = {}; }
      } else {
        tlObj = d.timeline_data || {};
        tlStr = JSON.stringify(tlObj);
      }
      wdcSet("wdc_timeline_data", tlStr);
      // Sync fps/duration hidden boxes from timeline data so Python handlers stay in sync
      if (tlObj.fps       !== undefined) wdcSet("wdc_fps",      String(tlObj.fps));
      if (tlObj.durationSec !== undefined) wdcSet("wdc_duration", String(tlObj.durationSec));
      if (tlObj.fps !== undefined && tlObj.durationSec !== undefined) {
        const fc = Math.max(1, Math.round(tlObj.durationSec * tlObj.fps)) + 1;
        wdcSet("wdc_frames", String(fc));
      }
    }
    if (d.local_prompts   !== undefined) wdcSet("wdc_local_prompts",   d.local_prompts);
    if (d.segment_lengths !== undefined) wdcSet("wdc_segment_lengths", d.segment_lengths);
    if (d.guide_strength  !== undefined) wdcSet("wdc_guide_strength",  d.guide_strength);
    if (d.frame_count     !== undefined) wdcSet("wdc_frame_count",     String(d.frame_count));
  });

  // OUTBOUND: intercept visible button clicks
  function wdcBindButtons() {
    const root = wdcRoot();

    // Apply
    const applyBtn = root.querySelector("#wdc-apply-btn button") || root.querySelector("#wdc-apply-btn");
    if (applyBtn && !applyBtn._wdcBound) {
      applyBtn._wdcBound = true;
      applyBtn.addEventListener("click", function(e) {
        e.stopImmediatePropagation();
        wdcSendToIframe("get_state");
        setTimeout(function() { wdcClickTrigger("wdc-apply-trigger"); }, 250);
      }, true);
    }

    // Generate Here: pull fresh timeline state, then fire the direct-gen
    // trigger. No tab switch / no button hunting — the WanGP plugin API queues
    // the job and streams the result into the inline player on this tab.
    const genHereBtn = root.querySelector("#wdc-generate-here-btn button") || root.querySelector("#wdc-generate-here-btn");
    if (genHereBtn && !genHereBtn._wdcBound) {
      genHereBtn._wdcBound = true;
      genHereBtn.addEventListener("click", function(e) {
        e.stopImmediatePropagation();
        wdcSendToIframe("get_state");
        setTimeout(function() { wdcClickTrigger("wdc-generate-here-trigger"); }, 300);
      }, true);
    }

    // Legacy Apply + Generate (older builds without the plugin gen API): if the
    // hidden generate trigger button is present and a visible legacy button
    // exists, keep the old JS relay working as a fallback.
    const genBtn = root.querySelector("#wdc-generate-btn button") || root.querySelector("#wdc-generate-btn");
    if (genBtn && !genBtn._wdcBound) {
      genBtn._wdcBound = true;
      genBtn.addEventListener("click", function(e) {
        e.stopImmediatePropagation();
        wdcSendToIframe("get_state");
        setTimeout(function() {
          wdcClickTrigger("wdc-generate-trigger");
          setTimeout(wdcSwitchToGenerateAndRun, 1200);
        }, 250);
      }, true);
    }

    // Preview
    const previewBtn = root.querySelector("#wdc-preview-btn button") || root.querySelector("#wdc-preview-btn");
    if (previewBtn && !previewBtn._wdcBound) {
      previewBtn._wdcBound = true;
      previewBtn.addEventListener("click", function(e) {
        e.stopImmediatePropagation();
        wdcSendToIframe("get_state");
        setTimeout(function() { wdcClickTrigger("wdc-preview-trigger"); }, 250);
      }, true);
    }

    // Clear
    const clearBtn = root.querySelector("#wdc-clear-btn button") || root.querySelector("#wdc-clear-btn");
    if (clearBtn && !clearBtn._wdcBound) {
      clearBtn._wdcBound = true;
      clearBtn.addEventListener("click", function(e) {
        e.stopImmediatePropagation();
        wdcSendToIframe("clear");
        wdcSet("wdc_timeline_data",   "{}");
        wdcSet("wdc_local_prompts",   "");
        wdcSet("wdc_segment_lengths", "");
        wdcSet("wdc_guide_strength",  "");
        setTimeout(function() { wdcClickTrigger("wdc-clear-trigger"); }, 250);
      }, true);
    }

    // Recover and Load are handled by Gradio's js= .then() — no interception needed here.
  }

  function wdcBindWithRetry(n) {
    const root = wdcRoot();
    const applyBtn = root.querySelector("#wdc-apply-btn button") || root.querySelector("#wdc-apply-btn");
    if (applyBtn) {
      wdcBindButtons();
      console.log("[LTXDirector] All buttons bound");
    } else if (n > 0) {
      setTimeout(function() { wdcBindWithRetry(n - 1); }, 300);
    } else {
      console.warn("[LTXDirector] Button bind timeout");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function() { wdcBindWithRetry(25); });
  } else {
    wdcBindWithRetry(25);
  }
})();
"""


# ---------------------------------------------------------------------------
# Timeline editor HTML/JS  (iframe content, base64-encoded at runtime)
# ---------------------------------------------------------------------------

TIMELINE_EDITOR_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LTX Director</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 100%; height: 100%; background: #1a1a1a; color: #e0e0e0; overflow: hidden; }
body { font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; font-size: 13px; display: flex; flex-direction: column; }

/* ── Toolbar ── */
#toolbar {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
  padding: 8px 10px; background: #111; border-bottom: 1px solid #333; flex-shrink: 0;
}
.btn {
  display: inline-flex; align-items: center; gap: 5px;
  background: #2a2a2a; color: #ddd; border: 1px solid #444;
  border-radius: 5px; padding: 5px 11px; font-size: 12px; cursor: pointer;
  transition: background .12s, border-color .12s, color .12s; white-space: nowrap;
  font-family: inherit;
}
.btn:hover { background: #383838; border-color: #666; color: #fff; }
.btn.danger:hover { background: #3a1515; border-color: #c33; color: #ffaaaa; }
.btn.primary { background: #1a4a2a; border-color: #2d7a44; color: #8ef0a8; }
.btn.primary:hover { background: #205a32; border-color: #3a9a54; color: #afffbf; }
.sep { width: 1px; height: 20px; background: #444; flex-shrink: 0; }
.lbl { font-size: 11px; color: #777; white-space: nowrap; }
.num-input {
  background: #222; border: 1px solid #444; border-radius: 4px;
  color: #ddd; font-size: 12px; width: 58px; padding: 4px 6px;
  text-align: center; font-family: inherit;
}
.num-input:focus { outline: none; border-color: #666; }
#timecode { font-size: 13px; font-family: monospace; color: #bbb; margin-left: auto; white-space: nowrap; }

/* ── Canvas wrap ── */
#canvas-wrap {
  position: relative; flex-shrink: 0;
  overflow: hidden;
  background: #222; border-bottom: 1px solid #333;
}
#timeline { display: block; cursor: default; }

/* ── Zoom/nav bar ── */
#zoom-bar-wrap {
  flex-shrink: 0; background: #111;
  border-bottom: 1px solid #2a2a2a; padding: 0;
  height: 28px; position: relative;
}
#zoom-bar { display: block; width: 100%; height: 28px; cursor: default; }

/* ── Properties panel ── */
#props {
  flex: 1; min-height: 0; overflow-y: auto;
  background: #1e1e1e; border-top: 1px solid #333; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 8px;
}
#prop-title { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: .05em; }
#prop-body { display: none; flex-direction: column; gap: 8px; }
#prop-body.visible { display: flex; }
.prop-row { display: flex; align-items: center; gap: 8px; }
.prop-label { font-size: 12px; color: #999; min-width: 90px; flex-shrink: 0; }
textarea#prop-prompt {
  width: 100%; background: #2a2a2a; color: #e0e0e0; border: 1px solid #444;
  border-radius: 5px; padding: 7px 9px; font-size: 12px; resize: vertical;
  min-height: 64px; outline: none; font-family: inherit; line-height: 1.45;
}
textarea#prop-prompt:focus { border-color: #666; }
input[type=range].slider {
  -webkit-appearance: none; appearance: none;
  height: 4px; background: #444; border-radius: 2px; outline: none; cursor: pointer; width: 120px;
}
input[type=range].slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 13px; height: 13px; border-radius: 50%; background: #aaa; cursor: pointer;
}
#prop-strength-val { font-size: 12px; color: #ccc; min-width: 32px; }
#prop-audio-info { font-size: 12px; color: #69b4ff; }
#prop-hint { font-size: 11px; color: #555; }
#status { font-size: 11px; color: #777; min-height: 15px; margin-top: 2px; }
</style>
</head>
<body>

<!-- Hidden file inputs -->
<input type="file" id="file-img"   accept="image/*"  multiple style="display:none">
<input type="file" id="file-audio" accept="audio/*"  multiple style="display:none">

<!-- Toolbar -->
<div id="toolbar">
  <button class="btn" id="btn-add-text">📝 Add Text</button>
  <button class="btn" id="btn-upload-img">🖼 Add Image</button>
  <button class="btn" id="btn-upload-audio">🎵 Add Audio</button>
  <div class="sep"></div>
  <span class="lbl">FPS</span>
  <input class="num-input" type="number" id="ctrl-fps" value="24" min="1" max="120" step="1">
  <span class="lbl">Duration (s)</span>
  <input class="num-input" type="number" id="ctrl-dur" value="5" min="0.5" max="600" step="0.5">
  <div class="sep"></div>
  <span class="lbl" title="Frames per sliding window — LTX 2.3 requires 8k+1 values (41, 49, … 129 … 417)">Win</span>
  <input class="num-input" type="number" id="ctrl-win" value="129" min="41" max="2001" step="8" title="Sliding window size (frames) — must be 8k+1 for LTX 2.3; typed values snap automatically">
  <span class="lbl" title="Overlap frames shared with the previous window — 8k+1 values (1, 9, 17 … 97)">Ovl</span>
  <input class="num-input" type="number" id="ctrl-ovl" value="9" min="1" max="97" step="8" title="Overlap frames — must be 8k+1 for LTX 2.3; new frames per window = size − overlap">
  <span class="lbl" id="win-info" style="color:#5a80b0" title="windows × new frames contributed by each window after the first"></span>
  <label class="lbl" style="display:inline-flex;align-items:center;gap:3px;cursor:pointer" title="Show sliding-window bands and boundary warnings">
    <input type="checkbox" id="ctrl-show-win" checked> bands
  </label>
  <div class="sep"></div>
  <button class="btn" id="btn-play">[Play]</button>
  <button class="btn danger" id="btn-clear">🗑 Clear</button>
  <span id="timecode">0.00s / 5.00s</span>
</div>

<!-- Timeline canvas -->
<div id="canvas-wrap">
  <canvas id="timeline"></canvas>
</div>

<!-- Zoom/navigation bar -->
<div id="zoom-bar-wrap">
  <canvas id="zoom-bar"></canvas>
</div>

<!-- Properties -->
<div id="props">
  <div id="prop-title">No segment selected — click a segment to edit · Double-click a gap to add text · Drag &amp; drop images or audio onto the timeline</div>
  <div id="prop-body">
    <textarea id="prop-prompt" placeholder="Describe what happens in this segment…" rows="3"></textarea>
    <div class="prop-row" id="prop-strength-row">
      <span class="prop-label">Guide strength</span>
      <input type="range" class="slider" id="prop-strength" min="0" max="1" step="0.01" value="1">
      <span id="prop-strength-val">1.00</span>
    </div>
    <div id="prop-audio-info"></div>
    <div class="prop-row" id="prop-warning" style="display:none;flex-wrap:wrap;gap:6px;background:#2e2310;border:1px solid #6a5020;border-radius:5px;padding:6px 8px;">
      <span id="prop-warning-text" style="color:#ffb84d;font-size:12px;flex-basis:100%;"></span>
      <button class="btn" id="btn-fix-trim"  title="Shorten this segment so it ends at the window boundary">✂ Trim to boundary</button>
      <button class="btn" id="btn-fix-move"  title="Move this segment so it starts at the next window">➡ Move to next window</button>
      <button class="btn" id="btn-fix-split" title="Split this segment into two at the boundary">⎮ Split at boundary</button>
    </div>
    <div class="prop-row">
      <button class="btn danger" id="btn-del-seg">🗑 Delete segment</button>
    </div>
  </div>
  <div id="prop-hint">Drag segments to move · Drag edge to resize · Double-click gap to add text · Drop files onto timeline · Scroll wheel to zoom · Shift+drag or middle-drag to pan</div>
  <div id="win-warnings" style="display:none;color:#ffb84d;font-size:12px;padding:4px 0;">
    <span id="win-warnings-text"></span>
    <button class="btn" id="btn-fix-all-split" style="margin-left:8px" title="Split every crossing asset at its window boundaries">⎮ Split All</button>
  </div>
  <div id="status"></div>
</div>

<script>
(function () {
'use strict';

// ── Layout constants ────────────────────────────────────────────────────────
const RULER_H  = 26;
const WIN_H    = 16;                 // sliding-window band strip
const TRACK_Y  = RULER_H + WIN_H;    // top of the video track
const IMG_H    = 148;
const AUDIO_H  = 64;
const TOTAL_H  = RULER_H + WIN_H + IMG_H + AUDIO_H;
const HANDLE   = 10;   // px of resize handle at each edge
const MIN_LEN  = 4;    // minimum segment length in frames

// ── State ───────────────────────────────────────────────────────────────────
let fps = 24;
let durSec = 5;
function durF() { return Math.max(1, Math.round(durSec * fps)); }

let segs  = [];   // {id,type:'image'|'text',start,length,prompt,imageB64,imgObj,guideStrength}
let audio = [];   // {id,type:'audio',start,length,trimStart,audioB64,fileName}

// ── Sliding windows ──────────────────────────────────────────────────────────
let winSize     = 129;   // frames per sliding window (WanGP LTX default)
let winOverlap  = 9;     // overlap frames between consecutive windows
let showWindows = true;  // draw window bands + boundary warnings

// LTX 2.3 frame grid: the VAE compresses time 8 frames per latent, so
// window size, overlap and total frames must all be 8k+1. New frames per
// window = size - overlap (a multiple of 8) — e.g. 417 - 17 = 400.
function snapLTX(v, lo, hi) {
  v = parseInt(v); if (isNaN(v)) v = lo;
  let s = Math.round((v - 1) / 8) * 8 + 1;
  s = Math.max(lo, s);
  if (hi !== undefined) s = Math.min(hi, s);
  return s;
}
function snapWindowPair(ws, ov) {
  ws = snapLTX(ws, 41);
  ov = snapLTX(ov, 1, 97);
  while (ov >= ws && ov > 1) ov -= 8;
  return [ws, Math.max(1, ov)];
}
function newFramesPerWindow() { return winSize - winOverlap; }

// Returns [{i, start, end}] — window i spans [start, end). Window 0 starts
// at 0; each subsequent window starts at the previous start + (size - overlap).
function getWindows() {
  const dF = durF();
  const ws = Math.max(8, winSize|0);
  const ov = Math.min(Math.max(0, winOverlap|0), ws - 1);
  const stride = ws - ov;
  const out = [];
  let s = 0, i = 0;
  while (s < dF && i < 500) {
    out.push({ i, start: s, end: Math.min(s + ws, dF) });
    if (s + ws >= dF) break;
    s += stride; i++;
  }
  return out;
}

// Boundaries a segment can "cross": the start frame of every window after
// the first. A segment spanning one of these gets generated across two
// separate windows, which can cause identity/motion discontinuities.
function windowBoundaries() {
  return getWindows().filter(w => w.i > 0).map(w => w.start);
}

function crossingBoundaries(seg) {
  if (!showWindows) return [];
  const res = [];
  for (const b of windowBoundaries()) {
    if (seg.start < b && seg.start + seg.length > b) res.push(b);
  }
  return res;
}

function allCrossingSegs() {
  const out = [];
  for (const s of segs)  { const c = crossingBoundaries(s); if (c.length) out.push({seg: s, track: 'image', boundaries: c}); }
  for (const s of audio) { const c = crossingBoundaries(s); if (c.length) out.push({seg: s, track: 'audio', boundaries: c}); }
  return out;
}

let selTrack = 'image';   // 'image' | 'audio'
let selId    = null;

let playhead = 0;
let playing  = false;
let rafId    = null;
let playT0   = 0;
let playF0   = 0;

// ── Drag ────────────────────────────────────────────────────────────────────
let drag = null;
// {track,id,zone:'move'|'left'|'right',ox,oStart,oLen}

// ── DOM ─────────────────────────────────────────────────────────────────────
const canvas     = document.getElementById('timeline');
const ctx        = canvas.getContext('2d');
const wrap       = document.getElementById('canvas-wrap');
const propBody   = document.getElementById('prop-body');
const propTitle  = document.getElementById('prop-title');
const propPrompt = document.getElementById('prop-prompt');
const propStr    = document.getElementById('prop-strength');
const propStrVal = document.getElementById('prop-strength-val');
const propStrRow = document.getElementById('prop-strength-row');
const propAudio  = document.getElementById('prop-audio-info');
const timecode   = document.getElementById('timecode');
const statusEl   = document.getElementById('status');
const btnPlay    = document.getElementById('btn-play');

// ── ID ───────────────────────────────────────────────────────────────────────
let _id = 0;
function uid() { return 's' + (++_id) + '_' + Math.random().toString(36).slice(2,6); }

// ── Canvas sizing ────────────────────────────────────────────────────────────
function resizeCanvas() {
  const w = Math.max(wrap.clientWidth || 800, 400);
  canvas.width  = w;
  canvas.height = TOTAL_H;
  render();
}
const ro = new ResizeObserver(resizeCanvas);
ro.observe(wrap);

// ── Coordinate helpers ───────────────────────────────────────────────────────

// View window — the range of frames [viewStart, viewEnd] visible on the canvas.
// Initially the full timeline is visible.
let viewStart = 0;         // first frame visible (can be fractional)
let viewEnd   = durF();    // last frame visible  (can be fractional)

// Clamp viewEnd when durF() changes
function syncView() {
  const df = durF();
  const span = Math.max(1, viewEnd - viewStart);
  viewEnd   = Math.min(df, viewEnd);
  viewStart = Math.max(0, viewEnd - span);
  if (viewEnd - viewStart < 1) { viewStart = 0; viewEnd = df; }
}

function viewSpan() { return Math.max(1, viewEnd - viewStart); }

// Frame → canvas pixel (within the current view window)
function fToPx(f) {
  return ((f - viewStart) / viewSpan()) * canvas.width;
}

// Canvas pixel → frame (within the current view window)
function pxToF(px) {
  return Math.round(clamp(viewStart + (px / canvas.width) * viewSpan(), 0, durF()));
}

// Exact (non-rounded) pixel → frame, used for zoom pivot
function pxToFExact(px) {
  return clamp(viewStart + (px / canvas.width) * viewSpan(), 0, durF());
}

// Frame LENGTH → pixel WIDTH.  (fToPx is for POSITIONS — it subtracts
// viewStart, which is wrong for widths and caused segments to shrink
// to slivers when zoomed in.)
function fToW(frames) {
  return (frames / viewSpan()) * canvas.width;
}

function clamp(v,lo,hi) { return Math.max(lo, Math.min(hi, v)); }

// ── Zoom helpers ──────────────────────────────────────────────────────────────
const MIN_ZOOM_FRAMES = 2;   // can't zoom in further than 2 frames visible

function zoomAt(pivotPx, factor) {
  // factor > 1 = zoom in (fewer frames visible), < 1 = zoom out
  const pivotF = pxToFExact(pivotPx);
  let span = viewSpan() / factor;
  span = Math.max(MIN_ZOOM_FRAMES, Math.min(durF(), span));

  // Keep pivot frame under cursor
  const leftRatio = pivotPx / canvas.width;
  viewStart = pivotF - leftRatio * span;
  viewEnd   = viewStart + span;

  // Clamp to [0, durF()]
  if (viewStart < 0) { viewEnd -= viewStart; viewStart = 0; }
  if (viewEnd > durF()) { viewStart -= (viewEnd - durF()); viewEnd = durF(); }
  viewStart = Math.max(0, viewStart);
  viewEnd   = Math.min(durF(), viewEnd);
}

function panBy(deltaF) {
  const span = viewSpan();
  viewStart = clamp(viewStart + deltaF, 0, durF() - span);
  viewEnd   = viewStart + span;
}

// ── Render ───────────────────────────────────────────────────────────────────
function render() {
  const W = canvas.width;
  ctx.clearRect(0, 0, W, TOTAL_H);

  // Track backgrounds
  ctx.fillStyle = '#252525'; ctx.fillRect(0, TRACK_Y, W, IMG_H);
  ctx.fillStyle = '#1c1c1c'; ctx.fillRect(0, TRACK_Y + IMG_H, W, AUDIO_H);

  // Sliding-window bands (under segments, over backgrounds)
  drawWindowBands(W);

  // Track labels
  ctx.fillStyle = '#444'; ctx.font = '10px sans-serif';
  ctx.fillText('VIDEO  (images · text prompts)', 8, TRACK_Y + 14);
  ctx.fillText('AUDIO', 8, TRACK_Y + IMG_H + 14);

  // Track separator line
  ctx.strokeStyle = '#333'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(0, TRACK_Y + IMG_H); ctx.lineTo(W, TRACK_Y + IMG_H); ctx.stroke();

  // Ruler
  drawRuler(W);

  // Segments
  segs.forEach(s  => drawSeg(s,  'image'));
  audio.forEach(s => drawSeg(s, 'audio'));

  // Playhead
  const ph = fToPx(playhead);
  ctx.strokeStyle = '#ff4444'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(ph, 0); ctx.lineTo(ph, TOTAL_H); ctx.stroke();
  // Playhead triangle
  ctx.fillStyle = '#ff4444';
  ctx.beginPath(); ctx.moveTo(ph-5,0); ctx.lineTo(ph+5,0); ctx.lineTo(ph,8); ctx.fill();

  // Timecode
  const tc = (playhead/fps).toFixed(2);
  const tot = durSec.toFixed(2);
  timecode.textContent = tc + 's / ' + tot + 's';

  updateWinWarnings();
  updateWinInfo();
}

// Alternating colored bands marking each sliding window, plus overlap
// regions and boundary lines.
function drawWindowBands(W) {
  // Strip background always drawn so the layout doesn't jump when toggled
  ctx.fillStyle = '#181818';
  ctx.fillRect(0, RULER_H, W, WIN_H);
  if (!showWindows) return;

  const wins = getWindows();
  const ov   = Math.min(Math.max(0, winOverlap|0), Math.max(8, winSize|0) - 1);
  // Alternating hues: steel blue / amber
  const hues = ['64,118,208', '208,148,64'];

  for (const w of wins) {
    const x0 = fToPx(w.start);
    const x1 = fToPx(w.end);
    if (x1 < 0 || x0 > W) continue;          // off-screen
    const bw = Math.max(1, x1 - x0);
    const c  = hues[w.i % 2];

    // Band in the strip
    ctx.fillStyle = 'rgba(' + c + ',0.85)';
    ctx.fillRect(x0, RULER_H + 2, bw, WIN_H - 4);

    // Faint tint over both tracks
    ctx.fillStyle = 'rgba(' + c + ',0.05)';
    ctx.fillRect(x0, TRACK_Y, bw, IMG_H + AUDIO_H);

    // Overlap region (shared with previous window) — lighter hatch
    if (w.i > 0 && ov > 0) {
      const ox1 = fToPx(Math.min(w.start + ov, durF()));
      const ow  = Math.max(1, ox1 - x0);
      ctx.fillStyle = 'rgba(255,255,255,0.22)';
      ctx.fillRect(x0, RULER_H + 2, ow, WIN_H - 4);
      ctx.fillStyle = 'rgba(255,200,80,0.08)';
      ctx.fillRect(x0, TRACK_Y, ow, IMG_H + AUDIO_H);
    }

    // Dashed boundary line at the start of every window after the first
    if (w.i > 0) {
      ctx.strokeStyle = 'rgba(255,200,80,0.55)';
      ctx.lineWidth = 1; ctx.setLineDash([4,3]);
      ctx.beginPath(); ctx.moveTo(x0, RULER_H); ctx.lineTo(x0, TOTAL_H); ctx.stroke();
      ctx.setLineDash([]);
    }

    // Window label (+ new-frame contribution for windows after the first)
    if (bw > 30) {
      ctx.fillStyle = '#e8eeff'; ctx.font = 'bold 9px monospace';
      let lbl = 'W' + (w.i + 1);
      if (w.i > 0 && bw > 70) lbl += ' +' + newFramesPerWindow();
      ctx.fillText(lbl, x0 + 4, RULER_H + WIN_H - 5);
    }
  }
}

// Toolbar readout: "→ N win × M new" (M = frames each window adds after the first)
function updateWinInfo() {
  const el = document.getElementById('win-info');
  if (!el) return;
  if (durF() <= winSize) { el.textContent = '→ single window'; return; }
  el.textContent = '→ ' + getWindows().length + ' win × ' + newFramesPerWindow() + ' new';
}

function drawRuler(W) {
  ctx.fillStyle = '#2a2a2a'; ctx.fillRect(0, 0, W, RULER_H);
  // Ruler ticks — based on the VISIBLE span so tick density stays
  // constant while zooming (previously used full durF(), so zooming in
  // left huge gaps between ticks).
  const targetMarks = Math.max(4, Math.floor(W / 90));
  const rawStep = viewSpan() / targetMarks;
  const niceSteps = [1,2,5,10,15,24,30,48,60,120,240,480,960];
  const step = niceSteps.reduce((p,c) => Math.abs(c-rawStep)<Math.abs(p-rawStep)?c:p);

  ctx.fillStyle = '#888'; ctx.font = '10px monospace'; ctx.textBaseline = 'top';
  const first = Math.max(0, Math.ceil(viewStart / step) * step);
  for (let f = first; f <= Math.min(viewEnd, durF()); f += step) {
    const x = fToPx(f);
    ctx.strokeStyle = '#555'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x, RULER_H-6); ctx.lineTo(x, RULER_H); ctx.stroke();
    const label = (f/fps).toFixed(step < fps ? 2 : 1) + 's';
    if (x + 4 < W) ctx.fillText(label, x+2, 5);
  }
  ctx.textBaseline = 'alphabetic';
}

function drawSeg(seg, track) {
  const isAudio = track === 'audio';
  const trackY  = isAudio ? TRACK_Y + IMG_H : TRACK_Y;
  const trackH  = isAudio ? AUDIO_H : IMG_H;
  const x = fToPx(seg.start);
  const w = Math.max(fToW(seg.length), 2);
  const sel = selId === seg.id && selTrack === track;

  // Background fill
  let fill;
  if (isAudio)           fill = sel ? '#1a4570' : '#142e4e';
  else if (seg.type==='text') fill = sel ? '#3a2e5a' : '#261e3e';
  else                        fill = sel ? '#1a4a2a' : '#102e18';

  ctx.fillStyle = fill;
  roundRect(x, trackY+2, w, trackH-4, 4);
  ctx.fill();

  // Image thumbnail (tiled)
  if (!isAudio && seg.type==='image' && seg.imgObj?.complete && seg.imgObj.naturalWidth > 0) {
    ctx.save();
    ctx.beginPath(); roundRect(x+2, trackY+4, w-4, trackH-8, 3); ctx.clip();
    const ih = trackH - 8;
    const iw = Math.max(1, Math.round(seg.imgObj.naturalWidth * ih / seg.imgObj.naturalHeight));
    for (let tx = x+2; tx < x+w-2; tx += iw) {
      ctx.drawImage(seg.imgObj, tx, trackY+4, Math.min(iw, x+w-2-tx), ih);
    }
    ctx.restore();
  }

  // Audio waveform — real peaks from the decoded buffer, computed per
  // visible pixel column in source-audio space (so zooming in shows more
  // detail). Falls back to a frame-anchored placeholder while decoding.
  if (isAudio) {
    // Only draw the on-screen part of the clip
    const visX0 = Math.max(0, Math.floor(x));
    const visX1 = Math.min(canvas.width, Math.ceil(x + w));
    if (visX1 > visX0) {
      const peaks = getPeaks(seg, Math.max(1, Math.round(w)));
      ctx.save();
      ctx.beginPath(); roundRect(x, trackY+2, w, trackH-4, 4); ctx.clip();
      if (peaks) {
        ctx.fillStyle = '#2a7abf';
        const mid = trackY + trackH / 2;
        for (let px = visX0; px < visX1; px++) {
          const c = Math.min(peaks.length - 1, Math.floor(px - x));
          const half = Math.max(0.5, peaks[c] * (trackH - 10) / 2);
          ctx.fillRect(px, mid - half, 1, half * 2);
        }
      } else {
        // Placeholder anchored to SOURCE FRAMES (not pixels) so it
        // stretches consistently with zoom while the clip decodes.
        ensureDecoded(seg);
        ctx.fillStyle = '#1f5a8d';
        const mid = trackY + trackH / 2;
        for (let px = visX0; px < visX1; px += 2) {
          const localF = (seg.trimStart||0) + ((px - x) / w) * seg.length;
          const half = (trackH*0.12) + (trackH*0.28) * Math.abs(Math.sin(localF * 0.37));
          ctx.fillRect(px, mid - half, 2, half * 2);
        }
      }
      ctx.restore();
    }
    // File name
    if (w > 30) {
      ctx.save();
      ctx.beginPath(); ctx.rect(x+4, trackY+2, w-8, AUDIO_H-4); ctx.clip();
      ctx.fillStyle = '#9ad0ff'; ctx.font = '10px sans-serif';
      ctx.fillText(seg.fileName || 'audio', x+5, trackY+AUDIO_H-6);
      ctx.restore();
    }
  }

  // Prompt overlay at bottom of video segments
  if (!isAudio && seg.prompt && w > 20) {
    const oH = Math.max(16, Math.round(trackH * 0.22));
    const oY = trackY + trackH - oH - 2;
    ctx.save();
    ctx.beginPath(); ctx.rect(x+2, oY, w-4, oH); ctx.clip();
    ctx.fillStyle = 'rgba(0,0,0,0.68)'; ctx.fillRect(x+2, oY, w-4, oH);
    ctx.fillStyle = '#dde2f0'; ctx.font = `${Math.min(11, Math.floor(oH*0.62))}px sans-serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    let lbl = seg.prompt;
    const maxW = w - 12;
    while (lbl.length > 1 && ctx.measureText(lbl+'…').width > maxW) lbl = lbl.slice(0,-1);
    if (lbl !== seg.prompt) lbl += '…';
    ctx.fillText(lbl, x + w/2, oY + oH/2);
    ctx.restore();
    ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  }

  // Type icon for text-only segments
  if (!isAudio && seg.type==='text' && w > 30) {
    ctx.fillStyle = '#9090d0'; ctx.font = 'bold 13px sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('T', x + Math.min(18, w/2), trackY + trackH/2 - (seg.prompt?12:0));
    ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  }

  // Border — amber dashed if the segment crosses a sliding-window boundary
  const crosses = crossingBoundaries(seg);
  if (crosses.length) {
    ctx.strokeStyle = '#ffb84d';
    ctx.lineWidth = 2; ctx.setLineDash([5,3]);
    roundRect(x, trackY+2, w, trackH-4, 4); ctx.stroke();
    ctx.setLineDash([]);
    // Warning marker + tick at each crossed boundary
    ctx.fillStyle = '#ffb84d'; ctx.font = 'bold 11px sans-serif';
    if (w > 22) ctx.fillText('⚠', x + w - 16, trackY + 15);
    for (const b of crosses) {
      const bx = fToPx(b);
      ctx.strokeStyle = 'rgba(255,120,60,0.9)'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(bx, trackY+2); ctx.lineTo(bx, trackY+trackH-2); ctx.stroke();
    }
  } else {
    ctx.strokeStyle = sel ? '#fff' : (isAudio ? '#2a7abf' : (seg.type==='text' ? '#6060b0' : '#2a7a4a'));
    ctx.lineWidth = sel ? 2 : 1;
    roundRect(x, trackY+2, w, trackH-4, 4); ctx.stroke();
  }
  if (sel && crosses.length) {
    // Keep the white selection ring visible on warned segments
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 1;
    roundRect(x-1, trackY+1, w+2, trackH-2, 5); ctx.stroke();
  }

  // Resize handles if selected
  if (sel) {
    ctx.fillStyle = '#fff';
    [[x, trackY+trackH/2-14, 4, 28], [x+w-4, trackY+trackH/2-14, 4, 28]].forEach(([hx,hy,hw,hh])=>{
      ctx.beginPath(); ctx.roundRect(hx,hy,hw,hh,2); ctx.fill();
    });
  }
}

function roundRect(x,y,w,h,r) {
  if (w < 2*r) r = w/2; if (h < 2*r) r = h/2;
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y);
  ctx.quadraticCurveTo(x+w,y,x+w,y+r);
  ctx.lineTo(x+w,y+h-r); ctx.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
  ctx.lineTo(x+r,y+h); ctx.quadraticCurveTo(x,y+h,x,y+h-r);
  ctx.lineTo(x,y+r); ctx.quadraticCurveTo(x,y,x+r,y);
  ctx.closePath();
}

// ── Hit-testing ───────────────────────────────────────────────────────────
function hitTest(mx, my) {
  if (my < TRACK_Y) return null;            // ruler / window strip
  const isAud = my >= TRACK_Y + IMG_H;
  const arr   = isAud ? audio : segs;
  const track = isAud ? 'audio' : 'image';
  for (let i = arr.length-1; i >= 0; i--) {
    const s = arr[i];
    const sx = fToPx(s.start), sw = fToW(s.length);
    if (mx >= sx - HANDLE/2 && mx <= sx + sw + HANDLE/2) {
      let zone = 'move';
      if (mx < sx + HANDLE) zone = 'left';
      else if (mx > sx + sw - HANDLE) zone = 'right';
      return { track, id: s.id, zone };
    }
  }
  return null;
}

// ── Mouse events ─────────────────────────────────────────────────────────
canvas.addEventListener('mousedown', e => {
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;

  // Seek on ruler / window-strip click
  if (my < TRACK_Y) {
    setPlayhead(pxToF(mx)); return;
  }

  const hit = hitTest(mx, my);
  if (hit) {
    selTrack = hit.track; selId = hit.id;
    const arr = hit.track==='audio' ? audio : segs;
    const s   = arr.find(x => x.id === hit.id);
    drag = { track: hit.track, id: hit.id, zone: hit.zone, ox: mx, oStart: s.start, oLen: s.length };
    updateProps(); render();
  } else {
    selId = null; updateProps(); render();
  }
});

canvas.addEventListener('mousemove', e => {
  if (!drag) return;
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left;
  const df = Math.round(pxToFExact(mx) - pxToFExact(drag.ox));
  const arr = drag.track==='audio' ? audio : segs;
  const s   = arr.find(x => x.id === drag.id);
  if (!s) return;

  if (drag.zone==='move') {
    s.start = clamp(drag.oStart + df, 0, durF() - s.length);
  } else if (drag.zone==='left') {
    const ns = clamp(drag.oStart + df, 0, drag.oStart + drag.oLen - MIN_LEN);
    const delta = ns - s.start;
    s.start  = ns;
    s.length = Math.max(MIN_LEN, drag.oLen - (ns - drag.oStart));
    if (drag.track==='audio') s.trimStart = Math.max(0, (s.trimStart||0) + delta);
  } else {
    s.length = Math.max(MIN_LEN, drag.oLen + df);
  }
  render();
});

canvas.addEventListener('mouseup',    () => { if (drag) { drag=null; commit(); } });
canvas.addEventListener('mouseleave', () => { if (drag) { drag=null; commit(); } });

// Cursor style
canvas.addEventListener('mousemove', e => {
  if (drag) return;
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;
  if (my < TRACK_Y) { canvas.style.cursor = 'col-resize'; return; }
  const hit = hitTest(mx, my);
  if (!hit) { canvas.style.cursor = 'crosshair'; return; }
  if (hit.zone==='left'||hit.zone==='right') canvas.style.cursor = 'ew-resize';
  else canvas.style.cursor = 'grab';
});

// ── Mouse wheel → zoom ───────────────────────────────────────────────────────
canvas.addEventListener('wheel', e => {
  e.preventDefault();
  const r    = canvas.getBoundingClientRect();
  const mx   = e.clientX - r.left;
  // deltaY > 0 = scroll down = zoom out; < 0 = zoom in
  const factor = e.deltaY < 0 ? 1.25 : 1 / 1.25;
  zoomAt(mx, factor);
  render();
  renderZoomBar();
}, { passive: false });

// ── Middle-mouse / Shift+drag → pan ──────────────────────────────────────────
let panDrag = null;  // { startX, startViewStart }

canvas.addEventListener('mousedown', e => {
  if (e.button === 1 || (e.button === 0 && e.shiftKey)) {
    e.preventDefault();
    const r = canvas.getBoundingClientRect();
    panDrag = { startX: e.clientX - r.left, startViewStart: viewStart };
  }
}, true);  // capture so it fires before the existing mousedown

canvas.addEventListener('mousemove', e => {
  if (!panDrag) return;
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left;
  const dF = ((panDrag.startX - mx) / canvas.width) * viewSpan();
  const span = viewSpan();
  viewStart = clamp(panDrag.startViewStart + dF, 0, durF() - span);
  viewEnd   = viewStart + span;
  render();
  renderZoomBar();
}, true);

canvas.addEventListener('mouseup', e => {
  if (e.button === 1 || panDrag) panDrag = null;
}, true);

canvas.addEventListener('mouseleave', () => { panDrag = null; });

// Double-click on gap → add text segment
canvas.addEventListener('dblclick', e => {
  const r  = canvas.getBoundingClientRect();
  const mx = e.clientX - r.left, my = e.clientY - r.top;
  if (my < TRACK_Y || my >= TRACK_Y + IMG_H) return;
  const hit = hitTest(mx, my);
  if (!hit) addText(clamp(pxToF(mx) - Math.round(fps), 0, durF() - MIN_LEN*2));
});

// ── Drag-and-drop files ───────────────────────────────────────────────────
canvas.addEventListener('dragover',  e => { e.preventDefault(); wrap.style.outline = '2px dashed #666'; });
canvas.addEventListener('dragleave', ()=> { wrap.style.outline = ''; });
canvas.addEventListener('drop', e => {
  e.preventDefault(); wrap.style.outline = '';
  const r     = canvas.getBoundingClientRect();
  const mx    = e.clientX - r.left, my = e.clientY - r.top;
  const isAud = my >= TRACK_Y + IMG_H;
  const atF   = clamp(pxToF(mx), 0, durF());
  const files = Array.from(e.dataTransfer.files);
  const imgs  = files.filter(f => f.type.startsWith('image/'));
  const auds  = files.filter(f => f.type.startsWith('audio/'));
  if (isAud || (auds.length > 0 && imgs.length === 0)) {
    auds.forEach(f => loadAudio(f, atF));
  } else {
    imgs.forEach((f,i) => loadImage(f, clamp(atF + i*fps, 0, durF())));
    if (imgs.length === 0) auds.forEach(f => loadAudio(f, atF));
  }
});

// ── Segment creators ──────────────────────────────────────────────────────
function addText(startF) {
  const s = { id:uid(), type:'text', start:startF, length:Math.round(fps*2), prompt:'', guideStrength:1 };
  segs.push(s);
  selTrack='image'; selId=s.id;
  updateProps(); render(); commit();
  propPrompt.focus();
}

function loadImage(file, startF) {
  const reader = new FileReader();
  reader.onload = ev => {
    const b64 = ev.target.result;
    const img = new Image();
    img.onload = () => {
      const s = { id:uid(), type:'image', start:startF, length:Math.round(fps*2), prompt:'', imageB64:b64, imgObj:img, guideStrength:1 };
      segs.push(s);
      selTrack='image'; selId=s.id;
      updateProps(); setStatus('Image: ' + file.name); render(); commit();
    };
    img.src = b64;
  };
  reader.readAsDataURL(file);
}

function loadAudio(file, startF) {
  const reader = new FileReader();
  reader.onload = ev => {
    const b64 = ev.target.result;
    const a   = new Audio(b64);
    a.addEventListener('loadedmetadata', () => {
      const lenF = Math.max(MIN_LEN, Math.round(a.duration * fps));
      const s = { id:uid(), type:'audio', start:startF, length:lenF, trimStart:0, audioB64:b64, fileName:file.name };
      audio.push(s);
      selTrack='audio'; selId=s.id;
      ensureDecoded(s);
      updateProps(); setStatus('Audio: ' + file.name + ' (' + a.duration.toFixed(2) + 's)'); render(); commit();
    });
    a.addEventListener('error', () => {
      setStatus('Could not read audio duration for ' + file.name + ' — added with default length.');
      const s = { id:uid(), type:'audio', start:startF, length:Math.round(fps*3), trimStart:0, audioB64:b64, fileName:file.name };
      audio.push(s);
      selTrack='audio'; selId=s.id;
      ensureDecoded(s);
      updateProps(); render(); commit();
    });
  };
  reader.readAsDataURL(file);
}

// ── Web Audio playback engine ────────────────────────────────────────────────
let actx = null;
const decoded = {};       // seg.id → AudioBuffer
const activeSrcs = {};    // seg.id → AudioBufferSourceNode (currently playing)

function getActx() {
  if (!actx || actx.state === 'closed') {
    actx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return actx;
}

// Decode a segment's base64 audio into an AudioBuffer (idempotent).
// Re-renders when done so the real waveform replaces the placeholder.
async function ensureDecoded(seg) {
  if (decoded[seg.id] || !seg.audioB64) return;
  try {
    let b64 = seg.audioB64;
    if (b64.includes(',')) b64 = b64.split(',')[1];
    const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    decoded[seg.id] = await getActx().decodeAudioData(bytes.buffer.slice(0));
    peakCache.clear();      // waveform can now be drawn for real
    render();
  } catch (err) {
    console.warn('[LTXDirector] audio decode failed for', seg.fileName || seg.id, err);
  }
}

async function preDecodeAll() {
  for (const s of audio) await ensureDecoded(s);
}

function stopAllAudio() {
  for (const id in activeSrcs) {
    try { activeSrcs[id].stop(); } catch(e) {}
    delete activeSrcs[id];
  }
}

// Schedule every audio clip relative to the playhead frame `fromF`.
function startAudioFrom(fromF) {
  stopAllAudio();
  const ac = getActx();
  if (ac.state === 'suspended') ac.resume();
  const now = ac.currentTime;
  const phS = fromF / fps;

  for (const seg of audio) {
    const buf = decoded[seg.id];
    if (!buf) continue;
    const clipStartS = seg.start / fps;
    const clipEndS   = (seg.start + seg.length) / fps;
    const trimS      = (seg.trimStart || 0) / fps;
    if (phS >= clipEndS) continue;                     // already passed

    const delay  = phS < clipStartS ? clipStartS - phS : 0;
    const offset = phS > clipStartS ? trimS + (phS - clipStartS) : trimS;
    const dur    = clipEndS - Math.max(phS, clipStartS);
    if (dur <= 0 || offset >= buf.duration) continue;

    const src = ac.createBufferSource();
    src.buffer = buf;
    src.connect(ac.destination);
    src.start(now + delay, Math.min(offset, buf.duration), Math.min(dur, buf.duration - offset));
    activeSrcs[seg.id] = src;
  }
}

// ── Waveform peak computation (zoom-aware, cached) ───────────────────────────
// Peaks are computed in SOURCE-AUDIO space per on-screen pixel column, so
// zooming in genuinely reveals more waveform detail.
const peakCache = new Map();   // key → Float32Array of per-column peaks

function getPeaks(seg, nCols) {
  const buf = decoded[seg.id];
  if (!buf || nCols < 1) return null;
  const key = seg.id + '|' + nCols + '|' + seg.length + '|' + (seg.trimStart || 0) + '|' + fps;
  let peaks = peakCache.get(key);
  if (peaks) return peaks;
  if (peakCache.size > 200) peakCache.clear();   // crude cap

  const ch = buf.getChannelData(0);
  const sr = buf.sampleRate;
  const srcStart = ((seg.trimStart || 0) / fps) * sr;          // clip start in samples
  const srcLen   = (seg.length / fps) * sr;                    // clip length in samples
  peaks = new Float32Array(nCols);
  for (let c = 0; c < nCols; c++) {
    let s0 = Math.floor(srcStart + (c / nCols) * srcLen);
    let s1 = Math.min(ch.length, Math.ceil(srcStart + ((c + 1) / nCols) * srcLen));
    if (s0 >= ch.length) break;
    if (s1 <= s0) s1 = s0 + 1;
    const stride = Math.max(1, Math.floor((s1 - s0) / 32));    // sample ≤32 points/col
    let peak = 0;
    for (let s = s0; s < s1; s += stride) {
      const v = Math.abs(ch[s]);
      if (v > peak) peak = v;
    }
    peaks[c] = peak;
  }
  peakCache.set(key, peaks);
  return peaks;
}

// ── Toolbar buttons ───────────────────────────────────────────────────────
document.getElementById('btn-add-text').addEventListener('click', () => {
  addText(clamp(playhead, 0, durF() - MIN_LEN*2));
});
document.getElementById('btn-upload-img').addEventListener('click', () => {
  document.getElementById('file-img').click();
});
document.getElementById('btn-upload-audio').addEventListener('click', () => {
  document.getElementById('file-audio').click();
});
document.getElementById('file-img').addEventListener('change', e => {
  Array.from(e.target.files).forEach((f,i) => loadImage(f, clamp(playhead + i*fps, 0, durF())));
  e.target.value = '';
});
document.getElementById('file-audio').addEventListener('change', e => {
  Array.from(e.target.files).forEach(f => loadAudio(f, clamp(playhead, 0, durF())));
  e.target.value = '';
});

document.getElementById('ctrl-fps').addEventListener('change', e => {
  fps = Math.max(1, parseInt(e.target.value)||24);
  syncView(); viewEnd = Math.max(viewEnd, durF()); render(); renderZoomBar(); commit();
});
document.getElementById('ctrl-dur').addEventListener('change', e => {
  durSec = Math.max(0.5, parseFloat(e.target.value)||5);
  syncView(); viewEnd = Math.max(viewEnd, durF()); render(); renderZoomBar(); commit();
});
document.getElementById('ctrl-win').addEventListener('change', e => {
  const typed = parseInt(e.target.value) || 129;
  const [ws, ov] = snapWindowPair(typed, winOverlap);
  winSize = ws; winOverlap = ov;
  e.target.value = winSize;
  document.getElementById('ctrl-ovl').value = winOverlap;
  if (ws !== typed) setStatus('Window size snapped ' + typed + ' → ' + ws + ' (LTX 2.3 needs 8k+1 frames).');
  render(); commit();
});
document.getElementById('ctrl-ovl').addEventListener('change', e => {
  const typed = parseInt(e.target.value) || 9;
  const [ws, ov] = snapWindowPair(winSize, typed);
  winSize = ws; winOverlap = ov;
  e.target.value = winOverlap;
  if (ov !== typed) setStatus('Overlap snapped ' + typed + ' → ' + ov + ' (LTX 2.3 needs 8k+1; e.g. 1, 9, 17). New frames/window: ' + newFramesPerWindow() + '.');
  render(); commit();
});
document.getElementById('ctrl-show-win').addEventListener('change', e => {
  showWindows = !!e.target.checked;
  render();
});

// Play/pause
function setPlayhead(f) {
  playhead = clamp(f,0,durF());
  if (playing) {                      // re-sync audio when seeking mid-play
    playT0 = performance.now(); playF0 = playhead;
    startAudioFrom(playhead);
  }
  render();
}

function tick() {
  const elapsed = (performance.now() - playT0) / 1000;
  playhead = Math.round(playF0 + elapsed * fps);
  if (playhead >= durF()) {           // loop: restart visuals AND audio
    playhead = 0; playT0 = performance.now(); playF0 = 0;
    if (playing) startAudioFrom(0);
  }
  render();
  if (playing) rafId = requestAnimationFrame(tick);
}

btnPlay.addEventListener('click', async () => {
  playing = !playing;
  btnPlay.textContent = playing ? '[Pause]' : '[Play]';
  if (playing) {
    const ac = getActx();
    if (ac.state === 'suspended') await ac.resume();   // browser autoplay policy
    await preDecodeAll();                              // make sure clips are ready
    playT0 = performance.now(); playF0 = playhead;
    startAudioFrom(playhead);
    tick();
  } else {
    cancelAnimationFrame(rafId);
    stopAllAudio();
  }
});

document.getElementById('btn-clear').addEventListener('click', () => {
  if (!confirm('Clear all segments?')) return;
  segs = []; audio = []; selId = null; updateProps();
  stopAllAudio();
  for (const k in decoded) delete decoded[k];
  peakCache.clear();
  setStatus('Cleared.'); commit();
});

// Delete selected
document.getElementById('btn-del-seg').addEventListener('click', () => {
  if (!selId) return;
  if (selTrack==='audio') {
    if (activeSrcs[selId]) { try { activeSrcs[selId].stop(); } catch(e){} delete activeSrcs[selId]; }
    delete decoded[selId];
    audio = audio.filter(s => s.id!==selId);
  }
  else                    segs  = segs.filter(s  => s.id!==selId);
  selId = null; updateProps(); commit();
});

// ── Properties panel ─────────────────────────────────────────────────────
function updateProps() {
  if (!selId) {
    propTitle.textContent = 'No segment selected — click a segment to edit · Double-click a gap to add text';
    propBody.classList.remove('visible'); return;
  }
  const arr = selTrack==='audio' ? audio : segs;
  const s   = arr.find(x => x.id===selId);
  if (!s) { selId=null; updateProps(); return; }

  propBody.classList.add('visible');
  const isAud = selTrack==='audio';

  propTitle.textContent = isAud
    ? '🎵 Audio clip — ' + (s.fileName||'audio')
    : (s.type==='text' ? '📝 Text segment' : '🖼 Image keyframe');

  propPrompt.style.display = isAud ? 'none' : 'block';
  propPrompt.value = s.prompt || '';

  propStrRow.style.display = (isAud || s.type==='text') ? 'none' : 'flex';
  if (!isAud && s.type!=='text') {
    propStr.value    = s.guideStrength ?? 1;
    propStrVal.textContent = parseFloat(propStr.value).toFixed(2);
  }

  propAudio.style.display = isAud ? 'block' : 'none';
  if (isAud) propAudio.textContent =
    'Length: ' + (s.length/fps).toFixed(2) + 's  ·  Trim start: ' + ((s.trimStart||0)/fps).toFixed(2) + 's';

  // ── Sliding-window boundary warning + fix buttons ─────────────────────
  const warnEl  = document.getElementById('prop-warning');
  const crosses = crossingBoundaries(s);
  if (crosses.length) {
    warnEl.style.display = 'flex';
    const bList = crosses.map(b => 'frame ' + b + ' (' + (b/fps).toFixed(2) + 's)').join(', ');
    document.getElementById('prop-warning-text').textContent =
      '⚠ This asset crosses ' + (crosses.length===1 ? 'a sliding-window boundary' :
      crosses.length + ' sliding-window boundaries') + ' at ' + bList +
      '. It will be generated across separate windows, which can cause visual or audio discontinuity.';
  } else {
    warnEl.style.display = 'none';
  }
}

// ── Boundary fix actions ───────────────────────────────────────────────────
function selSeg() {
  const arr = selTrack==='audio' ? audio : segs;
  return arr.find(x => x.id===selId) || null;
}

// Shorten the segment so it ends exactly at the first crossed boundary.
function fixTrim(s) {
  const crosses = crossingBoundaries(s);
  if (!crosses.length) return;
  s.length = Math.max(MIN_LEN, crosses[0] - s.start);
}

// Shift the segment so it starts at the first crossed boundary
// (i.e. fully inside the next window).
function fixMove(s) {
  const crosses = crossingBoundaries(s);
  if (!crosses.length) return;
  const b = crosses[0];
  s.start = clamp(b, 0, Math.max(0, durF() - s.length));
}

// Split the segment in two at the first crossed boundary. Repeats until
// no boundary is crossed (handles assets spanning several windows).
// Returns the list of newly created segments.
function fixSplit(s, track) {
  const created = [];
  let guard = 0;
  while (guard++ < 50) {
    const crosses = crossingBoundaries(s);
    if (!crosses.length) break;
    const b = crosses[0];
    const tailLen = (s.start + s.length) - b;
    if (tailLen < MIN_LEN || (b - s.start) < MIN_LEN) break;   // too small to split

    const tail = Object.assign({}, s, { id: uid(), start: b, length: tailLen });
    if (track === 'audio') {
      tail.trimStart = (s.trimStart||0) + (b - s.start);
    } else if (s.type === 'image') {
      // Both halves keep the same image reference; imgObj is shared on purpose
      tail.imageB64 = s.imageB64;
      tail.imgObj   = s.imgObj;
    }
    s.length = b - s.start;

    if (track === 'audio') audio.push(tail); else segs.push(tail);
    created.push(tail);
    s = tail;   // continue splitting the tail if it still crosses
  }
  return created;
}

document.getElementById('btn-fix-trim').addEventListener('click', () => {
  const s = selSeg(); if (!s) return;
  fixTrim(s); updateProps(); render(); commit();
  setStatus('Trimmed to window boundary.');
});
document.getElementById('btn-fix-move').addEventListener('click', () => {
  const s = selSeg(); if (!s) return;
  fixMove(s); updateProps(); render(); commit();
  setStatus('Moved into next window.');
});
document.getElementById('btn-fix-split').addEventListener('click', () => {
  const s = selSeg(); if (!s) return;
  const made = fixSplit(s, selTrack);
  updateProps(); render(); commit();
  setStatus(made.length ? 'Split into ' + (made.length+1) + ' part(s) at window boundaries.' : 'Segment too short to split.');
});
document.getElementById('btn-fix-all-split').addEventListener('click', () => {
  const crossing = allCrossingSegs();
  let total = 0;
  for (const {seg, track} of crossing) total += fixSplit(seg, track).length;
  updateProps(); render(); commit();
  setStatus(total ? 'Split ' + crossing.length + ' asset(s) at window boundaries.' : 'Nothing to split.');
});

// Global warning counter (called from render)
function updateWinWarnings() {
  const el = document.getElementById('win-warnings');
  if (!el) return;
  const crossing = showWindows ? allCrossingSegs() : [];
  if (!crossing.length) { el.style.display = 'none'; return; }
  el.style.display = 'block';
  document.getElementById('win-warnings-text').textContent =
    '⚠ ' + crossing.length + ' asset(s) cross sliding-window boundaries — select one for fix options, or:';
}

propPrompt.addEventListener('input', () => {
  const s = segs.find(x => x.id===selId);
  if (s) { s.prompt = propPrompt.value; render(); commit(); }
});

propStr.addEventListener('input', () => {
  const s = segs.find(x => x.id===selId);
  if (s) { s.guideStrength = parseFloat(propStr.value); propStrVal.textContent = s.guideStrength.toFixed(2); commit(); }
});

// ── Zoom bar ─────────────────────────────────────────────────────────────────
const zoomCanvas = document.getElementById('zoom-bar');
const zctx       = zoomCanvas.getContext('2d');
let zbDrag = null;  // dragging the viewport handle: { mode:'viewport'|'left'|'right', startX, startVS, startVE }

function renderZoomBar() {
  const W  = zoomCanvas.parentElement.clientWidth;
  if (W < 1) return;
  zoomCanvas.width  = W;
  zoomCanvas.height = 28;
  const df = durF();

  // Background
  zctx.fillStyle = '#111';
  zctx.fillRect(0, 0, W, 28);

  // Mini segment bars (full timeline in miniature)
  function miniX(f) { return (f / df) * W; }
  segs.forEach(s => {
    zctx.fillStyle = s.type==='text' ? '#3a2e5a' : '#1a4a2a';
    zctx.fillRect(miniX(s.start), 8, Math.max(1, miniX(s.length)), 12);
  });
  audio.forEach(s => {
    zctx.fillStyle = '#142e4e';
    zctx.fillRect(miniX(s.start), 8, Math.max(1, miniX(s.length)), 8);
  });

  // Viewport rect
  const vs = (viewStart / df) * W;
  const ve = (viewEnd   / df) * W;
  const vw = Math.max(4, ve - vs);

  zctx.fillStyle = 'rgba(255,255,255,0.08)';
  zctx.fillRect(vs, 0, vw, 28);
  zctx.strokeStyle = 'rgba(255,255,255,0.35)';
  zctx.lineWidth = 1;
  zctx.strokeRect(vs + 0.5, 0.5, vw - 1, 27);

  // Resize grips on left/right edge
  zctx.fillStyle = 'rgba(255,255,255,0.55)';
  [[vs, 6, 3, 16], [vs + vw - 3, 6, 3, 16]].forEach(([x,y,w,h]) => {
    zctx.fillRect(x, y, w, h);
  });

  // Zoom percentage label
  const pct = Math.round((df / Math.max(1, viewEnd - viewStart)) * 100);
  zctx.fillStyle = '#666';
  zctx.font = '10px monospace';
  zctx.textBaseline = 'middle';
  zctx.textAlign    = 'right';
  zctx.fillText(pct + '%', W - 4, 14);
  zctx.textAlign = 'left';
  zctx.textBaseline = 'alphabetic';

  // Reset zoom hint (when zoomed in)
  if (viewStart > 0 || viewEnd < df - 0.5) {
    zctx.fillStyle = '#555';
    zctx.font = '10px sans-serif';
    zctx.textBaseline = 'middle';
    zctx.fillText('double-click to reset zoom', 6, 14);
    zctx.textBaseline = 'alphabetic';
  }
}

// Zoom bar interactions
zoomCanvas.addEventListener('dblclick', () => {
  viewStart = 0; viewEnd = durF(); render(); renderZoomBar();
});

function zbHitZone(mx) {
  const df = durF();
  const W  = zoomCanvas.width;
  const vs = (viewStart / df) * W;
  const ve = (viewEnd   / df) * W;
  const GRIP = 6;
  if (Math.abs(mx - vs) <= GRIP) return 'left';
  if (Math.abs(mx - ve) <= GRIP) return 'right';
  if (mx >= vs && mx <= ve)      return 'viewport';
  return 'seek';
}

zoomCanvas.addEventListener('mousemove', e => {
  const zone = zbHitZone(e.offsetX);
  zoomCanvas.style.cursor =
    zone==='left'||zone==='right' ? 'ew-resize' :
    zone==='viewport'             ? 'grab'       : 'pointer';
});

zoomCanvas.addEventListener('mousedown', e => {
  e.preventDefault();
  zbDrag = { mode: zbHitZone(e.offsetX), startX: e.offsetX, startVS: viewStart, startVE: viewEnd };
  if (zbDrag.mode === 'seek') {
    // Click outside viewport → jump view to click position
    const df   = durF();
    const span = viewSpan();
    const atF  = (e.offsetX / zoomCanvas.width) * df;
    viewStart  = clamp(atF - span/2, 0, df - span);
    viewEnd    = viewStart + span;
    render(); renderZoomBar();
    zbDrag = null;
  }
});

window.addEventListener('mousemove', e => {
  if (!zbDrag || zbDrag.mode==='seek') return;
  const df  = durF();
  const W   = zoomCanvas.width;
  const dx  = e.clientX - zoomCanvas.getBoundingClientRect().left - zbDrag.startX;
  const dF  = (dx / W) * df;

  if (zbDrag.mode==='viewport') {
    const span = zbDrag.startVE - zbDrag.startVS;
    viewStart = clamp(zbDrag.startVS + dF, 0, df - span);
    viewEnd   = viewStart + span;
  } else if (zbDrag.mode==='left') {
    viewStart = clamp(zbDrag.startVS + dF, 0, viewEnd - MIN_ZOOM_FRAMES);
  } else if (zbDrag.mode==='right') {
    viewEnd   = clamp(zbDrag.startVE + dF, viewStart + MIN_ZOOM_FRAMES, df);
  }
  render(); renderZoomBar();
});

window.addEventListener('mouseup', () => { zbDrag = null; });

// ── Commit: postMessage to Wan2GP parent ──────────────────────────────────
function commit() {
  const sorted = [...segs].sort((a,b) => a.start - b.start);
  const dF = durF();

  // Build local_prompts + segment_lengths
  let cursor=0, pendGap=0;
  const prompts=[], lengths=[];
  for (const s of sorted) {
    if (s.start >= dF) break;
    if (s.start > cursor) {
      const gap = Math.min(s.start, dF) - cursor;
      if (lengths.length) lengths[lengths.length-1] += gap; else pendGap += gap;
    }
    const clen = Math.min(s.start+s.length, dF) - s.start;
    lengths.push(clen + pendGap);
    prompts.push(s.prompt || '');
    pendGap = 0;
    cursor  = s.start + s.length;
  }
  // Pad last to fill duration
  if (lengths.length && Math.min(cursor,dF) < dF) {
    lengths[lengths.length-1] += dF - Math.min(cursor,dF);
  }

  const imgStrengths = sorted.filter(s => s.type!=='text').map(s => (s.guideStrength??1).toFixed(2));

  // Strip imgObj before serialising
  const toSave = {
    fps,
    durationSec: durSec,
    slidingWindowSize:    winSize,
    slidingWindowOverlap: winOverlap,
    showWindows:          showWindows,
    segments:      sorted.map(({imgObj,...r}) => r),
    audioSegments: audio.map(s => ({...s})),
  };

  window.parent.postMessage({
    source:          'wdc_ltx_director',
    timeline_data:    JSON.stringify(toSave),
    local_prompts:    prompts.join(' | '),
    segment_lengths:  lengths.join(','),
    guide_strength:   imgStrengths.join(','),
  }, '*');

  render();
  renderZoomBar();
}

function setStatus(msg) { statusEl.textContent = msg; }

// ── Inbound commands from the parent page ─────────────────────────────────
// The bridge JS sends postMessage({ source:'wdc_parent', cmd:... }) here.
// Without this listener, load/autosave/recover/clear all silently fail.
window.addEventListener('message', function(e) {
  const d = e.data;
  if (!d || d.source !== 'wdc_parent') return;

  if (d.cmd === 'get_state') {
    // Parent wants current state immediately (called before Apply/Preview)
    commit();

  } else if (d.cmd === 'set_window_settings' && d.data) {
    // Sync from the Video Generator's Sliding Window tab.
    const ws0 = parseInt(d.data.slidingWindowSize);
    const ov0 = parseInt(d.data.slidingWindowOverlap);
    if (!isNaN(ws0) && ws0 >= 8) {
      const pair = snapWindowPair(ws0, isNaN(ov0) ? winOverlap : ov0);
      winSize = pair[0]; winOverlap = pair[1];
      document.getElementById('ctrl-win').value = winSize;
      document.getElementById('ctrl-ovl').value = winOverlap;
      render();
      commit();
      setStatus('Window settings synced from generator: ' + winSize + 'f / overlap ' + winOverlap +
                'f (' + newFramesPerWindow() + ' new frames per window).');
    }

  } else if (d.cmd === 'clear') {
    // Parent clear button — wipe internal state and re-render
    segs = []; audio = []; selId = null;
    playhead = 0; playing = false;
    cancelAnimationFrame(rafId);
    stopAllAudio();
    for (const k in decoded) delete decoded[k];
    peakCache.clear();
    btnPlay.textContent = '[Play]';
    updateProps();
    setStatus('Timeline cleared.');
    commit();

  } else if (d.cmd === 'restore' && d.data) {
    // Load / autosave restore.
    // d.data is the FULL session payload:
    //   { fps, duration_sec, global_prompt, epsilon, timeline: { segments, audioSegments } }
    // (The timeline sub-object may also be at the root for backwards compat.)
    try {
      const p = d.data;

      // ── Restore fps and duration from top-level fields ──────────────────
      // Note: the save format uses "duration_sec", not "durationSec"
      const newFps = parseInt(p.fps) || 24;
      const newDur = parseFloat(p.duration_sec || p.durationSec) || 5;
      fps    = newFps;
      durSec = newDur;
      document.getElementById('ctrl-fps').value = fps;
      document.getElementById('ctrl-dur').value = durSec;

      // ── Restore sliding-window settings (may be nested under .timeline) ─
      const winSrc = (p.timeline && p.timeline.slidingWindowSize !== undefined)
                     ? p.timeline : p;
      if (winSrc.slidingWindowSize !== undefined) {
        const pair = snapWindowPair(parseInt(winSrc.slidingWindowSize) || 129,
                                    parseInt(winSrc.slidingWindowOverlap) || 9);
        winSize = pair[0]; winOverlap = pair[1];
        if (winSrc.showWindows !== undefined) showWindows = !!winSrc.showWindows;
        document.getElementById('ctrl-win').value = winSize;
        document.getElementById('ctrl-ovl').value = winOverlap;
        document.getElementById('ctrl-show-win').checked = showWindows;
      }

      // Reset view to show full timeline
      viewStart = 0;
      viewEnd   = durF();

      // ── Find segments — may be nested under .timeline ───────────────────
      const src = (p.timeline && (p.timeline.segments || p.timeline.audioSegments))
                  ? p.timeline
                  : p;

      const rawSegs  = src.segments      || [];
      const rawAudio = src.audioSegments || [];

      // ── Restore audio — decode for waveform display + playback ─────────
      stopAllAudio();
      for (const k in decoded) delete decoded[k];
      peakCache.clear();
      audio = rawAudio.map(function(s) {
        return {
          id:        s.id || uid(),
          type:      'audio',
          start:     parseInt(s.start)     || 0,
          length:    parseInt(s.length)    || Math.round(fps * 3),
          trimStart: parseInt(s.trimStart) || 0,
          audioB64:  s.audioB64  || '',
          fileName:  s.fileName  || 'audio',
        };
      });
      audio.forEach(function(s) { ensureDecoded(s); });

      // ── Restore video segments, waiting for images to load ──────────────
      segs = [];
      let pending = 0;

      rawSegs.forEach(function(s) {
        const seg = {
          id:            s.id || uid(),
          type:          s.type || 'image',
          start:         parseInt(s.start)  || 0,
          length:        parseInt(s.length) || Math.round(fps * 2),
          prompt:        s.prompt           || '',
          guideStrength: parseFloat(s.guideStrength) || 1.0,
        };
        segs.push(seg);

        if (s.type === 'image' && s.imageB64) {
          seg.imageB64 = s.imageB64;
          pending++;
          const img = new Image();
          img.onload = function() {
            seg.imgObj = img;
            pending--;
            if (pending === 0) finalise();
          };
          img.onerror = function() {
            pending--;
            if (pending === 0) finalise();
          };
          img.src = s.imageB64;
        }
      });

      function finalise() {
        selId = null;
        updateProps();
        render();
        renderZoomBar();
        commit();
        setStatus('Restored: ' + segs.length + ' video segment(s), ' + audio.length + ' audio clip(s).');
      }

      // If no images to wait for, finalise immediately
      if (pending === 0) finalise();

    } catch(err) {
      console.error('[LTXDirector] restore error:', err);
      setStatus('Restore error: ' + err.message);
    }
  }
});

// ── Boot ─────────────────────────────────────────────────────────────────
resizeCanvas();
renderZoomBar();
new ResizeObserver(() => { renderZoomBar(); }).observe(document.getElementById('zoom-bar-wrap'));

// Notify parent of our height so iframe can auto-size
function notifyHeight() {
  window.parent.postMessage({ source:'wdc_ltx_director', height: document.body.scrollHeight }, '*');
}
window.addEventListener('load', notifyHeight);
new ResizeObserver(notifyHeight).observe(document.body);

})();
</script>
</body>
</html>
"""
