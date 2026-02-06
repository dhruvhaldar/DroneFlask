## 2024-05-23 - Persistent Error Toasts for Accessibility
**Learning:** Temporary error messages (toasts) that auto-dismiss are a significant accessibility barrier (WCAG 2.2.1), especially for users who need more time to read or interact with the content.
**Action:** Always ensure that error or critical alert toasts persist until the user manually dismisses them. Only use auto-dismiss for "success" or "info" status updates.

## 2024-05-24 - Continuous Control Inputs on UI Buttons
**Learning:** Users expect on-screen buttons for continuous values (like throttle) to auto-repeat or accumulate when held, mirroring physical button/joystick behavior. Single-click-only implementation makes mobile/mouse usage impractical.
**Action:** Implement `setInterval` loops for "press and hold" interactions on UI buttons that control continuous variables.
