## 2024-05-21 - System Status Visibility
**Learning:** When the system enters a disconnected state ("Signal Lost"), visually disabling interactive controls (via opacity and grayscale) is critical. Without this, users encounter "clickable" buttons that silently fail, leading to frustration.
**Action:** Always map system connection state to UI interactivity state by modifying the visual affordance of controls (e.g., dimming) and programmatically disabling them.

## 2024-05-22 - Invisible Interaction Discovery
**Learning:** Users often miss "standard" but invisible interactions like 3D camera controls (OrbitControls) unless explicitly prompted. A transient, "toast-like" hint that fades on first interaction is an effective, non-intrusive way to educate users without permanent UI clutter.
**Action:** Use ephemeral, interaction-triggered overlays to reveal hidden capabilities in rich media or canvas interfaces.

## 2026-01-30 - Ephemeral UI Timing
**Learning:** Auto-dismissing UI elements (like toasts) that don't pause on interaction can frustrate users and violate WCAG timing guidelines, especially for those who read slower or use keyboard navigation.
**Action:** Always implement pause-on-hover and pause-on-focus listeners for transient notifications to give users control over the reading time.
