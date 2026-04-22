# Panel image prompt template

Loaded by `pipeline/image.py`. Every panel prompt is built by concatenating the style guide, the character block, and the per-panel scene. Character block is passed **verbatim** into every panel so character appearance stays consistent across the four panels.

---

{{style_guide}}

## Characters in this story

{{characters_block}}

## This panel

Beat: {{beat}}

Scene: {{scene}}

## Output requirements

- Square aspect ratio (1:1).
- No text, no speech bubbles, no captions, no signature, no watermark, no page numbers. Just the illustration.
- Full scene visible — do not crop characters at the knees or frame. Show hands and feet where relevant to the action.
- Reuse the exact character appearance described above. Same hair, same clothes, same skin tone, same distinguishing features. This is panel {{panel_index}} of 4 in a consistent series.
