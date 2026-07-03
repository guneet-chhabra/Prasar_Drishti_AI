---
name: Signal Spectrum UI
colors:
  surface: '#031427'
  surface-dim: '#031427'
  surface-bright: '#2a3a4f'
  surface-container-lowest: '#000f21'
  surface-container-low: '#0b1c30'
  surface-container: '#102034'
  surface-container-high: '#1b2b3f'
  surface-container-highest: '#26364a'
  on-surface: '#d3e4fe'
  on-surface-variant: '#c6c6cd'
  inverse-surface: '#d3e4fe'
  inverse-on-surface: '#213145'
  outline: '#909097'
  outline-variant: '#45464d'
  surface-tint: '#bec6e0'
  primary: '#bec6e0'
  on-primary: '#283044'
  primary-container: '#0f172a'
  on-primary-container: '#798098'
  inverse-primary: '#565e74'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#4edea3'
  on-tertiary: '#003824'
  tertiary-container: '#001c10'
  on-tertiary-container: '#009365'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#031427'
  on-background: '#d3e4fe'
  surface-variant: '#26364a'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: monospace
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  sidebar-width: 260px
  topbar-height: 72px
  container-padding: 32px
  gutter: 24px
  card-gap: 16px
---

## Brand & Style

The design system is engineered for high-stakes intelligence and data synthesis. It embodies an authoritative, technical personality designed for analysts who require clarity amidst complex data streams. The aesthetic blends **Modern Corporate** structure with **Glassmorphism** to create a sense of depth and focus, mimicking a high-end command center.

Drawing inspiration from signal processing and broadcasting, the UI incorporates subtle rhythmic patterns and linear elements that evoke wave frequencies. The emotional response is one of precision, reliability, and "cutting through the noise." It prioritizes information density without sacrificing legibility, ensuring that critical AI-driven insights are immediately actionable.

## Colors

This design system utilizes a sophisticated dark-mode-first palette to reduce eye strain during long-form analysis.

- **Foundational Surfaces:** Deep Navy (`#0F172A`) serves as the core background, while Slate shades provide layered container depths.
- **Accents & Data Vis:** 
    - **Cyan:** Used for neutral system states, active navigation, and general AI-generated insights.
    - **Emerald:** Indicates positive sentiment, high-confidence scores, or "pro-government" data alignment.
    - **Amber/Coral:** Reserved for risk factors, critical alerts, and high-priority anomalies that require immediate attention.
- **Signal Waves:** Linear gradients transition from Secondary to Transparent to simulate frequency oscillations in the background of headers and data cards.

## Typography

The typography system relies on **Inter**, a typeface chosen for its exceptional legibility in data-heavy environments and its neutral, modern tone.

- **Scale:** Headlines use tight letter spacing and heavy weights to project authority. 
- **Data Display:** For numerical values, timestamps, and signal coordinates, a monospaced font should be used to ensure tabular alignment and rapid scanning.
- **Hierarchy:** Labels use uppercase styling with increased letter spacing to differentiate metadata from primary body content.
- **Mobile Adaptation:** Large display titles scale down aggressively on mobile to preserve screen real estate for charts and graphs.

## Layout & Spacing

The layout follows a **Fixed-to-Fluid** hybrid model. A persistent 260px sidebar handles primary navigation, while the main content area utilizes a 12-column fluid grid.

- **The Command Center Grid:** Content is organized into modular "tiles." On desktop, these span varying column counts (e.g., 4 columns for a KPI, 8 for a trend graph).
- **Rhythm:** An 8px linear scale governs all padding and margins. 
- **Navigation:** Primary navigation is vertical (sidebar). Secondary navigation uses a horizontal sub-tab system positioned directly below the top bar or within specific data modules.
- **Breakpoints:** 
    - **Desktop (1280px+):** Full 12-column visibility.
    - **Tablet (768px - 1279px):** Sidebar collapses to icons; 6-column grid.
    - **Mobile (<767px):** Single-column stacked layout; top-bar navigation converts to a bottom-docked menu.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** and **Glassmorphism**, rather than traditional heavy shadows.

- **Base Layer:** The deepest navy background (#0F172A).
- **Surface Layer (Cards):** Semi-transparent surfaces (80% opacity) with a 12px backdrop blur. This creates a "frosted glass" effect that allows background signal patterns to peek through.
- **Borders:** Every card and interactive element features a crisp, 1px border. Use a low-opacity white (10-15%) for neutral elements, and colored borders (Cyan/Emerald/Amber) to denote specific sentiment categories.
- **Active States:** Elements in focus or active use a subtle inner glow (box-shadow: inset) of the primary accent color to simulate an "energized" state.

## Shapes

The design system utilizes a **Soft (Level 1)** roundedness approach to maintain a professional, architectural feel. 

- **Primary Components:** Buttons, inputs, and small widgets use a 4px (0.25rem) corner radius.
- **Data Containers:** Large analytics cards and modal windows use an 8px (0.5rem) radius to feel substantial yet modern.
- **Signal Indicators:** Status dots and certain toggle switches may use pill-shapes (full rounding) to contrast against the otherwise geometric and structured layout.

## Components

- **Analytics Cards:** The core unit of the design system. Features a glassmorphic background, a 1px crisp border, and a "Signal Header" containing a title and a sparkline trend.
- **Buttons:**
    - **Primary:** Solid Cyan with white text.
    - **Secondary:** Transparent with a 1px Cyan border.
    - **Ghost:** No border or background; text-only until hover.
- **Status Chips:** Small, high-contrast badges used for sentiment tagging (e.g., "Positive," "Critical"). They should include a small pulsing dot icon to indicate real-time AI processing.
- **Input Fields:** Dark slate background with a bottom-only 2px border that "glows" Cyan when focused.
- **Navigation Tabs:** Primary tabs are vertical in the sidebar with high-contrast active states. Secondary sub-tabs are horizontal, using an underline indicator that mimics a frequency pulse.
- **Data Visualization:** Charts should use semi-transparent fills and glowing line strokes. Use the defined palette colors (Emerald, Cyan, Coral) to ensure semantic meaning is consistent across all visualizations.