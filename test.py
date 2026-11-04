import re

with open("app/components/control-panel.tsx") as f:
    text = f.read()

# Check for specific UX patterns to see if there's anything missing
print("Has aria-live polite?", "aria-live=\"polite\"" in text)
print("Has aria-label on <kbd>?", "<kbd aria-label" in text)
print("Has TooltipTerm focus outline?", "tabIndex={0}" in text and "TooltipTerm" in text)
print("Has Touch action none on range slider?", "touch-action: none" in open("app/globals.css").read())
print("Has error retry wrapper with aria-label?", "aria-label=\"Retry connection\"" in text)
