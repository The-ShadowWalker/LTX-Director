# LTX-Director
Wan2GP plugin ported from a ComfyUI node found here https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI 

this is designed for image injection and workflow enhancement. Maintained for Wan2GP integration and usability.
https://github.com/deepbeepmeep/Wan2GP.git


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


Changed

the way it saves everything is now put in a zip file, fixing the error that you get when it was saving everything in just a Json file. 
New defaults: Model defaults to LTX-2 2.3 Distilled 1.1 22B, Category
defaults to 720p, and Resolution Budget defaults to 720x1280 (9:16).
