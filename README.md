<!--
  HOW TO USE THIS FILE
  - Replace every [SCREENSHOT: ...] line with your own image, e.g.
        ![Timeline overview](images/timeline.png)
  - Delete any section you don't want.
  - Everything here is plain Markdown, so it works on GitHub, most forums, and Reddit.
-->

# LTX Director

**A timeline-based storyboard editor for LTX video generation in Wan2GP (WanGP).**

Place image keyframes, text prompts, and audio on a visual timeline, then send the
whole thing to WanGP to generate one continuous video. Think of it as a lightweight
"director's timeline" that sits on top of WanGP's generator.

> Version: **1.3.23** · Author: **The-ShadowWalker**


<img width="1917" height="895" alt="Screenshot 2026-06-28 142725" src="https://github.com/user-attachments/assets/cf16d430-4815-4bcb-9d01-e5ea51de0c74" />


---

## What it does

- **Visual timeline.** Drop image keyframes, text prompts, and audio clips onto a
  scrollable timeline and arrange them in time.
- **Keyframe injection.** Images are placed at exact frame positions and injected into
  the generation, so your video hits the shots you set when you set them.
- **Audio track.** Add one or more audio clips; they're mixed into a single soundtrack
  with gaps preserved, and lined up to the timeline.
- **Sliding-window aware.** The timeline shows WanGP's sliding-window layout so you can
  see where window boundaries fall and avoid placing keyframes badly.
- **Long-timeline support.** An optional override lets you generate past WanGP's default
  injected-frame cap (see *Going past the frame cap* below).
- **Mirrors WanGP's settings.** An Advanced panel reproduces WanGP's generation
  settings (model, resolution, sliding window, LoRAs, post-processing, audio, etc.) so
  you don't have to leave the plugin.

---

## Requirements

- A working **Wan2GP (WanGP)** install with an **LTX-2** model downloaded.
- That's it — the plugin uses the dependencies WanGP already provides (nothing extra to
  install). A `requirements.txt` is included for reference only.

---


---

## Quick start

1. Open the **LTX Director** tab.
2. Set your video length (duration) and fps at the top.
3. **Double-click** an empty spot on the timeline to add a text prompt, or use the add
   buttons to drop an image keyframe or audio clip.
4. Drag clips to position them; drag their edges to resize.
5. Open **Advanced** and confirm your model, resolution, and sliding-window settings.
6. Click **Generate** and let WanGP render the timeline.


---

## The timeline toolbar

The toolbar above the timeline holds the per-timeline controls:

| Control | What it does |
|---|---|
| **fps / duration** | Frame rate and total length of the video. |
| **bands** | Show/hide the sliding-window bands and boundary markers. |
| **snap** | Snap clip edges to other clips, the playhead, and window boundaries while dragging. Hold **Alt** to bypass. |
| **past cap** | Allow timelines longer than WanGP's injected-frame cap (asks for confirmation — see below). |
| **Play** | Preview the timeline with the playhead and audio. |
| **Clear** | Remove everything from the timeline (click twice to confirm). |

[SCREENSHOT: close-up of the toolbar showing the bands / snap / past cap checkboxes]

---

## Keyboard shortcuts

| Key | Action |
|---|---|
| **Ctrl/Cmd + C** | Copy the selected segment |
| **Ctrl/Cmd + V** | Paste at the playhead |
| **Delete / Backspace** | Delete the selected segment |
| **← / →** | Move the playhead one frame |
| **Shift + ← / →** | Move the playhead one second |
| **Space** | Play / pause |

(Shortcuts are ignored while you're typing in a text box, so prompt editing isn't affected.)

---

## Advanced settings

The **Advanced** panel mirrors WanGP's generation settings, grouped into tabs:

- **General** — seed, phases, guidance.
- **Sliding Window** — window size, overlap, discard-last-frames.
- **LoRAs** — pick and weight LoRAs for the model.
- **Quality** — perturbation, CFG-star/zero, and related quality options.
- **Steps Skipping** — step-skipping / acceleration options.
- **Post Processing** — spatial/temporal upsampling, film grain.
- **Audio** — post-process remux: MMAudio, custom soundtrack, control-video audio, voice replacement.

Defaults are tuned for LTX-2: model **LTX-2 2.3 Distilled 1.1 22B**, category **720p**,
budget **720x1280 (9:16)**. Changing the model updates the resolution options to match.

<img width="1893" height="938" alt="Screenshot 2026-06-28 143107" src="https://github.com/user-attachments/assets/7a3afda4-3ffa-4cfd-9191-9e92696a5e73" />

<img width="1895" height="909" alt="Screenshot 2026-06-28 143309" src="https://github.com/user-attachments/assets/2eb98764-09cd-44b5-9d5a-040cbeb65509" />

---

## Window settings & defaults

The sliding-window size/overlap default to WanGP's LTX-2 values (**481 / 17**), or to
whatever you've saved as your default.

In the **Session** panel you can choose where window defaults come from:

- **Use WanGP's saved settings** (checkbox on) — pulls from WanGP's own per-model
  settings, i.e. whatever you saved as default on the Video Generation tab.
- **Plugin defaults** (checkbox off) — use the plugin's own saved values instead.
- **💾 Save current as plugin default** — store the current window values as the plugin's
  default.
- **↺ Restore WanGP defaults** — clear the plugin override and go back to WanGP's settings.

Changing window size/overlap in the timeline toolbar also updates the Advanced fields so
the two stay in sync.

[SCREENSHOT: the Session panel showing the settings checkbox and the save/restore buttons]

---

## Going past the frame cap (long videos)

WanGP limits **injected-frame positions** to its `max_source_video_frames` cap
(by default ~125 seconds at 24 fps). Note this limit applies to *injected keyframes*, not
to start/end-image videos.

If you want a longer injected-keyframe timeline:

1. Tick **past cap** in the timeline toolbar and confirm the warning.
2. On each generation the plugin raises WanGP's cap to fit your whole timeline — no need
   to edit any WanGP files.
3. Turn it off and WanGP returns to its normal limit the same session.

Segments whose window runs past the cap are flagged with a **red border** on the timeline.

> ⚠️ **At your own risk.** The cap exists to protect against running out of video memory.
> Going past it can crash, run out of VRAM, or produce bad output on very long timelines —
> keep an eye on your VRAM usage.

<img width="1899" height="768" alt="Screenshot 2026-06-28 144803" src="https://github.com/user-attachments/assets/6ef77cc5-33bc-45aa-9fc5-1bc8aeaaf8f2" />


---

## Saving & loading projects

- Work is **auto-saved** every few seconds, so a page freeze won't lose your timeline.
- Use the **Session** panel to name a project, save it, load it back, or recover your last
  session. Loading a project restores the timeline plus the model, category, resolution,
  and window settings.

---

## Tips

- Place your **first image** at the very start — it anchors the opening shot.
- Watch the **window bands**: an image that lands right on a window seam transfers most
  cleanly.
- **Audio is one continuous track** — it spans the whole timeline and is never split at
  window boundaries, so it won't be flagged like image/text segments.
- If a setting in Advanced doesn't seem to match WanGP, check that you've selected the
  right model first — resolution and window options update per model.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Plugin doesn't load / prompts don't transfer | Make sure there's **only one** LTX Director folder in `plugins`, then restart WanGP. |
| "Invalid Frame Position" on long videos | Enable **past cap** in the toolbar (see above). |
| Window size shows the wrong default | Set your preferred size in Advanced and **Save current as plugin default**, or restore WanGP defaults. |
| Model defaults to the wrong version | The plugin targets **LTX-2 2.3 Distilled 1.1 22B**; pick your model from the selector if your build names it differently. |

---

## Credits

Created by **The-ShadowWalker**. Built on top of **Wan2GP** by DeepBeepMeep
and the LTX-2 models by Lightricks.

<!-- Add your links here: GitHub repo, TikTok/YouTube, support thread, etc. -->

Changelog
All notable changes to LTX Director are documented here.

**v1.3.24**

Added


Apply to Generator now switches the model. Clicking "Apply to Generator"
transfers the model to the Media Generator tab along with all settings (it
previously transferred settings but left the model unchanged). Fix contributed
by **GK Artist**.


**V1.3.17 - v1.3.23**

Added


Keyboard shortcuts on the timeline: copy/paste (Ctrl/Cmd+C/V), Delete to
remove the selected segment, ←/→ to move the playhead (Shift = 1-second
jumps), Space to play/pause.
Multi-clip audio mixing. Multiple audio clips are combined into one
soundtrack with gaps preserved and positions matched to the timeline.
Window-default settings. Choose whether window defaults come from WanGP's
saved per-model settings or the plugin's own saved defaults, with buttons to
save the current values as default or restore WanGP's.
Timeline → Advanced sync. Changing the window size/overlap in the timeline
toolbar updates the matching Advanced fields.


Changed


Audio settings now use WanGP's own audio UI, so the Audio tab matches the
Video Generation tab exactly (MMAudio prompts, custom soundtrack, control-video
audio, voice replacement), including the "Control Video Audio Track" option.
Spatial Upsampling now shows the method + scale as two dropdowns with the
full option set, and produces the exact value WanGP expects.
"Phases" is now shown for LTX-2 distilled (One / Two Phases, default Two).
Sliding-window default corrected to WanGP's LTX-2 values (481 / 17).


Fixed


Default model now correctly selects LTX-2 2.3 Distilled 1.1 22B (was
picking the 1.0 variant).
Changing the model no longer desyncs the resolution (Category and Resolution
Budget stay matched).
Resolution Budget options were missing for some categories; all tiers now show
their full list.
Audio clips no longer show a false sliding-window boundary warning.
Over-cap segments are flagged on the segment border, and the warning no longer
over-fires (only windows that actually run past the cap are flagged).
Minor fixes.



**v1.3.12 – v1.3.16**

Added


Long-timeline support past WanGP's frame cap. WanGP rejects injected-frame
timelines beyond max_source_video_frames (~125s at 24fps), which blocked
long renders. A "past cap" toggle in the timeline toolbar lets the plugin
raise that cap to fit the whole project on each generation (no editing
wgp.py). It reads and restores WanGP's real value, is session-safe (turning
it off restores normal behavior), requires a risk acknowledgment to enable,
and flags affected segments on the timeline.


Fixed


"Invalid Frame Position" error on timelines past ~120s.
Sliding-window count now accounts for "discard last frames."
Minor fixes.



**v1.3.11**

Fixed


Sliding-window count now honors "Discard last frames" so the window count and
bands match the generator.
Minor fixes.

---

## Credits

Created by **The-ShadowWalker**. Built on top of **Wan2GP** by DeepBeepMeep
and the LTX-2 models by Lightricks.

<!-- Add your links here: GitHub repo, TikTok/YouTube, support thread, etc. -->
