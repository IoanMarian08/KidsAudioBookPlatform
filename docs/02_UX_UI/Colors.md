# Color System

Version: 2.0.0  
Status: Proposed visual token values; product approval required before final brand sign-off  
Owner: Design System

## 1. Direction

The [Product Bible](../00_Project/Product_Bible.md) prescribes Midnight Blue, Warm Cream, Golden Yellow, Sage Green, Soft Lavender, Sky Blue and Warm Brown. These are the canonical **color families**. Hex values below are implementation proposals, not historically approved brand values.

## 2. Proposed primitive palette

| Token | Proposal | Intended use |
|---|---|---|
| midnight.900 | #17243B | Dark text and night backgrounds |
| midnight.700 | #304760 | Secondary dark surface |
| cream.50 | #FFF9ED | Default warm child surface |
| cream.100 | #F6EFDf | Gentle surface contrast |
| gold.400 | #EDBD55 | Highlight/accent, not small-text color |
| sage.500 | #6F987D | Quiet confirmation and nature theme |
| lavender.300 | #D8C6EC | Gentle illustration/UI accent |
| sky.300 | #A9D8F0 | Day theme and selections |
| brown.700 | #684935 | Warm secondary text |
| neutral.white | #FFFFFF | Surface and reverse text |

Validate every color pair with automated contrast checks before committing tokens to Flutter.

## 3. Semantic roles

| Role | Light/Child | Night/Child | Parent Zone |
|---|---|---|---|
| surface.primary | cream.50 | midnight.900 | neutral.white |
| surface.secondary | cream.100 | midnight.700 | cream.50 |
| text.primary | midnight.900 | neutral.white | midnight.900 |
| text.secondary | brown.700 | cream.100 | midnight.700 |
| accent.decorative | gold.400 | lavender.300 | sky.300 |
| interactive.primary | midnight.900 | cream.50 | midnight.900 |

Actual foreground/background pairings must pass contrast validation. Do not assume that accent colors work for normal body text.

## 4. Accessibility requirements

- Normal-size text must aim for WCAG AA contrast ratio >= 4.5:1 and large text >= 3:1.
- Non-text controls, indicators and focus states must meet >= 3:1 where applicable.
- A status label must have text/icon meaning in addition to color.
- Night mode must reduce perceived brightness while preserving readable text and parent controls.
- Never use flashing saturated color to increase child engagement.
- Validate in grayscale and representative color-vision deficiency simulations.

## 5. Behavioral rules

Premium content must be recognizable by explicit label/icon instead of gold alone. Error, warning and successful states use semantic roles independent of the decorative palette. Never encode children’s profiles solely with colored avatars.

Night mode and time-of-day background are **separate concepts**: night background may be selected based on local time while system brightness/contrast remains authoritative for readability.

## 6. Usage example

~~~dart
// Illustrative token interface. Match actual ThemeExtensions naming at implementation.
final surface = context.appColors.surfacePrimary;
final text = context.appColors.textPrimary;
~~~

Avoid magic hex literals in widgets. Maintain a token export for Flutter and design-tool usage, verify cross-platform screenshots and record palette revisions.

## 7. Approval checklist

[ ] Color contrast matrix passes  
[ ] Child/Parent states tested in light and night contexts  
[ ] Critical actions distinguishable without color  
[ ] Error/warning/premium labeling is unambiguous  
[ ] OLED night mode does not obscure controls  
[ ] Brand owner approves final primitive values

Related: [Design System](UI_Design_System.md), [Typography](Typography.md), [UX Guidelines](UX_Guidelines.md).
