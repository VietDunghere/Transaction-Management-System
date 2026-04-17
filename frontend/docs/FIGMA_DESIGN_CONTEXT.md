# Figma Design Context — HuzaFraud Dashboard

> **Source:** [HuzaFraud (Figma)](https://www.figma.com/design/xJSaeyid68w3gxjxA4KK1Z/HuzaFraud)
> **Design system:** SnowUI (snowui.byewind.com)
> **Last modified:** 2026-03-10
> **Extracted:** 2026-04-17 (automated deep scan via Figma REST API)

---

## 1. File Structure

| Page             | ID         | Purpose                             |
| ---------------- | ---------- | ----------------------------------- |
| Dashboard        | `0:1`      | Main dashboard screens (6 variants) |
| Design system    | `509:2201` | Component library & color reference |
| Made with SnowUI | `401:9440` | Attribution / showcase              |
| Cover            | `1:9655`   | Project cover                       |

### Dashboard Variants

| Variant          | Node ID       | Size        | Figma Link                                                                                      |
| ---------------- | ------------- | ----------- | ----------------------------------------------------------------------------------------------- |
| Light — compact  | `549:8646`    | 1440 x 1024 | [Open](https://www.figma.com/design/xJSaeyid68w3gxjxA4KK1Z/HuzaFraud?node-id=549-8646&m=dev)    |
| Dark — compact   | `54869:11584` | 1440 x 1024 | [Open](https://www.figma.com/design/xJSaeyid68w3gxjxA4KK1Z/HuzaFraud?node-id=54869-11584&m=dev) |
| Light — expanded | `54869:6543`  | 1440 x 1708 | [Open](https://www.figma.com/design/xJSaeyid68w3gxjxA4KK1Z/HuzaFraud?node-id=54869-6543&m=dev)  |
| Dark — expanded  | `54869:6544`  | 1440 x 1708 | [Open](https://www.figma.com/design/xJSaeyid68w3gxjxA4KK1Z/HuzaFraud?node-id=54869-6544&m=dev)  |
| Mobile — light   | `54869:8609`  | 393 x 1767  | [Open](https://www.figma.com/design/xJSaeyid68w3gxjxA4KK1Z/HuzaFraud?node-id=54869-8609&m=dev)  |
| Mobile — dark    | `54869:8610`  | 393 x 1767  | [Open](https://www.figma.com/design/xJSaeyid68w3gxjxA4KK1Z/HuzaFraud?node-id=54869-8610&m=dev)  |

---

## 2. Layout Structure (Desktop 1440 x 1024)

```
+--Sidebar--+----------Header-----------+--Right Bar--+
|   212px   |         948 x 68           |   280px     |
|           +----------------------------+             |
|           |                            |             |
|           |      Main Content          | Notifications|
|           |      892 x 1086            | Activities  |
|           |      (starts x=240 y=140)  | Contacts    |
|           |                            |             |
+-----------+----------------------------+-------------+
```

### Section Dimensions

| Section          | Width | Height      | Padding (T/R/B/L) | Gap           | Layout          | Border                    |
| ---------------- | ----- | ----------- | ----------------- | ------------- | --------------- | ------------------------- |
| **Sidebar**      | 212   | 1024 (full) | 16 / 16 / 16 / 16 | 8             | VERTICAL        | right: 0.5px `#0000001A`  |
| **Header**       | 948   | 68          | 20 / 28 / 20 / 28 | SPACE_BETWEEN | HORIZONTAL      | bottom: 0.5px `#0000001A` |
| **Right Bar**    | 280   | 1024 (full) | 16 / 16 / 16 / 16 | 16            | VERTICAL        | left: 0.5px `#0000001A`   |
| **Main Content** | 892   | scrollable  | 0                 | 28            | HORIZONTAL WRAP | none                      |

### Expanded Layout (1440 x 1708)

The expanded variant removes the Right Bar, giving main content the full width:

| Section          | Width | Height      |
| ---------------- | ----- | ----------- |
| **Sidebar**      | 220   | 1708 (full) |
| **Header**       | 1188  | 36          |
| **Main Content** | 1220  | 1708        |
| **Footer**       | 1188  | 56          |

Additional expanded content: full-width chart block (1188x360), two medium blocks (586x268 each), data table block (1188x420 with 1140x320 table), and footer with copyright.

### Mobile Layout (393 x 1767)

| Section     | Width | Height |
| ----------- | ----- | ------ |
| **Nav Bar** | 393   | 98     |
| **Content** | 393   | 1572   |
| **Tab Bar** | 393   | 97     |

---

## 3. Color System

### Light Mode

| Token              | Hex       | Opacity    | Usage                                                   |
| ------------------ | --------- | ---------- | ------------------------------------------------------- |
| `bg-primary`       | `#FFFFFF` | 100%       | Page background, cards                                  |
| `bg-secondary`     | `#F9F9FA` | 100%       | Content blocks, panels                                  |
| `bg-subtle`        | `#000000` | 4% (`0A`)  | Very subtle tinted surfaces                             |
| `bg-accent-purple` | `#EDEEFC` | 100%       | Stat cards (Views, New Users), notification icon bg     |
| `bg-accent-blue`   | `#E6F1FD` | 100%       | Stat cards (Visits, Active Users), notification icon bg |
| `text-primary`     | `#000000` | 100%       | Headings, body text, nav labels                         |
| `text-secondary`   | `#000000` | 40% (`66`) | Secondary labels, timestamps                            |
| `text-tertiary`    | `#000000` | 20% (`33`) | Muted text, placeholders                                |
| `text-disabled`    | `#000000` | 10% (`1A`) | Disabled text                                           |
| `border-default`   | `#000000` | 10% (`1A`) | Dividers, card borders, section separators              |
| `border-strong`    | `#000000` | 100%       | Rare strong borders                                     |
| `accent-indigo`    | `#4F507F` | 100%       | Logo, icon fills                                        |

### Dark Mode

| Token              | Hex       | Opacity    | Usage                                            |
| ------------------ | --------- | ---------- | ------------------------------------------------ |
| `bg-primary`       | `#333333` | 100%       | Page/root background                             |
| `bg-surface`       | `#FFFFFF` | 4% (`0A`)  | Content blocks, panels                           |
| `bg-elevated`      | `#FFFFFF` | 10% (`1A`) | Input backgrounds, elevated surfaces             |
| `bg-accent-purple` | `#EDEEFC` | 100%       | Stat cards (same as light)                       |
| `bg-accent-blue`   | `#E6F1FD` | 100%       | Stat cards (same as light)                       |
| `text-primary`     | `#FFFFFF` | 100%       | Headings, body text, nav labels                  |
| `text-secondary`   | `#FFFFFF` | 40% (`66`) | Secondary labels                                 |
| `text-tertiary`    | `#FFFFFF` | 20% (`33`) | Muted text                                       |
| `text-disabled`    | `#FFFFFF` | 15% (`26`) | Disabled/placeholder text                        |
| `text-on-accent`   | `#000000` | 100%       | Text on accent-colored cards                     |
| `border-default`   | `#FFFFFF` | 15%        | Dividers, section separators (1px inside stroke) |

### Theme Switching Pattern

The design uses an **alpha-based theming** approach:

- Light mode: `#000000` at various alpha levels for text/borders on `#FFFFFF` background
- Dark mode: `#FFFFFF` at various alpha levels for text/borders on `#333333` background
- Accent colors (`#EDEEFC`, `#E6F1FD`) remain **identical** in both themes
- Text on accent cards is always `#000000` (even in dark mode)

---

## 4. Typography

**Font family:** `Inter` (sole font across entire design)

### Type Scale

| Name         | Size | Weight         | Line Height | Letter Spacing | Usage                                           |
| ------------ | ---- | -------------- | ----------- | -------------- | ----------------------------------------------- |
| `heading-xl` | 24px | 600 (SemiBold) | 32px        | 0              | Stat card numbers ("7,265")                     |
| `heading-sm` | 14px | 600 (SemiBold) | 20px        | 0              | Block titles, nav section active item, emphasis |
| `body`       | 14px | 400 (Regular)  | 20px        | 0              | Nav items, notification text, body copy         |
| `caption`    | 12px | 400 (Regular)  | 16px        | 0              | Timestamps, secondary labels, breadcrumb text   |

### Text Color Combinations (Light)

| Style         | Color           | Example                                   |
| ------------- | --------------- | ----------------------------------------- |
| Primary body  | `#000000`       | "ByeWind", "Overview", "You fixed a bug." |
| Section label | `#000000` / 40% | "Dashboards", "Pages"                     |
| Timestamp     | `#000000` / 40% | "Just now", "59 minutes ago"              |
| Placeholder   | `#000000` / 20% | Search placeholder                        |

### Text Color Combinations (Dark)

| Style         | Color           | Example                               |
| ------------- | --------------- | ------------------------------------- |
| Primary body  | `#FFFFFF`       | "Traffic by Website", "Notifications" |
| Section label | `#FFFFFF` / 40% | Category labels                       |
| Timestamp     | `#FFFFFF` / 40% | "59 minutes ago"                      |
| Placeholder   | `#FFFFFF` / 15% | Search placeholder                    |
| On accent     | `#000000`       | Card numbers on lavender/blue cards   |

---

## 5. Spacing System

**Base unit:** 4px

### Spacing Scale

| Token       | Value | Usage                                                      |
| ----------- | ----- | ---------------------------------------------------------- |
| `space-0.5` | 2px   | Line separator padding                                     |
| `space-1`   | 4px   | Icon-to-text gap (small), button internal padding          |
| `space-2`   | 8px   | Default gap, list item padding, sidebar gap, icon-text gap |
| `space-3`   | 12px  | Button horizontal padding, sidebar section label padding   |
| `space-4`   | 16px  | Right bar gap, sidebar/right-bar container padding         |
| `space-5`   | 20px  | Header vertical padding, icon group gap                    |
| `space-6`   | 24px  | Card/block internal padding (all sides)                    |
| `space-7`   | 28px  | Header horizontal padding, main content gap                |
| `space-10`  | 40px  | Large gaps (background blur radius)                        |
| `space-12`  | 48px  | Counter-axis spacing                                       |

### Most Used Padding Patterns

| Pattern (T/R/B/L)   | Count | Component                                         |
| ------------------- | ----- | ------------------------------------------------- |
| `8 / 8 / 8 / 8`     | 32x   | Sidebar items, list items, notification rows      |
| `4 / 4 / 4 / 4`     | 10x   | Small internal padding, icon containers           |
| `24 / 24 / 24 / 24` | 9x    | Cards, content blocks                             |
| `4 / 12 / 4 / 12`   | 6x    | Buttons, breadcrumb items, sidebar section labels |
| `16 / 16 / 16 / 16` | 2x    | Sidebar container, Right Bar container            |
| `20 / 28 / 20 / 28` | 1x    | Header                                            |
| `4 / 8 / 4 / 8`     | —     | Search input                                      |

---

## 6. Border Radius

| Token         | Value | Usage                                                     |
| ------------- | ----- | --------------------------------------------------------- |
| `radius-xs`   | 4px   | Small tags, dots                                          |
| `radius-sm`   | 8px   | Buttons, inputs, tags, small cards                        |
| `radius-md`   | 12px  | Medium cards, blocks (primary radius in dark mode)        |
| `radius-lg`   | 16px  | Larger containers                                         |
| `radius-xl`   | 20px  | Stat cards, content blocks (primary radius in light mode) |
| `radius-2xl`  | 24px  | Large card panels                                         |
| `radius-full` | 80px  | Avatars, pill shapes                                      |

---

## 7. Shadows & Effects

| Effect          | Value | Usage                                  |
| --------------- | ----- | -------------------------------------- |
| Background blur | 40px  | Logo component, glass/overlay elements |
| Drop shadow     | none  | No drop shadows in either theme        |

The design is notably **flat** — no shadows are used for elevation. Depth is communicated through:

- Background color differentiation (white vs `#F9F9FA` in light; `#333333` vs white-4% in dark)
- Border separators (0.5px or 1px strokes)

---

## 8. Stroke / Border System

### Light Mode

| Weight | Color                   | Side   | Usage                |
| ------ | ----------------------- | ------ | -------------------- |
| 0.5px  | `#0000001A` (black 10%) | right  | Sidebar divider      |
| 0.5px  | `#0000001A` (black 10%) | bottom | Header divider       |
| 0.5px  | `#0000001A` (black 10%) | left   | Right Bar divider    |
| 1.0px  | `#000000`               | all    | Strong border (rare) |

### Dark Mode

| Weight | Color            | Side   | Usage                               |
| ------ | ---------------- | ------ | ----------------------------------- |
| 1.0px  | `#FFFFFF` at 15% | inside | Sidebar, Header, Right Bar dividers |
| 0.5px  | `#FFFFFF` at 15% | inside | Input underlines                    |

---

## 9. Icon System

### Sizes

| Size        | Count (Light) | Count (Dark) | Usage                                                     |
| ----------- | ------------- | ------------ | --------------------------------------------------------- |
| **16 x 16** | 27            | 49           | Small icons — nav items, notifications, actions           |
| **20 x 20** | 13            | 15           | Medium icons — sidebar section icons, logo marks          |
| **24 x 24** | 16            | 34           | Large icons — avatars, action buttons, notification icons |

### Icon Components Used

| Icon Name          | Context                               |
| ------------------ | ------------------------------------- |
| `BugBeetle`        | Notification: bug fix                 |
| `User`             | Notification: new user                |
| `Broadcast`        | Notification: subscription            |
| `ArrowLineRight2`  | Sidebar: active nav item indicator    |
| `ArrowLineRight-s` | Sidebar: collapsed nav item indicator |
| `Dot2`             | Sidebar: top-level nav bullet         |

### Avatar System

All avatars are **24 x 24** with `border-radius: 80px` (fully circular).

Named avatar variants: `AvatarByewind`, `AvatarAbstract03`, `AvatarFemale03`, `AvatarMale02`, `Avatar3d03`, `AvatarAbstract04`, `AvatarFemale06`, `AvatarMale01`, `AvatarFemale01`, `AvatarMale04`, `AvatarFemale04`, `AvatarFemale05`

---

## 10. Component Inventory

### Stat Cards

```
+---------------------------+
|  [label]        p=24      |
|  [rolling-number]         |
|  [trend-indicator]        |
+---------------------------+
  202 x 112 (light) / 202 x 108 (dark)
  bg: alternating #EDEEFC / #E6F1FD
  radius: 20px
  padding: 24px all sides
  gap: 8px (vertical)
  layout: VERTICAL
```

Card labels: **Views**, **Visits**, **New Users**, **Active Users**

### Content Blocks

```
+--------------------------------------+
|  [title-bar]  14px/600   p=24        |
|  [chart or content]                  |
+--------------------------------------+
  variable width, bg: #F9F9FA (light) / #FFFFFF0A (dark)
  radius: 20px
  padding: 24px all sides
  gap: 16px (vertical)
```

Block types in compact view:

| Block               | Size      | Content                                                                       |
| ------------------- | --------- | ----------------------------------------------------------------------------- |
| Revenue chart       | 662 x 330 | Line chart (This year / Last year), Y-axis: 0-30K                             |
| Traffic by Website  | 202 x 330 | Donut chart + list (Google, YouTube, Instagram, Pinterest, Facebook, Twitter) |
| Traffic by Device   | 432 x 280 | Bar chart, Y-axis: 0-30K                                                      |
| Traffic by Location | 432 x 280 | Map/geo visualization                                                         |
| Marketing & SEO     | 892 x 280 | Area chart, full width, Y-axis: 0-30K                                         |

Additional blocks in expanded view:

| Block            | Size       | Content                             |
| ---------------- | ---------- | ----------------------------------- |
| Full-width chart | 1188 x 360 | Large line/area chart               |
| Medium chart A   | 586 x 268  | Chart with tooltip (78x44)          |
| Medium chart B   | 586 x 268  | Chart                               |
| Large chart      | 1188 x 340 | Chart                               |
| Data table       | 1188 x 420 | Table (1140 x 320), with header row |

### Chart Components

| Component                   | Sizes                     | Type                     |
| --------------------------- | ------------------------- | ------------------------ |
| `ChartMotion`               | 384x196, 614x246, 844x196 | Animated chart widget    |
| `DonutGraph` / `DonutChart` | 28x33 to 120x120          | Pie/donut visualization  |
| `HorizontalBar 03`          | 80 x 34                   | Horizontal bar segment   |
| `Rolling number`            | 48x36, 72x36              | Animated counter group   |
| `Roll numbers`              | 8x36, 16x36               | Individual counter digit |

### Sidebar

```
Sidebar (212px wide, full height)
  padding: 16px, gap: 8px, VERTICAL
  +------------------------------+
  | [Avatar 24x24] [Username]    |  ByeWind row (180x40, p=8)
  |------------------------------|
  | [Dot] Overview               |  Top nav (180x36, p=8, gap=4)
  | [Dot] Projects               |
  |------------------------------|
  | DASHBOARDS (section label)   |  Section label (180x28, p=4/12)
  |   [>] [icon] Default         |  Nav item (180x36, p=8, gap=4)
  |   [>] [icon] eCommerce       |    Arrow icon: 16x16
  |   [>] [icon] Projects        |    Section icon: 20x20
  |------------------------------|
  | PAGES (section label)        |
  |   [>] [icon] User Profile    |
  |   [>] [icon] Overview        |  10 items total
  |   [>] [icon] Projects        |
  |   [>] [icon] Campaigns       |
  |   [>] [icon] Documents       |
  |   [>] [icon] Followers       |
  |   [>] [icon] Shots           |
  |   [>] [icon] Resources       |
  |   [>] [icon] Tasks           |
  |   [>] [icon] Forms           |
  +------------------------------+
  | [SnowUI Logo]               |  Logo (180x36, p=8)
  +------------------------------+
```

### Header

```
Header (948 x 68, p=20/28, HORIZONTAL, SPACE_BETWEEN)
  +-----------------------------------------------+
  | [<][>] Dashboards / Default    [Search /] [4 icons] |
  +-----------------------------------------------+
```

| Element           | Size              | Details                              |
| ----------------- | ----------------- | ------------------------------------ |
| Nav arrows        | 24 x 24           | Back/forward buttons, p=4            |
| Breadcrumb        | 179 x 24          | "Dashboards / Default", gap=8        |
| Breadcrumb button | 93 x 24 / 65 x 24 | p=4/12, text 12px                    |
| Search            | 160 x 28          | p=4/8, gap=8, icon+text+"/" shortcut |
| Action icons      | 24 x 24 (x4)      | Star, notification, clock, settings  |

### Right Bar

```
Right Bar (280px wide, full height)
  padding: 16px, gap: 16px, VERTICAL
  +--------------------------------+
  | NOTIFICATIONS (section title)  |  (248x36, p=8/4)
  |   [icon-bg] Text  + timestamp  |  Row: 248x52, p=8, gap=8
  |   [icon-bg] Text  + timestamp  |  Icon bg: 24x24, r=4, accent color
  |   [icon-bg] Text  + timestamp  |  Title: 14px/400
  |   [icon-bg] Text  + timestamp  |  Time:  12px/400
  |--------------------------------|
  | ACTIVITIES (section title)     |
  |   [avatar] Text  + timestamp   |  Row: 248x52, p=8, gap=8
  |   [avatar] Text  + timestamp   |  Avatar: 24x24 circle
  |   [avatar] Text  + timestamp   |  Timeline strip: 1px vertical line
  |   [avatar] Text  + timestamp   |
  |   [avatar] Text  + timestamp   |
  |--------------------------------|
  | CONTACTS (section title)       |
  |   [avatar] Name                |  Row: 248x40, p=8, gap=8
  |   [avatar] Name                |  Avatar: 24x24 circle
  |   [avatar] Name                |  Name: 14px/400
  |   [avatar] Name                |
  |   [avatar] Name                |
  |   [avatar] Name                |
  +--------------------------------+
```

### Buttons

| Variant           | Size       | Padding         | Radius | Content                   |
| ----------------- | ---------- | --------------- | ------ | ------------------------- |
| Icon button       | 24 x 24    | 4 / 4 / 4 / 4   | 8      | 16px icon only            |
| Text button       | 65-93 x 24 | 4 / 12 / 4 / 12 | 8      | Text label                |
| Segmented control | 77 x 24    | 4 / 12 / 4 / 12 | 8      | "Favourites" / "Recently" |

### Tags & Tabs

| Component   | Size        | Padding | Details                |
| ----------- | ----------- | ------- | ---------------------- |
| `Tag`       | 76-81 x 20  | —       | Status indicators      |
| `Tap` (tab) | 77-112 x 20 | —       | Chart period selectors |

### Search Input

| Property   | Value                        |
| ---------- | ---------------------------- |
| Size       | 160 x 28                     |
| Padding    | 4 / 8 / 4 / 8                |
| Gap        | 8                            |
| Radius     | 8                            |
| BG (light) | `#0000000A` (black 4%)       |
| BG (dark)  | `#FFFFFF1A` (white 10%)      |
| Content    | [search-icon] "Search" ["/"] |

---

## 11. Responsive Breakpoints

| Breakpoint         | Canvas Size | Layout                                       |
| ------------------ | ----------- | -------------------------------------------- |
| Desktop (3-column) | 1440 x 1024 | Sidebar (212) + Content + Right Bar (280)    |
| Desktop (2-column) | 1440 x 1708 | Sidebar (220) + Content (1220), no Right Bar |
| Mobile             | 393 x 1767  | Full-width + Nav Bar (98) + Tab Bar (97)     |

### Mobile Components

| Component               | Size       |
| ----------------------- | ---------- |
| Navigation Bar (iPhone) | 393 x 98   |
| Content area            | 393 x 1572 |
| Tab Bar                 | 393 x 97   |

---

## 12. Design Tokens Summary (CSS Custom Properties)

```css
/* ===== LIGHT THEME ===== */
:root {
    /* Backgrounds */
    --bg-primary: #ffffff;
    --bg-secondary: #f9f9fa;
    --bg-subtle: rgba(0, 0, 0, 0.04);
    --bg-accent-purple: #edeefc;
    --bg-accent-blue: #e6f1fd;

    /* Text */
    --text-primary: #000000;
    --text-secondary: rgba(0, 0, 0, 0.4);
    --text-tertiary: rgba(0, 0, 0, 0.2);
    --text-disabled: rgba(0, 0, 0, 0.1);

    /* Borders */
    --border-default: rgba(0, 0, 0, 0.1);
    --border-strong: #000000;

    /* Accent */
    --accent-indigo: #4f507f;

    /* Surfaces */
    --surface-card: #f9f9fa;
    --surface-input: rgba(0, 0, 0, 0.04);
}

/* ===== DARK THEME ===== */
[data-theme='dark'] {
    /* Backgrounds */
    --bg-primary: #333333;
    --bg-secondary: rgba(255, 255, 255, 0.04);
    --bg-subtle: rgba(255, 255, 255, 0.1);
    --bg-accent-purple: #edeefc; /* unchanged */
    --bg-accent-blue: #e6f1fd; /* unchanged */

    /* Text */
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.4);
    --text-tertiary: rgba(255, 255, 255, 0.2);
    --text-disabled: rgba(255, 255, 255, 0.15);
    --text-on-accent: #000000;

    /* Borders */
    --border-default: rgba(255, 255, 255, 0.15);

    /* Surfaces */
    --surface-card: rgba(255, 255, 255, 0.04);
    --surface-input: rgba(255, 255, 255, 0.1);
}

/* ===== TYPOGRAPHY ===== */
:root {
    --font-family: 'Inter', sans-serif;

    --text-xl: 24px; /* line-height: 32px; font-weight: 600 */
    --text-base: 14px; /* line-height: 20px; font-weight: 400 | 600 */
    --text-sm: 12px; /* line-height: 16px; font-weight: 400 */
}

/* ===== SPACING ===== */
:root {
    --space-0-5: 2px;
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 20px;
    --space-6: 24px;
    --space-7: 28px;
    --space-10: 40px;
    --space-12: 48px;
}

/* ===== RADIUS ===== */
:root {
    --radius-xs: 4px;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --radius-2xl: 24px;
    --radius-full: 80px;
}

/* ===== LAYOUT ===== */
:root {
    --sidebar-width: 212px;
    --header-height: 68px;
    --right-bar-width: 280px;
    --content-gap: 28px;
    --card-padding: 24px;
    --card-radius: 20px;
    --section-padding: 16px;
}
```

---

## 13. Component Quick Reference

| Component             | Size (WxH) | BG        | Radius | Padding | Gap | Layout     |
| --------------------- | ---------- | --------- | ------ | ------- | --- | ---------- |
| Stat Card             | 202 x 112  | accent    | 20     | 24      | 8   | VERTICAL   |
| Content Block         | varies     | secondary | 20     | 24      | 16  | VERTICAL   |
| Sidebar Item          | 180 x 36   | —         | —      | 8       | 4   | HORIZONTAL |
| Sidebar Section Label | 180 x 28   | —         | —      | 4/12    | —   | VERTICAL   |
| Notification Row      | 248 x 52   | —         | —      | 8       | 8   | HORIZONTAL |
| Activity Row          | 248 x 52   | —         | —      | 8       | 8   | HORIZONTAL |
| Contact Row           | 248 x 40   | —         | —      | 8       | 8   | HORIZONTAL |
| Icon Button           | 24 x 24    | —         | 8      | 4       | —   | HORIZONTAL |
| Text Button           | ~80 x 24   | —         | 8      | 4/12    | 4   | HORIZONTAL |
| Search Input          | 160 x 28   | subtle    | 8      | 4/8     | 8   | HORIZONTAL |
| Avatar                | 24 x 24    | —         | 80     | —       | —   | —          |
| Breadcrumb            | 179 x 24   | —         | —      | —       | 8   | HORIZONTAL |
| Tag                   | ~80 x 20   | —         | 8      | —       | —   | —          |

---

## 14. Notification & Activity Patterns

### Notification Item

```
[icon-container 24x24, bg=accent, r=4, p=4]  [text-group]
  [16x16 icon]                                   [title 14px/400 primary]
                                                  [time  12px/400 secondary]
```

### Activity Item

```
[avatar 24x24, circle]  [text-group]               [timeline-strip]
                           [action 14px/400 primary]    [1px line, 16.5px segments]
                           [time   12px/400 secondary]
```

### Contact Item

```
[avatar 24x24, circle]  [name 14px/400 primary]
```

---

## 15. Chart & Data Visualization

### Chart Containers

All charts live inside Content Blocks with:

- Title bar: 14px/600 SemiBold, with optional period tabs ("This year" / "Last year")
- Chart area: `ChartMotion` component (animated)
- Y-axis labels: 0, 10K, 20K, 30K

### Donut Charts

- Small indicator: 28 x 33
- Medium: ~60 x 60
- Large: 120 x 120
- Used in "Traffic by Website" block alongside percentage list

### Horizontal Bars

- `HorizontalBar 03`: 80 x 34
- Used for percentage breakdowns (Google, YouTube, etc.)

---

## 16. Key Design Decisions

1. **No shadows** — Elevation is communicated through background color shifts only
2. **Alpha-based theming** — Single base color (black or white) at varying opacities, rather than named semantic colors
3. **Accent colors persist** — `#EDEEFC` and `#E6F1FD` are theme-invariant; text on them is always `#000000`
4. **Single font** — Inter at 3 sizes (12, 14, 24) and 2 weights (400, 600)
5. **4px grid** — All spacing values (except 2px) are multiples of 4
6. **Consistent padding** — Cards/blocks use 24px uniform padding; list items use 8px
7. **Flat design language** — Background blur (40px) is the only non-trivial effect
8. **Component-first** — 56+ unique components, 280+ instances; highly reusable design system
