## 2025-01-20 - Demystifying Jargon and Securing Hardware Actions
**Learning:** For specialized applications like drone control panels, users face unique hurdles. Highly technical jargon (e.g., "Stabilize" vs "Position Hold") can be intimidating and obscure exactly what the hardware will do. Simultaneously, destructive or inherently dangerous actions (like spinning up propellers) require intentionality, as an accidental click can have real-world consequences.
**Action:** Always add descriptive tooltips (`title`) or inline help to clarify domain-specific jargon. Implement explicit friction, such as `window.confirm`, for actions that trigger dangerous real-world hardware states.
## 2026-06-06 - Enhancing Accessibility on Dark Glass UIs
**Learning:** The default browser focus outlines are often completely invisible against dark backgrounds and "glassmorphism" designs (like the drone panel), significantly degrading keyboard navigation. Additionally, range sliders visually indicate values but often lack semantic HTML binding, meaning screen readers can't easily correlate the visible value directly with the input.
**Action:** Always manually define high-contrast `:focus-visible` styles (e.g., using a bright accent color like `#72f0c4`) for interactive elements on dark UI components. Use the `<output htmlFor="id">` tag instead of generic `<span>` elements when displaying a live value associated with a range input to provide correct semantic context.
## 2026-06-07 - Clarifying Disabled States for Safety-Critical Actions
**Learning:** For actions like "Arm Motors" which have strict preconditions (e.g., throttle must be exactly 0 to avoid immediate catastrophic takeoffs), simply disabling the button is not enough. Users may perceive the interface as broken if they don't understand the invisible precondition. A button that silently refuses to work causes frustration and confusion in high-stakes contexts.
**Action:** Always provide inline, explicit explanations for disabled states on safety-critical or destructive actions. Instead of a generic disabled button with "Arm Motors", dynamically update the text to provide the exact actionable instruction required to unlock the state, such as "Zero Throttle to Arm", providing immediate, clear feedback.

## 2026-06-08 - Enhancing Sliders and Preserving Focus on Instructive Buttons
**Learning:** Relying purely on JavaScript for range slider magnetic snapping is often over-engineered. Native `<datalist>` elements provide an elegant, built-in solution for creating magnetic center points, improving precision. Furthermore, when using the `disabled` attribute on an element that displays important dynamic instructions (like "Zero Throttle to Arm"), screen readers may skip it entirely as it becomes unfocusable.
**Action:** Use native `<datalist>` options with matching `list` attributes on `<input type="range">` elements for intuitive snap points without complex JS. Use `aria-disabled="true"` instead of the `disabled` attribute for buttons that convey critical contextual instructions, and manually prevent action execution in the click handler to ensure keyboard users and screen readers can still focus and read the crucial instructions.
## 2026-06-09 - Making Hidden Context Persistent and Accessible
**Learning:** Native `title` tooltips on buttons are inherently flawed for critical contextual information—they are invisible on mobile devices, difficult for screen reader users to access, and require slow hover interactions on desktop. For specialized interfaces with complex modes, hiding descriptions in tooltips degrades discoverability.
**Action:** Replace or augment native hover tooltips with explicit, persistent on-screen text. Use `aria-live="polite"` on a dedicated, visually subtle text element to ensure that when a user switches modes, screen readers immediately announce the descriptive context, vastly improving both visibility and accessibility.

## 2025-01-20 - Enhancing Discoverability over Native Tooltips
**Learning:** Native `title` tooltips on buttons are inherently flawed for critical contextual information—they are invisible on mobile devices, difficult for screen reader users to access, and require slow hover interactions on desktop. For specialized interfaces with complex modes, hiding descriptions in tooltips degrades discoverability.
**Action:** Replace or augment native hover tooltips with explicit, persistent on-screen text. Use interactive focus and hover handlers (`onMouseEnter`, `onFocus`, etc) to dynamically update an inline description element mapped via `aria-describedby` and ensure it uses `aria-live="polite"` so screen readers immediately announce the descriptive context, vastly improving both visibility and accessibility without cluttering the UI.

## 2025-01-20 - Replacing Hidden Tooltips with Visible Helper Text and Keyboard Shortcuts
**Learning:** Native `title` tooltips on interactive elements like sliders are hidden on mobile devices and difficult for keyboard/screen reader users to discover. Additionally, mouse-only actions like "double-click to center" exclude keyboard users.
**Action:** Replace `title` attributes with visible, explicit helper text. To avoid inherited text transformations (like `textTransform: "capitalize"` from parent labels), place the helper text `<span>` outside the `<label>`. Always implement a keyboard equivalent (`onKeyDown` handler listening for relevant keys like '0' or 'Escape') for mouse-only convenience actions to ensure equitable access.

## 2026-06-12 - Associating Hints and Structuring Telemetry Data
**Learning:** For interactive UI inputs (like range sliders), providing visual text hints regarding keyboard shortcuts doesn't automatically translate to an accessible experience. Screen readers need explicitly linked hints. Moreover, presenting key-value data visually as a grid of elements often lacks semantic meaning for screen readers.
**Action:** Use `aria-describedby` on inputs to reference the `id` of visually adjacent hint text, ensuring screen reader users hear instructions like keyboard shortcuts. Also, use description lists (`<dl>`, `<dt>`, `<dd>`) for key-value telemetry data instead of generic `<div>` and `<p>` elements to provide strong semantic structure. In addition, when using `output` to reflect a range `input`'s value visually, consider adding `aria-hidden="true"` to the `output` to avoid screen readers announcing the value twice (once from the input and once from the output).

## 2024-06-13 - [Focus Management on Disabled Actions]
**Learning:** When preventing an action due to an invalid state (like "Zero Throttle to Arm"), silently disabling or ignoring clicks leaves users confused. Guiding them directly to the source of the issue improves usability.
**Action:** When a button is disabled/inactive due to another input's state, clicking it should shift focus to the input that needs correction, providing a clear path to resolution.

## 2024-12-23 - Improve Range Input Accessibility
**Learning:** Adding a `title` attribute to `input[type="range"]` elements serves as a highly effective, native way to provide tooltips for visual users navigating with a mouse, complementing existing ARIA labels or `htmlFor` bindings which only assist screen readers.
**Action:** When adding or updating range sliders or generic input fields, ensure to include a descriptive `title` attribute for native tooltips, while still relying on `<label>` elements and `aria-*` tags for screen reader accessibility.
## 2024-12-23 - Corrective Action Buttons
**Learning:** Buttons providing helpful corrective actions (like auto-zeroing a slider) shouldn't be styled as disabled (`aria-disabled` or `cursor: not-allowed`). This hides the helpful action from both screen readers and sighted users.
**Action:** Always ensure that if a button has an `onClick` handler that actually does something helpful for the user, it is presented as interactive and fully actionable, using `title` and proper ARIA states to clarify its behavior instead of disabling it.

## 2024-06-17 - Zero-Dependency Visual Scanning Enhancements
**Learning:** In telemetry-heavy interfaces, users must quickly parse a dense grid of changing variables. Pure text data often creates a wall of text that requires cognitive load to scan. Adding simple visual anchors drastically reduces this load, but importing full icon libraries can bloat the UI.
**Action:** Use universally supported unicode emojis as zero-dependency visual anchors adjacent to data labels. They dramatically improve "glanceability" and parse speed without adding new dependencies or complex SVG implementations. Always accompany live-updating telemetry lists with `aria-busy` to inform screen reader users that the content within the region is actively changing.

## 2025-01-20 - Maintaining Keyboard Navigation During Async Feedback
**Learning:** For buttons triggering async operations (like "Arm Motors" or switching modes), adding the `disabled` attribute immediately removes the element from the document tab order. If a user triggers the action via keyboard (`Enter` or `Space`), their focus is immediately lost, resetting them to the top of the page—a highly frustrating experience, especially for screen reader users.
**Action:** Use `aria-disabled="true"` combined with manual click/keydown blocking (`if (saving) return;`) instead of the native `disabled` attribute for buttons indicating an active loading state. This allows the button to remain focusable and visually communicate its processing state (e.g., using `cursor: wait` or text changes) without breaking the user's navigational context.

## 2024-05-18 - Visual distinction for keyboard shortcuts
**Learning:** Users often miss keyboard shortcuts hidden in plain text hints, and undocumented shortcuts ('C' for center) cause confusion if discovered accidentally.
**Action:** Always wrap keyboard shortcuts in semantic `<kbd>` tags and style them to look like physical keys (using the design system's style, e.g., glassmorphism) so they stand out clearly and intuitively.
## 2024-05-20 - Contextual Confirmation for Destructive Actions
**Learning:** For actions like disarming a drone, the context of the action matters heavily. Disarming on the ground (throttle 0) should be frictionless. However, disarming mid-air (throttle > 0) causes immediate catastrophic failure. A one-size-fits-all approach to action confirmations either creates annoying friction for safe states or allows accidental catastrophic outcomes in dangerous states.
**Action:** Always evaluate the state-context of destructive actions. Apply conditional friction (like `window.confirm`) only when the current context (e.g., active throttle) implies high risk, allowing safe-state actions to remain frictionless.
## 2026-06-21 - [Replace blocking window.confirm]
**Learning:** Synchronous `window.confirm` calls block the main JavaScript thread, which is problematic for Next.js apps handling real-time state like telemetry.
**Action:** Use an inline confirmation state (e.g., `confirmAction`) and UI to handle warnings non-blockingly.

## 2025-01-20 - Adding Semantic Visual Hierarchy with Native `<meter>` Tags
**Learning:** Pure text-based telemetry indicators (like percentage readings) force users to read and interpret numbers, which increases cognitive load when monitoring live systems. While progress bar components are often introduced to solve this, they usually require new CSS or complex React components that bloat the bundle. Native HTML `<meter>` elements provide a lightweight, semantically correct, and accessible solution out-of-the-box.
**Action:** Use the native `<meter>` tag to provide visual context for scalar telemetry values (like Battery or Link Quality). Leverage its built-in attributes (`min`, `max`, `low`, `high`, `optimum`) to implicitly handle state-based coloring without custom CSS, and always add an `aria-label` to ensure screen readers can contextualize the bar.

## 2025-01-20 - Hiding Decorative Emojis from Screen Readers
**Learning:** When using emojis as visual anchors next to explicit text labels, screen readers announce both the emoji's default literal name and the text label (e.g., "Battery Battery"). This is repetitive and degrades the auditory user experience.
**Action:** Always wrap purely decorative emojis that accompany text labels in `<span aria-hidden="true">`. This ensures they enhance the visual UI for sighted users without adding redundant noise for screen reader users.

## 2025-01-20 - Reducing Auditory Spam on Rapidly Updating States
**Learning:** Adding `aria-live="polite"` to rapidly updating UI elements, such as a "Syncing..." status tied to a slider's real-time continuous movement, overwhelms screen readers with constant, overlapping auditory spam, degrading the user experience.
**Action:** Remove `aria-live` from high-frequency or transient state indicators unless the final state change is critical, infrequent, and needs to interrupt the user's current context. Let visual users rely on the visual indicator without punishing screen reader users.

## 2025-01-20 - Preserving Formatting Context in Range Inputs for Screen Readers
**Learning:** Sighted users see formatting context alongside slider values (e.g., "+50%"). Screen readers, however, only read the raw numeric `value` attribute of the `<input type="range">`, stripping this important context (positive/negative sign and unit).
**Action:** Always provide an explicit `aria-valuetext` attribute on range inputs to ensure screen readers announce the value with its full formatting context (e.g., `aria-valuetext={state[axis] > 0 ? "+" + state[axis] + "%" : state[axis] + "%"}`).

## 2025-01-20 - Keyboard Escape Hatch for Inline Confirmations
**Learning:** When transitioning a button to an inline confirmation state (e.g., clicking to arm -> "Click again to confirm"), keyboard users might reconsider but have no intuitive way to dismiss the warning and reset the button state without shifting focus.
**Action:** Always provide an `onKeyDown` handler on buttons with multi-step inline actions that listens for the `Escape` key, allowing users to safely abort the action and reset the button's state without leaving the element.

## 2026-06-26 - Keyboard Shortcut Resiliency and Screen Reader Optimization
**Learning:** Relying on exact string matches for keyboard shortcuts (like `e.key === 'c'`) breaks when Caps Lock or Shift is active. Furthermore, decorative unicode characters like '✓' add auditory noise for screen reader users.
**Action:** Use `.toLowerCase()` when checking single-character keydown events to ensure reliability across keyboard states. Always wrap purely decorative text characters that accompany status labels in `<span aria-hidden="true">`. Avoid replacing existing CSS classes (like Tailwind utility classes) with inline styles to preserve maintainability; if a component is visually broken due to missing framework CSS, fix it by appending available existing classes (e.g., `.glass`) rather than rewriting its structure.

## 2025-01-20 - Reducing Double Announcements on Tooltips
**Learning:** Adding `aria-live="polite"` to an element acting as a tooltip description (referenced by `aria-describedby` on a focusable element) causes some screen readers to announce the content twice when the user focuses the element: once because it's the described-by content, and once because the live region mutates.
**Action:** Do not use `aria-live` on tooltip containers that update upon hover/focus when they are already linked to the active element via `aria-describedby`. Rely solely on the `aria-describedby` association to provide context to assistive technologies.

## 2025-01-20 - Visible Escape Hatches and Consistent Visual Weight
**Learning:** Providing a keyboard escape hatch (like `Esc`) for inline confirmations is only effective if users know it exists. Without a visible hint, users may feel trapped. Additionally, inline warning states should match the visual weight of active states (e.g., matching border and box-shadow) to properly signal importance.
**Action:** Always include explicitly visible keyboard hints (using `<kbd>` tags) alongside inline warnings so users know how to dismiss them. When applying warning colors, ensure they match the full visual weight (like inset box-shadows) of the app's existing active components.

## 2025-01-20 - Prevent Interaction Layout Shift for Conditional Content
**Learning:** Rendering conditional content (like inline warnings or confirmations) immediately above an interactive target (like a button) causes the interactive target to shift downwards when the conditional content appears. This disrupts the user interaction, often forcing the user to reposition their mouse to complete a multi-step action.
**Action:** Always render conditional inline confirmations or alerts below the primary interactive target that triggered them, or ensure fixed positioning/heights, to prevent the target from shifting away from the user's cursor.
## 2026-06-30 - Emojis as State Anchors and Dimming Neutral Values
**Learning:** Wrapping state-indicating emojis in `aria-hidden="true"` provides visual clarity without adding redundant noise to screen readers, significantly improving accessibility.
**Action:** Always wrap non-semantic visual emojis used alongside text labels with `aria-hidden="true"`.
## 2024-05-24 - Inline Confirmation Layout Shifts
**Learning:** Placing static indicator elements (like status pills) below conditional warnings or confirmations causes a jarring layout shift during interaction.
**Action:** Always render conditional content (like inline warnings or confirmations) below the primary interactive target and any static indicators that triggered them, or ensure fixed positioning/heights to prevent layout displacement.
## 2024-05-15 - Structural classes on inline typography
**Learning:** Applying layout-level structural CSS classes (like large panel boxes with massive shadows and blurs) to inline typographical elements (like `<kbd>`) completely disrupts the inline flow and heavily obscures surrounding text, reducing legibility and aesthetics.
**Action:** Always ensure that inline visual styles (like keycap indicators) use dedicated minimal styles (e.g. slight padding, small border radius) and avoid reusing overarching structural classes (e.g. `.glass` panels).

## 2025-01-20 - Reducing Double Announcements on Visual Meters
**Learning:** Placing an `aria-label` directly on a `<meter>` element that sits adjacent to a raw text percentage causes screen readers to redundantly announce the value twice (once for the text node, once for the meter).
**Action:** When using `<meter>` tags strictly as visual accompaniments to adjacent explicit text values, use `aria-hidden="true"` instead of an `aria-label` to prevent "double-speak" and provide a cleaner auditory experience.

## 2026-07-07 - Verifying the Execution Environment for Utility Classes
**Learning:** Relying on utility classes (e.g., Tailwind's `px-1.5 py-0.5`) on semantic tags like `<kbd>` without confirming the framework is actually installed results in those tags rendering as plain, unstyled text. This completely undermines the UX goal of making keyboard shortcuts visually distinct as physical keys.
**Action:** Always verify the project's CSS architecture before applying utility classes. If a project relies on standard CSS, add semantic styling globally rather than injecting inert framework-specific classes.

## 2025-01-20 - Adding Visual Distinction for Aria-Disabled State
**Learning:** Components sometimes use `aria-disabled="true"` instead of the native `disabled` attribute to maintain keyboard focusability or enable interactive tooltips. However, without explicit CSS rules, these elements look identical to active ones and respond to hover events, which causes confusion and makes the UI feel broken during asynchronous actions.
**Action:** Always add visual inertness styles specifically for `[aria-disabled="true"]`. Reduce opacity, apply a `not-allowed` cursor, and remove hover/active interactions by guarding base CSS rules with `:not([aria-disabled="true"])`.

## 2024-07-09 - Explicit Context on Multi-step Inline Confirmations
**Learning:** Using generic strings like "Click to Confirm" on multi-step buttons introduces cognitive load, particularly for screen reader users or users handling destructive actions (like arming/disarming a drone). Users lose the context of *what* they are confirming directly on the focused element.
**Action:** Always replace generic confirmation labels with explicit, state-aware strings (e.g., `Confirm ${action}`) that describe the exact destructive action being finalized.

## 2025-01-20 - Preserving formatting for magnitude vs directional controls
**Learning:** Hardcoding directional prefixes (like `+`) for all values greater than 0 on range inputs breaks semantic meaning for absolute magnitude controls (like Throttle 0-100), causing confusion when compared to bi-directional axes (like Pitch/Roll/Yaw -100 to 100).
**Action:** Avoid formatting absolute magnitude controls with directional prefixes. Ensure formatting logic conditionally checks the axis type (e.g. `axis !== "throttle"`) before prepending signs to `output` displays and `aria-valuetext`.

## 2025-01-20 - Allowing global semantic ARIA states to override inline styles
**Learning:** Hardcoding generic inline styles (like `opacity: 1` or `cursor: pointer`) on interactive elements forcefully overrides global CSS rules tied to semantic states, such as `[aria-disabled="true"]`. This breaks visual accessibility cues (like reducing opacity or showing a `not-allowed` cursor) during asynchronous operations.
**Action:** Always conditionally apply inline styles (e.g. `opacity: isSaving ? undefined : 1`) to allow global, accessible CSS rules to properly cascade and take precedence when semantic ARIA states are active.

## 2024-05-18 - Missing Failure Feedback in Optimistic UIs
**Learning:** In highly interactive, real-time control interfaces (like drone telemetry), optimistic UI updates that fail silently on the network lead to dangerous state mismatches where users believe critical actions (like 'Disarm') succeeded when they actually didn't.
**Action:** Always provide explicit error or 'Offline' feedback in the UI when async requests fail, especially when local UI state is updated optimistically.

## 2025-01-20 - Actionable Shortcuts vs Disabled States
**Learning:** Using reduced opacity (e.g., 0.8) and warning icons (🛑) on a button that actually performs an auto-correction action (like zeroing a throttle) misleads users into thinking the button is completely disabled. They will seek other ways to fix the issue instead of clicking the helpful shortcut.
**Action:** When a button acts as a shortcut to fix a prerequisite state (like auto-zeroing a slider), style it as fully active and use action-oriented phrasing (e.g., "Auto-Zero") rather than warning phrasing (e.g., "Zero to Arm").

## 2025-01-20 - Optimistic UI State Illusions in Localized Indicators
**Learning:** In systems with optimistic updates, showing localized status pills (like "Armed" or "Safe") alongside separate "Synced/Offline" indicators can create dangerous illusions. If the sync fails, the primary status pill still incorrectly shows the optimistic state, misleading the user.
**Action:** Always intertwine sync error states directly into the most prominent primary status indicators. E.g., if there is an error, the primary status pill should explicitly say "Offline" instead of incorrectly displaying the optimistic "Armed" or "Safe" state.

## 2026-07-18 - Inline Cursors vs Semantic Disabled States
**Learning:** Hardcoded generic inline styles (like `cursor: wait`) forcefully override global semantic CSS rules tied to states like `[aria-disabled="true"]`. This prevents the application from showing standard `not-allowed` cursors and can confuse users when a button is temporarily locked out during network operations.
**Action:** Avoid hardcoding inline cursor states for async actions. Instead, let global `[aria-disabled="true"]` CSS rules handle the visual inertness natively, and add explicit tooltips (e.g., `title="Action unavailable while syncing"`) to provide clear context for why the interaction is blocked.

## 2025-02-12 - Expand double-click targets for axis reset
**Learning:** Expanding hit targets for quick actions (like double-clicking to zero an axis) beyond just the input element significantly improves usability, but when those targets include text (labels/hints), double-clicking often triggers native browser text selection, causing jarring blue highlight flashes.
**Action:** When adding rapid click/double-click handlers to container wrappers (like `.row`), explicitly apply `userSelect: "none"` to prevent unintended and disruptive text selection highlighting during natural interaction.

## 2024-05-14 - Situational Awareness for Real-Time Control UI
**Learning:** Real-time control interfaces require cross-tab situational awareness (`document.title` dynamic updates based on flight state) and protection against catastrophic accidental closures (`beforeunload` during Armed state) because a sudden disconnect could cause a drone crash.
**Action:** Always implement `document.title` state syncing and `beforeunload` protections for dangerous active application states to prevent accidental tab closures.

## 2026-07-21 - Preserve Contextual Button Text During Global Async Operations
**Learning:** Overriding the text of primary action buttons (like Arm/Disarm) with generic loading states (e.g., 'Syncing...') triggered by unrelated global async operations (like sliding a throttle) creates a jarring UX. It visually hijacks the button's context and can disorient users in critical interfaces.
**Action:** Avoid altering contextual button text for global background network state. Handle global loading states elsewhere (e.g., a status pill) and ensure state updates are short-circuited if the target value matches the current state to prevent redundant syncs and UI lockouts.

## 2025-01-20 - Dynamic Text Buttons vs Aria-Pressed
**Learning:** Using `aria-pressed` on a toggle button whose actual text label completely changes to reflect the new state (e.g., from "Arm Motors" to "Disarm") creates a highly confusing, double-spoken state for screen readers. The screen reader will announce "Disarm, toggle button, pressed", mixing the new action with the old state concept.
**Action:** Only use `aria-pressed` on buttons whose primary text or icon remains static (e.g., a "Mute" button that stays "Mute" but toggles pressed state). If the button text explicitly changes to describe the *next* action, do not use `aria-pressed`.

## 2025-01-20 - Accessible Native Keyboard Shortcuts
**Learning:** Relying solely on `<kbd>` text limits accessibility. Sighted users may not know what a single letter like 'C' stands for without context, and screen readers will just read the letter blindly without indicating it's a hotkey.
**Action:** Add explicit `title` (for visual tooltips) and `aria-label` (for screen readers) attributes to `<kbd>` shortcut indicators to ensure both audiences immediately grasp the physical key binding (e.g. `<kbd aria-label="Center" title="Center">C</kbd>`).

## 2025-01-21 - Accessible Keyboard Shortcuts using `<abbr>`
**Learning:** Adding `aria-label` to a `<kbd>` tag does not work for screen readers unless it has an interactive role, leading to redundant/invalid HTML. `aria-label` should not be used on non-interactive elements like `<kbd>`.
**Action:** To make keyboard shortcut abbreviations accessible without invalid ARIA usage, wrap the shortcut text in an `<abbr title="Expanded Text" style={{ textDecoration: "none" }}>` inside the `<kbd>`. This provides context on hover for sighted users and expanded text for screen readers.

## 2025-02-12 - Clearing Multi-step Inline Confirmations on Parallel Interactions
**Learning:** Relying strictly on `onBlur` to dismiss dangerous inline multi-step confirmations (like "Confirm Arm") is insufficient. Many parallel interactions in a UI (like dragging range sliders, double-clicking non-focusable wrappers, or standard button clicks in Safari) do not inherently move browser focus. This causes the dangerous confirmation state to linger unexpectedly while the user is performing unrelated actions.
**Action:** Always explicitly dismiss multi-step inline confirmations during parallel interactions (e.g., when a user interacts with a slider or changes modes). Do not rely solely on `onBlur` events on the confirmation button itself to handle all dismissal cases.

## 2025-02-20 - Prevent screen reader spam on high-frequency state changes
**Learning:** Adding `aria-live="polite"` to rapidly updating UI elements, such as a status pill tied to real-time control modes or continuous network syncing, overwhelms screen readers with constant, overlapping auditory spam, degrading the user experience.
**Action:** Remove `aria-live` from high-frequency or transient state indicators unless the final state change is critical, infrequent, and needs to interrupt the user's current context. Let visual users rely on the visual indicator without punishing screen reader users.

## 2025-02-23 - Visual Hierarchy of Network Statuses
**Learning:** Rendering non-critical network states (like 'Syncing...' or 'Synced') with the same visual weight as critical data or error states ('Offline') creates unnecessary visual noise. In high-density telemetry panels, users' attention should be drawn to problems, not expected background activity.
**Action:** Visually de-emphasize expected, neutral states in status indicators by applying existing utility CSS classes (e.g., `subtle`). This reduces noise and ensures critical error states stand out prominently in the visual hierarchy.

## 2025-03-02 - Animating Inline Emojis requires inline-block
**Learning:** Applying CSS transforms or animations (like `@keyframes spin`) directly to inline elements (such as spans wrapping emojis like `🔄`) will fail because transforms do not function on default `display: inline` properties. The animation will be ignored.
**Action:** When animating inline decorative elements or emojis using CSS transforms, explicitly apply `display: inline-block` to the element (e.g., via a `.spin` class) so the transform box is respected and the animation plays correctly.
## 2026-08-03 - Explicit Escape Hatches for Mobile Users
**Learning:** Relying solely on `onBlur` to cancel inline warnings traps mobile users without an Escape key, as tapping non-interactive areas does not trigger blur events on touch devices.
**Action:** Always provide explicit, tappable 'Cancel' buttons alongside keyboard hints for inline confirmations to ensure touch accessibility.
