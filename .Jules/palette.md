## 2024-05-21 - System Status Visibility
**Learning:** When the system enters a disconnected state ("Signal Lost"), visually disabling interactive controls (via opacity and grayscale) is critical. Without this, users encounter "clickable" buttons that silently fail, leading to frustration.
**Action:** Always map system connection state to UI interactivity state by modifying the visual affordance of controls (e.g., dimming) and programmatically disabling them.
