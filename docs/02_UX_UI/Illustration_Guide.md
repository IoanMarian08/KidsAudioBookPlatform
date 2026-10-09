# Illustration Guide

Version: 2.0.0  
Status: Content production baseline  
Owner: Creative Direction and Editorial

## 1. Visual language

The Product Bible defines **digital watercolor**, soft edges, pastel colors, warm light and gentle characters. Illustrations are meant to support imagination and comprehension without frightening imagery, aggressive shadows or hyper-realistic violence.

## 2. Editorial requirements

- Illustrations must match the approved story script, age range, locale and scene timing.
- Character appearance, wardrobe and setting remain consistent between episodes.
- Avoid age-inappropriate imagery, unreviewed brand logos, religious/political persuasion, stereotypes and identifiable real children.
- No embedded text unless separately localized, approved and required.
- Every asset must have rights/provenance records and a reviewer decision.
- Generative AI assistance, if used, requires provenance, rights and child-safety review before publication.

## 3. Asset families

| Asset | Usage | Quality criteria |
|---|---|---|
| Story cover | Catalog/home/detail | Recognizable at thumbnail scale; clear focal point |
| Scene illustration | Story playback | Consistent narrative timeline, no essential text |
| Episode thumbnail | Series browsing | Distinct yet coherent with parent series |
| Collection art | Curated groups | Mood/theme without spoiling stories |
| Child room decorative layer | Day/night ambience | Lightweight, calm, optional |
| Empty/error illustration | Support states | Reassuring, not misleading or shaming |

## 4. Technical pipeline

1. Create source art at sufficient resolution; preserve layered editable original in editorial storage.
2. Produce defined rendition sizes (thumbnail/card/detail) and mobile-friendly formats with quality tests.
3. Strip sensitive EXIF, validate MIME and dimensions, scan files, verify transparency requirements.
4. Include asset version and content hash; never reuse immutable CDN key for changed bytes.
5. Associate licensed asset with story, locale/age classification and timing cues where applicable.
6. Publish only after editor approval; revoke/cache invalidate on takedown.

The application must gracefully handle missing rendition or failed image load without blocking audio playback.

## 5. Accessibility

Editorial metadata should include a short, factual alt-description for essential scene meaning; decorative pictures are hidden from screen readers. Never place critical navigation or warning meaning only in illustration. Contrast should be evaluated for overlaid labels, otherwise use dedicated UI surfaces.

## 6. Consistency and review sheet

Each illustration package must include story ID, asset ID/version, creative owner, source/rights proof, locale, age suitability, review state, crop-safe region, palette reference and content sensitivity notes. Before publishing, check narrative accuracy, tone, inclusive representation, copyright, potential frightening content and readability at small sizes.

Related: [Product Bible](../00_Project/Product_Bible.md), [Colors](Colors.md), [Mascot](Mascot.md), [Admin Dashboard](../03_Architecture/Admin_Dashboard.md).
