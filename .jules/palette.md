# Palette's Journal

## 2024-05-22 - Missing Animations
**Learning:** The project uses `animate-fade-in-down` class but it is not defined in the standard Tailwind configuration or custom CSS, leading to missing animations.
**Action:** When using utility classes for animation, always verify they are standard Tailwind or explicitly defined in the project's config/CSS. For this project, stick to standard animations or inline styles if needed.

## 2024-05-23 - Emergency Shortcuts
**Learning:** Critical actions like "Emergency Stop" require global keyboard shortcuts (e.g., Esc) for immediate accessibility, as mouse navigation is too slow in panic situations.
**Action:** Implement global key listeners for emergency actions and expose them via standard visual hints (e.g., `<kbd>` tooltips) to ensure users know they exist.

## 2024-05-24 - Overlay Interaction Traps
**Learning:** Placing interactive elements (toasts) inside a `pointer-events-none` container (to let clicks pass through to the canvas) silently disables interaction for child elements unless `pointer-events-auto` is explicitly re-applied.
**Action:** When designing overlays over 3D canvases, always verify that interactive children (buttons, inputs) explicitly restore pointer events.

## 2024-10-24 - Critical Status Visibility
**Learning:** In real-time control interfaces, text-only status indicators are insufficient for critical failure states. A full-screen (non-blocking) overlay provides unmistakable feedback.
**Action:** Use high-contrast overlays for connection loss with `pointer-events-none` to keep controls accessible. specific learnings: Emojis are unreliable for critical icons across platforms; inline SVGs ensure consistent rendering.
