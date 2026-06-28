"""
LTX Director — model-reactive Advanced settings clone.

This module reproduces WanGP's Video Generator "Advanced" form for the LTX
model families (LTX-Video `ltxv_13B` and LTX-2 `ltx2_19B` / `ltx2_22B` /
`ltx2_22B_edit_anything` / `joyai_echo`, plus finetunes of those).

Because WanGP generates that form dynamically from each model's `model_def`
flags (so 13B and 22B genuinely show different fields), this clone is built
ONCE with the full union of LTX fields across all 8 tabs, and then made
model-reactive: when the selected model changes, resolve_visibility(model_def)
returns the exact set of fields WanGP would show for that model. That keeps the
clone 1:1 per model and resilient to WanGP changing a model's flags.

The visibility rules below mirror wgp.py's generate_media_tab gating expressed
in terms of model_def flags:
    embedded_guidance_row  -> model_def.get("embedded_guidance") or audio_guidance
    guidance_phases        -> model_def.get("guidance_max_phases", 0) >= 2
    negative_prompt_row    -> not model_def.get("no_negative_prompt")
    Steps Skipping tab     -> model_def.get("tea_cache") or model_def.get("mag_cache")
    Quality tab            -> perturbation/cfg_star/cfg_zero/adaptive_projected/
                              motion_amplitude/self_refiner (any)
    Audio tab              -> not image/audio-only (LTX video models: shown)
    Sliding Window tab     -> model_def.get("sliding_window")
    sample_solver row      -> model_def.get("sample_solvers") is not None
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import gradio as gr

log = logging.getLogger(__name__)


# ── Resolution data, cloned verbatim from WanGP's get_resolution_choices /
#    group_thresholds / categorize_resolution so the Category + Resolution
#    Budget dropdowns behave EXACTLY like the Video Generator even if the live
#    wgp module can't be imported. (4K tier included; matches enable_4k.)
_RES_CHOICES_4K = [
    ("3840x2176 (16:9)", "3840x2176"), ("2176x3840 (9:16)", "2176x3840"),
    ("3840x1664 (21:9)", "3840x1664"), ("1664x3840 (9:21)", "1664x3840"),
    ("2560x1440 (16:9)", "2560x1440"), ("1440x2560 (9:16)", "1440x2560"),
    ("1920x1440 (4:3)", "1920x1440"),  ("1440x1920 (3:4)", "1440x1920"),
    ("2160x1440 (3:2)", "2160x1440"),  ("1440x2160 (2:3)", "1440x2160"),
    ("1440x1440 (1:1)", "1440x1440"),  ("2688x1152 (21:9)", "2688x1152"),
    ("1152x2688 (9:21)", "1152x2688"),
]
_RES_CHOICES_BASE = [
    # 1080p
    ("1920x1088 (16:9)", "1920x1088"), ("1088x1920 (9:16)", "1088x1920"),
    ("1920x832 (21:9)", "1920x832"),   ("832x1920 (9:21)", "832x1920"),
    # 720p
    ("1024x1024 (1:1)", "1024x1024"),  ("1280x720 (16:9)", "1280x720"),
    ("720x1280 (9:16)", "720x1280"),   ("1280x544 (21:9)", "1280x544"),
    ("544x1280 (9:21)", "544x1280"),   ("1104x832 (4:3)", "1104x832"),
    ("832x1104 (3:4)", "832x1104"),    ("960x960 (1:1)", "960x960"),
    # 540p
    ("960x544 (16:9)", "960x544"),     ("544x960 (9:16)", "544x960"),
    # 480p
    ("832x624 (4:3)", "832x624"),      ("624x832 (3:4)", "624x832"),
    ("720x720 (1:1)", "720x720"),      ("832x480 (16:9)", "832x480"),
    ("480x832 (9:16)", "480x832"),
    # 384p
    ("672x384 (16:9)", "672x384"),     ("384x672 (9:16)", "384x672"),
    ("512x512 (1:1)", "512x512"),
    # 320p
    ("576x320 (16:9)", "576x320"),     ("320x576 (9:16)", "320x576"),
    ("448x448 (1:1)", "448x448"),
    # 256p
    ("448x256 (7:4)", "448x256"),      ("256x448 (4:7)", "256x448"),
    ("320x320 (1:1)", "320x320"),
]
_GROUP_THRESHOLDS = {
    "256p": 448 * 256,   "320p": 448 * 448,   "384p": 512 * 512,
    "480p": 832 * 624,   "540p": 960 * 544,   "720p": 1024 * 1024,
    "1080p": 1920 * 1088, "1440p": 2560 * 1440, "2160p": 3840 * 2176,
}


def categorize_resolution(resolution_str: str) -> str:
    """Bucket a 'WxH' string into a category by pixel count (clone of wgp)."""
    try:
        w, h = map(int, resolution_str.split("x"))
    except Exception:
        return "720p"
    px = w * h
    for group, thresh in _GROUP_THRESHOLDS.items():
        if px <= thresh:
            return group
    return next(reversed(_GROUP_THRESHOLDS))


def all_resolution_choices(enable_4k: bool = False) -> list:
    """Full (label, value) resolution list, 4K tier optional (clone of wgp)."""
    return (list(_RES_CHOICES_4K) if enable_4k else []) + list(_RES_CHOICES_BASE)


def resolution_groups_and_selection(selected_resolution: str | None = None,
                                    enable_4k: bool = False):
    """Return (groups, group_resolutions, selected_group, selected_value),
    matching how the Video Generator groups resolutions by Category. Groups are
    ordered largest-first (as the Video Generator reverses them)."""
    choices = all_resolution_choices(enable_4k)
    if not selected_resolution or not any(selected_resolution == r for _, r in choices):
        selected_resolution = "832x480"  # sensible LTX default
    grouped: Dict[str, list] = {}
    for label, res in choices:
        grouped.setdefault(categorize_resolution(res), []).append((label, res))
    # group_thresholds order is small→large; the UI shows large→small.
    available = [g for g in _GROUP_THRESHOLDS if g in grouped]
    available.reverse()
    sel_group = categorize_resolution(selected_resolution)
    sel_group_res = grouped.get(sel_group, [])
    return available, sel_group_res, sel_group, selected_resolution


def resolutions_for_group(group: str, enable_4k: bool = False) -> list:
    """The (label, value) resolutions belonging to one Category group."""
    return [(lbl, res) for (lbl, res) in all_resolution_choices(enable_4k)
            if categorize_resolution(res) == group]




# Setting keys this clone manages, grouped by the row/tab they belong to. The
# order here is the canonical order used everywhere (component list, value
# collection, visibility updates).
ADV_FIELD_ORDER: List[str] = [
    # General
    "seed", "guidance_phases", "guidance_scale", "guidance2_scale", "guidance3_scale",
    "switch_threshold", "switch_threshold2", "model_switch_phase",
    "audio_guidance_scale", "embedded_guidance_scale",
    "sample_solver", "flow_shift",
    "negative_prompt",
    "NAG_scale", "NAG_tau", "NAG_alpha",
    "repeat_generation", "multi_prompts_gen_type",
    # Steps Skipping
    "skip_steps_cache_type", "skip_steps_multiplier", "skip_steps_start_step_perc",
    # Post Processing
    "temporal_upsampling", "spatial_upsampling_method", "spatial_upsampling_ratio",
    "film_grain_intensity", "film_grain_saturation",
    # Audio
    "postprocess_audio", "postprocess_audio_prompt", "postprocess_audio_neg_prompt",
    "audio_source", "replace_voice_method", "replace_voice_sample", "replace_voice_sample2",
    # Quality
    "perturbation_switch", "perturbation_layers",
    "perturbation_start_perc", "perturbation_end_perc",
    "apg_switch", "cfg_star_switch", "cfg_zero_step",
    "motion_amplitude", "self_refiner_setting",
    # Sliding Window
    "sliding_window_size", "sliding_window_overlap",
    "sliding_window_overlap_noise", "sliding_window_discard_last_frames",
    "sliding_window_color_correction_strength",
    # Misc
    "RIFLEx_setting", "force_fps", "num_inference_steps", "resolution_group", "resolution", "video_length",
]


def _flag(model_def: dict, key: str, default=False):
    try:
        return model_def.get(key, default)
    except Exception:
        return default


def resolve_visibility(model_def: dict | None) -> Dict[str, bool]:
    """Return {field_key: visible} for the given model_def, mirroring WanGP's
    own gating. Unknown / None model_def → show the conservative LTX-Video set.
    """
    md = model_def or {}
    base = str(md.get("architecture", "") or md.get("model_type", "") or "")

    guidance_max_phases = int(_flag(md, "guidance_max_phases", 0) or 0)
    any_embedded = bool(_flag(md, "embedded_guidance", False))
    any_audio_guid = bool(_flag(md, "audio_guidance", False))
    no_negative = bool(_flag(md, "no_negative_prompt", False))
    any_tea = bool(_flag(md, "tea_cache", False))
    any_mag = bool(_flag(md, "mag_cache", False))
    any_pert = bool(_flag(md, "perturbation", False))
    any_cfg_star = bool(_flag(md, "cfg_star", False))
    any_cfg_zero = bool(_flag(md, "cfg_zero", False))
    any_apg = bool(_flag(md, "adaptive_projected_guidance", False))
    any_motion = bool(_flag(md, "motion_amplitude", False))
    any_refiner = bool(_flag(md, "self_refiner", False))
    has_solvers = _flag(md, "sample_solvers", None) is not None
    sliding = bool(_flag(md, "sliding_window", False))
    # RIFLEx is hidden for ltxv/diffusion-forcing in wgp.py
    riflex_hidden_families = ("ltxv", "ltx2")
    riflex_visible = not any(base.startswith(p) for p in riflex_hidden_families)
    # NAG column visibility comes from model_def too
    any_nag = bool(_flag(md, "NAG", False)) or bool(_flag(md, "nag", False))

    quality_any = any([any_pert, any_cfg_star, any_cfg_zero, any_apg,
                       any_motion, any_refiner])

    v: Dict[str, bool] = {k: True for k in ADV_FIELD_ORDER}

    # General
    v["guidance_phases"]   = guidance_max_phases >= 2
    v["guidance2_scale"]   = guidance_max_phases >= 2
    v["guidance3_scale"]   = guidance_max_phases >= 3
    v["switch_threshold"]  = guidance_max_phases >= 2
    v["switch_threshold2"] = guidance_max_phases >= 3
    v["model_switch_phase"] = guidance_max_phases >= 3 and bool(_flag(md, "multiple_submodels", False))
    v["audio_guidance_scale"]    = any_audio_guid
    v["embedded_guidance_scale"] = any_embedded
    v["sample_solver"]     = has_solvers
    v["negative_prompt"]   = not no_negative
    v["NAG_scale"] = v["NAG_tau"] = v["NAG_alpha"] = any_nag

    # Steps Skipping (whole tab)
    steps_skip = any_tea or any_mag
    for k in ("skip_steps_cache_type", "skip_steps_multiplier", "skip_steps_start_step_perc"):
        v[k] = steps_skip

    # Quality (whole tab + per-feature)
    v["perturbation_switch"] = any_pert
    v["perturbation_layers"] = any_pert
    v["perturbation_start_perc"] = any_pert
    v["perturbation_end_perc"] = any_pert
    v["apg_switch"] = any_apg
    v["cfg_star_switch"] = any_cfg_star
    v["cfg_zero_step"] = any_cfg_zero
    v["motion_amplitude"] = any_motion
    v["self_refiner_setting"] = any_refiner

    # Sliding Window
    for k in ("sliding_window_size", "sliding_window_overlap",
              "sliding_window_overlap_noise", "sliding_window_discard_last_frames",
              "sliding_window_color_correction_strength"):
        v[k] = sliding
    # color-correction + overlap-noise are hidden for ltxv specifically in wgp.py
    if base.startswith("ltxv"):
        v["sliding_window_color_correction_strength"] = False
        v["sliding_window_overlap_noise"] = False

    # Misc
    v["RIFLEx_setting"] = riflex_visible

    return v


def tab_visibility(vis: Dict[str, bool]) -> Dict[str, bool]:
    """Roll field visibility up to whole-tab visibility (a tab is shown if any
    of its fields are visible)."""
    groups = {
        "general":  ["seed", "guidance_scale", "flow_shift", "repeat_generation",
                     "multi_prompts_gen_type", "sample_solver", "negative_prompt"],
        "loras":    ["__loras__"],  # always shown
        "steps":    ["skip_steps_cache_type"],
        "post":     ["temporal_upsampling", "spatial_upsampling_method"],
        "audio":    ["postprocess_audio"],
        "quality":  ["perturbation_switch", "apg_switch", "cfg_star_switch",
                     "cfg_zero_step", "motion_amplitude", "self_refiner_setting"],
        "sliding":  ["sliding_window_size"],
        "misc":     ["force_fps", "RIFLEx_setting", "num_inference_steps", "resolution"],
    }
    out = {}
    for tab, keys in groups.items():
        if "__loras__" in keys:
            out[tab] = True
        else:
            out[tab] = any(vis.get(k, False) for k in keys)
    return out


def _fmt(v) -> str:
    """Format a slider value for the multipliers string (trim trailing zeros)."""
    try:
        f = float(v)
    except Exception:
        return "1"
    if f == int(f):
        return str(int(f))
    return ("%.2f" % f).rstrip("0").rstrip(".")


def _parse_multipliers_text(text: str, n_loras: int, n_phases: int) -> list:
    """Parse an existing multipliers string back into a [n_loras][n_phases]
    grid of floats so toggling the sliders preserves prior values. Matches
    WanGP's preparse: LoRAs are separated by spaces OR newlines, phases within
    a LoRA by ';'. Missing entries default to 1.0."""
    grid = [[1.0] * n_phases for _ in range(n_loras)]
    if not text:
        return grid
    # Collapse newlines to spaces (drop comment lines), then split on whitespace.
    raw_lines = [ln.strip() for ln in str(text).replace("\r", "").split("\n")]
    raw_lines = [ln for ln in raw_lines if ln and not ln.startswith("#")]
    tokens = " ".join(raw_lines).replace("|", " ").split()
    for i in range(min(n_loras, len(tokens))):
        parts = tokens[i].split(";")
        for p in range(n_phases):
            try:
                if len(parts) == 1:
                    grid[i][p] = float(parts[0])
                elif p < len(parts):
                    grid[i][p] = float(parts[p])
                else:
                    grid[i][p] = float(parts[-1])
            except Exception:
                grid[i][p] = 1.0
    return grid


def layout_lora_sliders(selected, phases, show, current_mult,
                        max_rows: int, max_phases: int):
    """Compute Gradio updates for the fixed slider pool. Returns a flat list:
      [col_update, row_update*max_rows, label_update*max_rows,
       slider_update*(max_rows*max_phases)]."""
    import gradio as gr
    selected = list(selected or [])
    try:
        nphases = max(1, min(max_phases, int(phases or 1)))
    except Exception:
        nphases = 1
    show = bool(show)
    n = min(len(selected), max_rows)
    seeded = _parse_multipliers_text(current_mult, n, nphases) if n else []

    col_u = gr.update(visible=show and n > 0)
    row_us, lbl_us, sld_us = [], [], []
    for r in range(max_rows):
        active_row = show and r < n
        row_us.append(gr.update(visible=active_row))
        lbl_us.append(gr.update(value=(f"**{selected[r]}**" if active_row else "")))
        for p in range(max_phases):
            if active_row and p < nphases:
                val = seeded[r][p] if r < len(seeded) else 1.0
                sld_us.append(gr.update(
                    value=val, visible=True,
                    label=(f"Phase {p+1}" if nphases > 1 else "Strength")))
            else:
                sld_us.append(gr.update(visible=False))
    return [col_u, *row_us, *lbl_us, *sld_us]


def collect_lora_multipliers(selected, phases, max_phases: int, *slider_vals):
    """Build the WanGP multipliers string from the fixed slider pool. Output:
    LoRAs space-separated, phases ';'-separated, e.g. "1;1 1;1"."""
    selected = list(selected or [])
    try:
        nphases = max(1, min(max_phases, int(phases or 1)))
    except Exception:
        nphases = 1
    groups = []
    for r in range(len(selected)):
        base = r * max_phases
        phase_vals = [slider_vals[base + p] for p in range(nphases)]
        if nphases > 1:
            groups.append(";".join(_fmt(v) for v in phase_vals))
        else:
            groups.append(_fmt(phase_vals[0]))
    return " ".join(groups)


def build_advanced_ui(show_lora_sliders: bool = True,
                      initial_loras: list | None = None,
                      initial_spatial_methods: list | None = None,
                      initial_spatial_ratios: list | None = None,
                      initial_window_size=None,
                      initial_window_overlap=None,
                      initial_window_discard=None,
                      external_resolution=None,
                      external_resolution_group=None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Build the 8-tab Advanced clone. Returns (components, tabs) where
    components maps field_key -> gradio component (in ADV_FIELD_ORDER) plus a
    few non-settings keys (loras_choices, loras_multipliers,
    lora_show_sliders, lora_sliders_state), and tabs maps tab_key -> gr.Tab
    handle (for show/hide).

    show_lora_sliders sets the initial state of the "Show strength sliders"
    checkbox in the LoRAs tab (persisted by the caller).
    """
    c: Dict[str, Any] = {}
    tabs: Dict[str, Any] = {}

    with gr.Tabs(elem_id="wdc-adv-tabs"):
        # ── General ────────────────────────────────────────────────────────
        with gr.Tab("General", elem_id="wdc-adv-tab-general") as t_general:
            tabs["general"] = t_general
            with gr.Row():
                c["seed"] = gr.Slider(-1, 999999999, value=-1, step=1,
                                      label="Seed (-1 for random)", scale=2)
                # LTX-2 distilled exposes guidance_max_phases=2 / visible_phases=0,
                # so WanGP shows this as a "Phases" dropdown with One/Two options
                # (default 2). It is NOT hidden for these models.
                c["guidance_phases"] = gr.Dropdown(
                    choices=[("One Phase", 1), ("Two Phases", 2)],
                    value=2, label="Phases", visible=True, allow_custom_value=True)
            with gr.Row():
                c["model_switch_phase"] = gr.Dropdown(
                    choices=[("Phase 1-2 transition", 1), ("Phase 2-3 transition", 2)],
                    value=1, label="Model Switch", visible=False, allow_custom_value=True)
                c["switch_threshold"] = gr.Slider(0, 1000, value=0, step=1,
                    label="Switch Threshold", visible=False)
                c["switch_threshold2"] = gr.Slider(0, 1000, value=0, step=1,
                    label="Switch Threshold 2", visible=False)
            with gr.Row():
                c["guidance_scale"] = gr.Slider(1.0, 20.0, value=3.0, step=0.1,
                    label="Guidance Scale (CFG)")
                c["guidance2_scale"] = gr.Slider(1.0, 20.0, value=3.0, step=0.1,
                    label="Guidance Scale (Phase 2)", visible=False)
                c["guidance3_scale"] = gr.Slider(1.0, 20.0, value=3.0, step=0.1,
                    label="Guidance Scale (Phase 3)", visible=False)
            with gr.Row():
                c["audio_guidance_scale"] = gr.Slider(1.0, 20.0, value=1.0, step=0.1,
                    label="Audio Guidance Scale", visible=False)
                c["embedded_guidance_scale"] = gr.Slider(1.0, 20.0, value=6.0, step=0.1,
                    label="Embedded Guidance Scale", visible=False)
            with gr.Row():
                c["sample_solver"] = gr.Dropdown(
                    choices=[("Default", "")], value="",
                    label="Sampler Solver / Scheduler", visible=False, allow_custom_value=True)
                c["flow_shift"] = gr.Slider(0.0, 25.0, value=5.0, step=0.1,
                    label="Flow Shift (Shift Scale)")
            c["negative_prompt"] = gr.Textbox(label="Negative Prompt", value="",
                                              lines=2, visible=False)
            with gr.Row():
                c["NAG_scale"] = gr.Slider(1.0, 20.0, value=1.0, step=0.1,
                    label="NAG Scale", visible=False)
                c["NAG_tau"] = gr.Slider(0.0, 10.0, value=3.5, step=0.1,
                    label="NAG Tau", visible=False)
                c["NAG_alpha"] = gr.Slider(0.0, 10.0, value=0.5, step=0.1,
                    label="NAG Alpha", visible=False)
            with gr.Row():
                c["repeat_generation"] = gr.Slider(1, 25, value=1, step=1,
                    label="Num. of Generated Videos per Prompt")
                c["multi_prompts_gen_type"] = gr.Dropdown(
                    choices=[
                        ("Auto — set by the timeline (single prompt vs. sliding windows)", "AUTO"),
                        ("All the Lines are Part of the Same Prompt", "FG"),
                        ("Each Paragraph (blank-line separated) → new Sliding Window", "PW"),
                    ],
                    value="AUTO",
                    label="How to Process each Line of the Text Prompt (managed by the timeline)",
                    allow_custom_value=True)

        # ── LoRAs ──────────────────────────────────────────────────────────
        with gr.Tab("LoRAs", elem_id="wdc-adv-tab-loras") as t_loras:
            tabs["loras"] = t_loras
            gr.Markdown("<B>LoRAs create special effects when you mention a "
                        "trigger word in the Prompt. Pick as many as you like; "
                        "the list comes from the selected model's LoRA folder.</B>")

            # Prefer WanGP's native folder-grouped HierarchySelector (same widget
            # the Video Generator uses) so LoRAs are organised by sub-folder.
            # Fall back to a flat multiselect dropdown if it can't be imported.
            _hier_ok = False
            try:
                from shared.gradio.hierarchy_selector import (
                    HierarchySelector as _HS, build_choices_hierarchy as _bch)
                _hierarchy = _bch(list(initial_loras or []))
                c["loras_choices"] = _HS(
                    hierarchy=_hierarchy, value=[], height=0,
                    label="Activated LoRAs", search_empty_label="No matching LoRAs",
                    elem_id="wdc-adv-loras")
                c["_loras_is_hierarchy"] = True
                _hier_ok = True
            except Exception as exc:
                log.info("HierarchySelector unavailable, using flat dropdown: %s", exc)
            if not _hier_ok:
                c["loras_choices"] = gr.Dropdown(
                    choices=list(initial_loras or []), value=[],
                    multiselect=True, filterable=True,
                    label="Activated LoRAs", elem_id="wdc-adv-loras-flat",
                    info="Empty means no LoRA files were found in the model's folder.")
                c["_loras_is_hierarchy"] = False

            c["lora_show_sliders"] = gr.Checkbox(
                value=bool(show_lora_sliders),
                label="Show strength sliders for each LoRA",
                elem_id="wdc-adv-lora-show-sliders",
                info="One slider per guidance phase per LoRA. Remembered between sessions.")

            # The multipliers text box. Stays visible and editable; the strength
            # sliders below write into it (space-separated LoRAs, ';' phases).
            c["loras_multipliers"] = gr.Textbox(
                label="LoRAs Multipliers (1.0 by default). LoRAs separated by "
                      "spaces, phases within a LoRA by ';' , e.g. 1;1 1;1 . "
                      "Lines starting with # are ignored.",
                value="", lines=2, elem_id="wdc-adv-lora-mult")

            # Fixed pool of strength-slider rows (NO @gr.render — dynamic event
            # creation breaks the WanGP plugin queue with KeyError). We build
            # MAX_LORA_ROWS rows of MAX_PHASES sliders up front, all hidden, and
            # a handler in the plugin shows/relabels exactly the ones needed for
            # the current selection + guidance-phase count.
            MAX_LORA_ROWS = 12
            MAX_PHASES = 3
            c["_lora_slider_rows"] = []
            c["_lora_slider_labels"] = []
            c["_lora_sliders"] = []
            c["_lora_slider_grid"] = []
            c["_lora_max_rows"] = MAX_LORA_ROWS
            c["_lora_max_phases"] = MAX_PHASES
            with gr.Column(elem_id="wdc-adv-lora-sliders",
                           visible=bool(show_lora_sliders)) as lora_sliders_col:
                c["_lora_sliders_col"] = lora_sliders_col
                for r in range(MAX_LORA_ROWS):
                    with gr.Row(visible=False) as row:
                        lbl = gr.Markdown("", elem_id=f"wdc-lora-lbl-{r}")
                        row_sliders = []
                        for p in range(MAX_PHASES):
                            s = gr.Slider(
                                0.0, 2.0, value=1.0, step=0.05,
                                label=f"Phase {p+1}", visible=False,
                                scale=1, show_reset_button=False,
                                elem_id=f"wdc-lora-s-{r}-{p}")
                            row_sliders.append(s)
                            c["_lora_sliders"].append(s)
                    c["_lora_slider_rows"].append(row)
                    c["_lora_slider_labels"].append(lbl)
                    c["_lora_slider_grid"].append(row_sliders)


        # ── Steps Skipping ─────────────────────────────────────────────────
        with gr.Tab("Steps Skipping", elem_id="wdc-adv-tab-steps", visible=False) as t_steps:
            tabs["steps"] = t_steps
            gr.Markdown("<B>Tea Cache / Mag Cache accelerate generation by "
                        "skipping steps; more skipped = lower quality.</B>")
            c["skip_steps_cache_type"] = gr.Dropdown(
                choices=[("None", ""), ("Tea Cache", "tea"), ("Mag Cache", "mag")],
                value="", label="Skip Steps Cache Type", allow_custom_value=True)
            c["skip_steps_multiplier"] = gr.Dropdown(
                choices=[("around x1.5 speed up", 1.5), ("around x1.75 speed up", 1.75),
                         ("around x2 speed up", 2.0), ("around x2.25 speed up", 2.25),
                         ("around x2.5 speed up", 2.5)],
                value=1.75, label="Skip Steps Cache Global Acceleration", allow_custom_value=True)
            c["skip_steps_start_step_perc"] = gr.Slider(0, 100, value=0, step=1,
                label="Skip Steps starting moment in % of generation")

        # ── Post Processing ────────────────────────────────────────────────
        with gr.Tab("Post Processing", elem_id="wdc-adv-tab-post") as t_post:
            tabs["post"] = t_post
            gr.Markdown("<B>Upsampling - postprocessing that may improve "
                        "fluidity and the size of the output.</B>")
            c["temporal_upsampling"] = gr.Dropdown(
                choices=[("Disabled", ""), ("Rife x2 frames/s", "rife2"),
                         ("Rife x4 frames/s", "rife4")],
                value="", label="Temporal Upsampling", allow_custom_value=True)
            with gr.Row():
                c["spatial_upsampling_method"] = gr.Dropdown(
                    choices=(initial_spatial_methods or
                             [("None", ""), ("Lanczos", "lanczos"),
                              ("FlashVSR", "flashvsr"),
                              ("FlashVSR Two Pass", "flashvsr2pass"),
                              ("VAE Upscaling", "vae")]),
                    value="", scale=3, allow_custom_value=True,
                    label="Spatial Upsampling")
                c["spatial_upsampling_ratio"] = gr.Dropdown(
                    choices=(initial_spatial_ratios or
                             [("x1.0", 1.0), ("x1.5", 1.5), ("x2.0", 2.0),
                              ("x2.5", 2.5), ("x3.0", 3.0), ("x3.5", 3.5),
                              ("x4.0", 4.0)]),
                    value=2.0, scale=1, allow_custom_value=True,
                    label="Scale", visible=False)
            with gr.Row():
                c["film_grain_intensity"] = gr.Slider(0, 1, value=0, step=0.01,
                    label="Film Grain Intensity (0 = disabled)")
                c["film_grain_saturation"] = gr.Slider(0.0, 1, value=0.5, step=0.01,
                    label="Film Grain Saturation")

        # ── Audio ──────────────────────────────────────────────────────────
        with gr.Tab("Audio", elem_id="wdc-adv-tab-audio") as t_audio:
            tabs["audio"] = t_audio
            _audio_native = False
            try:
                # Build the EXACT audio UI WanGP uses on its Video Gen tab, so
                # this section looks and behaves identically (all conditional
                # columns: MMAudio prompts, custom soundtrack, control reuse,
                # voice replacement + samples). We pass simple shims for the
                # ui_get / ui_defaults helpers it expects.
                from postprocessing import audio_processors as _apa
                _ui_defaults = {}
                def _ui_get(key, default=None):
                    return _ui_defaults.get(key, default)
                _aui = _apa.create_generation_audio_ui(
                    gr, _ui_get, _ui_defaults,
                    any_control_video=True, update_form=False)
                # Map WanGP's components into our field dict (real field names).
                c["postprocess_audio"]          = _aui["postprocess_audio"]
                c["postprocess_audio_prompt"]   = _aui["postprocess_audio_prompt"]
                c["postprocess_audio_neg_prompt"] = _aui["postprocess_audio_neg_prompt"]
                c["audio_source"]               = _aui["audio_source"]
                c["replace_voice_method"]       = _aui["replace_voice_method"]
                c["replace_voice_sample"]       = _aui["replace_voice_sample"]
                c["replace_voice_sample2"]      = _aui["replace_voice_sample2"]
                # WanGP wires its own show/hide handlers internally, so we don't
                # need to. Stash nothing for the plugin to manage.
                c["_audio_native"] = True
                _audio_native = True
            except Exception as _aex:
                # Fallback: hand-built simplified audio UI (older WanGP without
                # the audio_processors API).
                c["postprocess_audio"] = gr.Dropdown(
                    choices=[("None", ""),
                             ("Custom Soundtrack", "custom"),
                             ("MMAudio (generate Audio Based on Video Content)", "mmaudio"),
                             ("Control Video Audio Track (Reuse Control Video Audio Track)", "control")],
                    value="", scale=1, allow_custom_value=True,
                    label="Postprocess Remux Audio")
                with gr.Column(visible=False) as _mmaudio_col:
                    with gr.Row():
                        c["postprocess_audio_prompt"] = gr.Textbox(value="", label="Prompt (1 or 2 keywords)")
                        c["postprocess_audio_neg_prompt"] = gr.Textbox(value="", label="Negative Prompt (1 or 2 keywords)")
                with gr.Column(visible=False) as _control_col:
                    gr.Markdown("<B>Reuse the Control Video audio track</B>")
                with gr.Column(visible=False) as _custom_col:
                    c["audio_source"] = gr.Audio(value=None, type="filepath",
                        label="Soundtrack", show_download_button=True)
                c["_audio_cols"] = {"mmaudio": _mmaudio_col,
                                    "control": _control_col, "custom": _custom_col}

        # ── Quality ────────────────────────────────────────────────────────
        with gr.Tab("Quality", elem_id="wdc-adv-tab-quality", visible=False) as t_quality:
            tabs["quality"] = t_quality
            gr.Markdown("<B>Perturbation (improves video quality, requires guidance > 1)</B>")
            with gr.Row():
                c["perturbation_switch"] = gr.Dropdown(
                    choices=[("OFF", 0), ("Skip Layer Guidance", 1)], value=0,
                    label="Perturbation", visible=False, allow_custom_value=True)
                c["perturbation_layers"] = gr.Dropdown(
                    choices=[(str(i), i) for i in range(48)], value=[], multiselect=True,
                    label="Perturbation Layers", visible=False, allow_custom_value=True)
            with gr.Row():
                c["perturbation_start_perc"] = gr.Slider(0, 100, value=0, step=1,
                    label="Denoising Steps % start", visible=False)
                c["perturbation_end_perc"] = gr.Slider(0, 100, value=100, step=1,
                    label="Denoising Steps % end", visible=False)
            c["apg_switch"] = gr.Dropdown(
                choices=[("OFF", 0), ("ON", 1)], value=0,
                label="Adaptive Projected Guidance (requires Guidance > 1)", visible=False, allow_custom_value=True)
            c["cfg_star_switch"] = gr.Dropdown(
                choices=[("OFF", 0), ("ON", 1)], value=0,
                label="Classifier-Free Guidance Star (requires Guidance > 1)", visible=False, allow_custom_value=True)
            c["cfg_zero_step"] = gr.Slider(-1, 39, value=-1, step=1,
                label="CFG Zero below this Layer (Extra Process)", visible=False)
            c["motion_amplitude"] = gr.Slider(1.0, 2.0, value=1.0, step=0.01,
                label="Motion Amplitude (1 = disabled, 1.15 recommended)", visible=False)
            c["self_refiner_setting"] = gr.Dropdown(
                choices=[("Disabled", 0), ("Enabled with P1-Norm", 1),
                         ("Enabled with P2-Norm", 2)], value=0,
                label="Self Refiner (PnP)", visible=False, allow_custom_value=True)

        # ── Sliding Window ─────────────────────────────────────────────────
        with gr.Tab("Sliding Window", elem_id="wdc-adv-tab-sliding") as t_sliding:
            tabs["sliding"] = t_sliding
            gr.Markdown("<B>A Sliding Window lets you generate video with a "
                        "duration not limited by the Model. It turns on "
                        "automatically when frames > Window Size.</B>")
            with gr.Row():
                _ws_default = int(initial_window_size) if initial_window_size else 481
                _ov_default = int(initial_window_overlap) if initial_window_overlap else 17
                _disc_default = int(initial_window_discard) if initial_window_discard else 0
                c["sliding_window_size"] = gr.Slider(41, 737, value=_ws_default, step=8,
                    label="Sliding Window Size (frames)")
                c["sliding_window_overlap"] = gr.Slider(1, 97, value=_ov_default, step=8,
                    label="Window Frames Overlap")
            with gr.Row():
                c["sliding_window_discard_last_frames"] = gr.Slider(0, 40, value=_disc_default, step=8,
                    label="Discard Last Frames of Window")
                c["sliding_window_overlap_noise"] = gr.Slider(0, 100, value=20, step=1,
                    label="Overlap Noise", visible=False)
            c["sliding_window_color_correction_strength"] = gr.Slider(0, 1, value=0, step=0.01,
                label="Color Correction Strength", visible=False)

        # ── Misc. ──────────────────────────────────────────────────────────
        with gr.Tab("Misc.", elem_id="wdc-adv-tab-misc") as t_misc:
            tabs["misc"] = t_misc
            c["RIFLEx_setting"] = gr.Dropdown(
                choices=[("Auto (ON if Video longer than 5s)", 0),
                         ("Always ON", 1), ("Always OFF", 2)], value=0,
                label="RIFLEx positional embedding for long video", visible=False, allow_custom_value=True)
            c["force_fps"] = gr.Dropdown(
                choices=[("Model Default", ""), ("15", "15"), ("16", "16"),
                         ("23", "23"), ("24", "24"), ("25", "25"),
                         ("30", "30"), ("48", "48"), ("50", "50")],
                value="", label="Force Output FPS", allow_custom_value=True)
            with gr.Row():
                c["num_inference_steps"] = gr.Slider(1, 100, value=30, step=1,
                    label="Inference Steps")
                c["video_length"] = gr.Slider(17, 1800, value=97, step=8,
                    label="Video Length (frames)")
            # Resolution lives next to the model selector (built by the plugin
            # and passed in). Reference those components here so the sync still
            # targets them; only build a local fallback if none were provided.
            if external_resolution is not None:
                c["resolution"] = external_resolution
                if external_resolution_group is not None:
                    c["resolution_group"] = external_resolution_group
            else:
                with gr.Row():
                    c["resolution_group"] = gr.Dropdown(
                        choices=[], value=None, scale=2,
                        label="Category", allow_custom_value=True,
                        elem_id="wdc-adv-res-group")
                    c["resolution"] = gr.Dropdown(
                        choices=["832x480", "1280x720", "1024x576", "768x512", "512x512",
                                 "720x1280", "480x832"],
                        value="832x480", allow_custom_value=True, scale=5,
                        label="Resolution Budget (Pixels will be reallocated to preserve Inputs W/H ratio)",
                        elem_id="wdc-adv-resolution")

    # ── Hover/inline help for every field ──────────────────────────────────
    # Gradio renders a component's `info` as helper text under its label and in
    # the hover title, so this gives users an explanation of each control.
    for _key, _help in ADV_FIELD_HELP.items():
        _comp = c.get(_key)
        if _comp is not None:
            try:
                _comp.info = _help
            except Exception:
                pass

    return c, tabs


# Plain-language help for each Advanced field (shown as inline/hover help).
ADV_FIELD_HELP: Dict[str, str] = {
    "seed": "Starting random seed. Use -1 for a new random result each time; set a fixed number to reproduce the same video.",
    "guidance_phases": "How many guidance phases the sampler runs. More phases can refine motion but cost time. Most LTX models use 2.",
    "guidance_scale": "Classifier-Free Guidance (CFG). Higher = follows the prompt more strictly; lower = more creative/loose. Typical 3-7.",
    "guidance2_scale": "CFG strength used during the second guidance phase.",
    "guidance3_scale": "CFG strength used during the third guidance phase.",
    "switch_threshold": "Denoising step at which the model switches to phase 2 (advanced phase tuning).",
    "switch_threshold2": "Denoising step at which the model switches to phase 3.",
    "model_switch_phase": "Which phase transition the model switch happens at.",
    "audio_guidance_scale": "How strongly generated audio follows the audio prompt/reference. Higher = closer to the reference.",
    "embedded_guidance_scale": "Guidance baked into distilled models. Leave at the model's default unless you know you need to change it.",
    "sample_solver": "The sampler/scheduler algorithm. 'Default' uses the model's recommended solver.",
    "flow_shift": "Flow shift (shift scale). Affects motion/sharpness trade-off; higher can sharpen but may add artifacts. Default ~5.",
    "negative_prompt": "Describe what you DON'T want to see. Leave blank if the model doesn't support it.",
    "NAG_scale": "Normalized Attention Guidance strength - an alternative way to steer toward the prompt.",
    "NAG_tau": "NAG tau parameter (controls how NAG is applied).",
    "NAG_alpha": "NAG alpha parameter (controls how NAG is applied).",
    "repeat_generation": "How many videos to generate from this prompt in one run.",
    "multi_prompts_gen_type": "How each line of the prompt is used: as one prompt, or each blank-line paragraph as its own sliding window. The timeline sets this automatically.",
    "skip_steps_cache_type": "Step-skipping cache (TeaCache / MagCache) to speed up generation by reusing computation. Off = highest quality.",
    "skip_steps_multiplier": "How aggressively steps are skipped. Higher = faster but lower quality.",
    "skip_steps_start_step_perc": "Don't start skipping until this percentage of steps have run, protecting early structure.",
    "temporal_upsampling": "Smooths/interpolates frames after generation for a higher effective frame rate.",
    "spatial_upsampling_method": "Method used to upscale the video's resolution after generation.",
    "spatial_upsampling_ratio": "How much to enlarge the video spatially.",
    "film_grain_intensity": "Adds film grain. 0 = none; higher = more grain for a filmic look.",
    "film_grain_saturation": "Color saturation of the added film grain.",
    "postprocess_audio": "Run audio post-processing (e.g. MMAudio) after the video is generated.",
    "postprocess_audio_prompt": "Text describing the sound/ambience to generate for the video.",
    "postprocess_audio_neg_prompt": "Sounds to avoid in the generated audio.",
    "replace_voice_method": "Replace spoken voice in the video using SeedVC (one or two speakers).",
    "audio_source": "Custom soundtrack file to remux onto the generated video.",
    "perturbation_switch": "Enables perturbed-attention guidance, which can improve detail and coherence.",
    "perturbation_layers": "Which model layers the perturbation is applied to.",
    "perturbation_start_perc": "Percentage of steps after which perturbation begins.",
    "perturbation_end_perc": "Percentage of steps after which perturbation stops.",
    "apg_switch": "Adaptive Projected Guidance - adjusts guidance dynamically for better quality.",
    "cfg_star_switch": "CFG-Star: a refined guidance method that can reduce artifacts.",
    "cfg_zero_step": "Step at which CFG-Zero begins (advanced guidance tuning).",
    "motion_amplitude": "How much motion to encourage. Higher = more movement; lower = calmer, steadier shots.",
    "self_refiner_setting": "Optional self-refinement pass for extra detail at the cost of speed.",
    "sliding_window_size": "Frames per sliding window for long videos. LTX needs 8xn+1 values; the timeline manages this for you.",
    "sliding_window_overlap": "Frames each window shares with the previous one to keep motion continuous. New frames per window = size - overlap.",
    "sliding_window_overlap_noise": "How much noise is added in the overlap region to blend windows.",
    "sliding_window_discard_last_frames": "Drop this many frames from the end of each window (can hide end-of-window artifacts).",
    "sliding_window_color_correction_strength": "Corrects color drift between windows. Higher = stronger matching.",
    "RIFLEx_setting": "RIFLEx positional handling for long videos - helps consistency across many frames.",
    "force_fps": "Force the output frame rate. The timeline sets this from your FPS control.",
    "num_inference_steps": "Denoising steps. More = higher quality but slower; distilled LTX models need very few (e.g. 8).",
    "resolution": "Pixel budget for the output. Pixels are reallocated to preserve your input's aspect ratio.",
    "video_length": "Total number of frames to generate. The timeline sets this from FPS x Duration.",
    "loras_choices": "Select LoRA add-ons to apply their style/subject to the generation.",
    "loras_multipliers": "Strength of each selected LoRA. Higher = stronger effect.",
    "lora_show_sliders": "Show per-LoRA strength sliders instead of typing multipliers as text.",
}
