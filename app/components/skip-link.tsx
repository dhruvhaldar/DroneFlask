"use client";

import { useState } from "react";

export function SkipLink() {
  const [focused, setFocused] = useState(false);

  return (
    <a
      href="#main-content"
      className="glass"
      style={{
        position: "absolute",
        top: focused ? "1rem" : "-100px",
        left: "1rem",
        padding: "0.75rem 1rem",
        color: "white",
        textDecoration: "none",
        fontWeight: 600,
        zIndex: 9999,
        transition: "top 0.2s ease-out",
        outline: focused ? "2px solid #72f0c4" : "none",
        outlineOffset: "2px",
      }}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
    >
      Skip to main content
    </a>
  );
}
