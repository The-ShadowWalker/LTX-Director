# LTX-Director
Wan2GP plugin ported from a ComfyUI node found here https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI 

this is designed for image injection and workflow enhancement. Maintained for Wan2GP integration and usability.
https://github.com/deepbeepmeep/Wan2GP.git


v1.3.16

Fixed


Over-cap warning no longer over-fires. The warning now finds the actual
sliding window a keyframe falls into and only flags it if that window
extends past WanGP's frame cap. A keyframe whose window ends exactly on the
cap is treated as fine — only windows that genuinely run past it are flagged.
All cap/timing logic is settings-driven, not hardcoded. The warning label,
the window layout, the risk dialog, and the "past the default" count are all
computed from the live fps, window size/overlap, and the cap value read from
WanGP — no hardcoded frame numbers or seconds.


Added


Risk acknowledgment on the override. Enabling "past cap" now requires an
explicit confirmation that explains it bypasses WanGP's built-in maximum
frame limit, that the limit guards against running out of VRAM, and that the
user proceeds at their own risk. Declining leaves it off.


v1.3.15

Added


"Past cap" override moved into the timeline toolbar (next to bands/snap),
so it's visible instead of buried in a collapsed panel.
Session-safe cap handling. When the override is on, the plugin raises
WanGP's max_source_video_frames to cover the whole timeline on each
generation. When it's turned off, the cap is restored to WanGP's original
value on the next generation, so behavior returns to normal within the same
session without a restart.


v1.3.14

Added


Plugin raises the cap itself. With the override on, the plugin sets
WanGP's max_source_video_frames to fit the project on every generation, so
long injected-frame timelines work without hand-editing wgp.py. The value
is only ever raised, never lowered.


v1.3.13

Added


Override toggle + live cap reading. The plugin reads WanGP's
max_source_video_frames at runtime (instead of assuming a fixed number) and
adds an override so injected-frame positions past the cap can be sent through
rather than clamped.


v1.3.12

Fixed


"Invalid Frame Position" error past ~120s. WanGP rejects injected image
positions beyond its max_source_video_frames cap (3000 frames ≈ 125s at
24fps). Long timelines hit this and the whole job was refused. Positions are
now handled against that cap so generation isn't blocked, and an on-timeline
marker flags keyframes that sit past it. The original keyframe position
semantics are otherwise unchanged.



v1.3.11

Fixed


Sliding-window count now honors "Discard last frames." Window math was
computing the stride as size − overlap, but the engine uses
size − discard − overlap. With a non-zero discard setting the window count
and the on-timeline window bands could drift from what the generator actually
produced. Discard is now threaded through the count, the preview, the window
bands, and save/restore. (Default discard is 0, so this only affected setups
that changed it.)
Verified the window-count formula against the Wan2GP reference across tens of
thousands of valid configurations — it matches the engine exactly.


v1.3.10

Added


requirements.txt for reference/documentation. A working Wan2GP install
already provides every dependency the plugin uses (av, soundfile, numpy are
in Wan2GP's own requirements; Pillow comes in transitively), so nothing
normally needs installing — the file documents what the plugin imports and
acts as a safety net for slimmed-down installs.


v1.3.9

Fixed


Audio clips no longer show a false sliding-window boundary warning. Audio
is a single continuous file that spans the whole timeline and is never split
at window boundaries, so the crossing warning (border, ⚠ marker, and the
properties-panel notice) no longer appears for audio. Image and text segments
still get the warning, since those are genuinely window-bound.



v1.3.8

Fixed


Resolution Budget now updates with the Category. Selecting a Category
(e.g. 720p) repopulates the Resolution Budget list with that tier's options
instead of leaving a stale/partial list. This now happens on the very first
render and on project load — not only when you manually click the Category
dropdown.
720x1280 (9:16) is now available and selected by default. Previously the
default budget couldn't be set because the 720p list wasn't built yet, so the
value didn't "stick."
All Category tiers show their complete option list. Verified each tier
(256p / 320p / 384p / 480p / 540p / 720p / 1080p) exposes its full set — e.g.
480p includes 832x624, 624x832, 720x720, 832x480, 480x832; 720p includes
720x1280 plus the rest.
Loading a saved project updates the Budget list to match the restored
Category. All three load paths (Recover Last, Load Path, and file load) now
refresh the budget choices after restoring the Category, while keeping the
saved resolution selected.


Notes


Resolution-locked models are respected: if a model locks its resolutions, the
plugin keeps that locked list instead of forcing the 720p default.



v1.3.7

Fixed


Timeline "Clear" button now works. It previously relied on a confirmation
dialog that the embedded timeline blocked, so clicking it did nothing. It now
uses a two-step "click again to clear" confirmation that always works (and the
dialog permission was added as a fallback).
Model is restored when loading a project. Loading a saved or autosaved
project now switches the Model selector back to the model that was in use when
the project was saved. (Previously the model never changed on load.)
Category is saved and restored. The Category (resolution tier) was not
being tracked at all, so it was never saved or restored. It is now persisted
with the project and restored on load. It remains a UI-only control and is not
sent to the generator.
Resolution Budget is restored. Now persists and restores correctly across
Recover Last, Load Path, and file load.
Selection borders are always visible. The selected segment is now drawn on
top of its neighbours with a bright, high-contrast highlight, so its border no
longer disappears behind an overlapping segment, making it easy to see what is
selected and adjust it.


Added


Snap to edges, with a toggle. A new snap checkbox in the timeline
toolbar. When on, segment edges snap to other segments, the playhead, and
sliding-window boundaries while dragging. Hold Alt to bypass snapping
momentarily.
