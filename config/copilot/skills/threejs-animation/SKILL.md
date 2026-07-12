---
name: threejs-animation
description: Implement or debug Three.js animation using AnimationClip, AnimationMixer, AnimationAction, GLTF clips, skeletal animation, morph targets, blending, procedural motion, and update-loop performance. Use when objects, characters, cameras, bones, or morph targets must animate or blend correctly.
---

# Three.js Animation

## Workflow

1. Identify whether the motion is clip-based, skeletal, morph-target, procedural, or a blend.
2. Inspect the installed Three.js version and the asset's actual clips, bones, tracks, and morph-target names.
3. Create one clear owner for elapsed time and mixer updates.
4. Configure actions, loop mode, weights, fades, or additive blending explicitly.
5. Keep per-frame work allocation-light and frame-rate independent.
6. Verify start, transition, interruption, completion, cleanup, and reduced/paused update behavior.

Completion requires deterministic action ownership, delta-time updates, correct transitions, and no abandoned mixers, listeners, or animation-frame work.

## Reference Routing

Read the relevant section of [references/full-guide.md](references/full-guide.md):

- clips and keyframe tracks;
- mixers and actions;
- GLTF animation loading;
- skeletons and bone attachments;
- morph targets;
- cross-fades or additive blending;
- animation utilities;
- damping, springs, oscillation, or performance.

Use `rg -n '^## |^### ' references/full-guide.md` to find the branch without loading the entire example catalog.

## Guardrails

- Reuse mixers and actions rather than recreating them each frame.
- Update animation from one render/update loop with delta time.
- Do not assume clip, bone, or morph-target names; inspect the loaded asset.
- Stop actions and uncache roots/clips when disposing long-lived scenes.
- Avoid allocations and scene traversal in hot per-frame paths.
