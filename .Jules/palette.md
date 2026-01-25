# Palette's Journal

## 2024-10-23 - Soft Disable Pattern
**Learning:** For real-time apps with connection states (like this drone sim), overlaying a "Signal Lost" message isn't enough. Users try to click bright buttons.
**Action:** Use `opacity-50 grayscale pointer-events-none` on UI containers (Header, Footer) when offline to visually and functionally disable them.
