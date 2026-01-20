# Equal Experts Brand Style Guide for Web Applications

This guide provides all the information needed to style web applications according to Equal Experts brand guidelines.

---

## Colours

### Primary Palette

| Name | Hex | RGB | CSS Variable Suggestion |
|------|-----|-----|------------------------|
| **Equal Experts Blue** (Primary) | `#1795D4` | rgb(23, 149, 212) | `--ee-blue` |
| **Tech Blue** (Dark Blue) | `#22567C` | rgb(34, 86, 124) | `--ee-tech-blue` |
| **Transform Teal** | `#269C9E` | rgb(38, 156, 158) | `--ee-teal` |
| **Equal Ember** (Orange/Accent) | `#F07C00` | rgb(240, 124, 0) | `--ee-ember` |

### Neutral Palette

| Name | Hex | RGB | CSS Variable Suggestion |
|------|-----|-----|------------------------|
| **Dark Data** (Near Black) | `#212526` | rgb(33, 37, 38) | `--ee-dark` |
| **The Cloud** (Light Grey) | `#F5F5F5` | rgb(245, 245, 245) | `--ee-cloud` |
| **Byte White** | `#FFFFFF` | rgb(255, 255, 255) | `--ee-white` |

### CSS Variables Template

```css
:root {
  /* Primary colours */
  --ee-blue: #1795D4;
  --ee-tech-blue: #22567C;
  --ee-teal: #269C9E;
  --ee-ember: #F07C00;

  /* Neutral colours */
  --ee-dark: #212526;
  --ee-cloud: #F5F5F5;
  --ee-white: #FFFFFF;
}
```

---

## Typography

### Font Family

**Lexend** - A clean, accessible font designed to reduce visual stress and improve reading performance for everyone, including those with dyslexia.

```css
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;700&display=swap');

:root {
  --font-family: 'Lexend', sans-serif;
}

body {
  font-family: var(--font-family);
}
```

### Font Weights

| Weight | Name | Usage |
|--------|------|-------|
| 300 | Light | Body text on websites, paragraphs, links |
| 400 | Normal/Regular | Section titles, body copy, general text |
| 500 | Medium | H2 headings, emphasis |
| 700 | Bold | Strong emphasis, CTAs, key facts |

### Typography Scale - Documents & Slides

| Element | Font | Size | Colour | Spacing |
|---------|------|------|--------|---------|
| Section Title | Lexend Normal | 12pt | EE Blue `#1795D4` | Single |
| Main Heading | Lexend Normal | 22pt | Tech Blue `#22567C` | Single |
| Body Copy | Lexend Normal | 10pt min | Dark Data `#212526` | 1.15 |

### Typography Scale - Website

| Element | Font Weight | Size (px/pt) | Colour |
|---------|-------------|--------------|--------|
| H1 | Normal (400) | 45px / 34pt | White on EE Blue background |
| H2 | Medium (500) | 24px / 18pt | EE Blue `#1795D4` |
| H3 | Normal (400) | 40px / 30pt | Tech Blue `#22567C` |
| H4 | Normal (400) | 24px / 18pt | Tech Blue `#22567C` |
| Paragraph | Light (300) | 19px / 14pt | Dark Data `#212526` |
| Link | Light (300) | 19px / 14pt | Tech Blue `#22567C`, underlined |
| Pull Quote | Light (300) | 36px / 27pt | - |
| Attribution | Light (300) | 20px / 15pt | - |

### CSS Typography Example

```css
h1 {
  font-family: var(--font-family);
  font-weight: 400;
  font-size: 45px;
  color: var(--ee-white);
  background-color: var(--ee-blue);
}

h2 {
  font-family: var(--font-family);
  font-weight: 500;
  font-size: 24px;
  color: var(--ee-blue);
  text-transform: uppercase;
}

h3 {
  font-family: var(--font-family);
  font-weight: 400;
  font-size: 40px;
  color: var(--ee-tech-blue);
}

h4 {
  font-family: var(--font-family);
  font-weight: 400;
  font-size: 24px;
  color: var(--ee-tech-blue);
}

p {
  font-family: var(--font-family);
  font-weight: 300;
  font-size: 19px;
  line-height: 1.15;
  color: var(--ee-dark);
}

a {
  font-family: var(--font-family);
  font-weight: 300;
  font-size: 19px;
  color: var(--ee-tech-blue);
  text-decoration: underline;
}
```

---

## Accessibility - Colour Combinations

Equal Experts aims to meet WCAG AA accessibility standards:
- **4.5:1** contrast ratio for normal text
- **3:1** contrast ratio for large text (Bold 14pt/19px+ or Normal 18pt/24px+)

### Approved Colour Combinations

#### On Dark Data (`#212526`) Background
| Text Colour | Usage |
|-------------|-------|
| White `#FFFFFF` | ✅ Normal & Large text |
| Light Grey `#F5F5F5` | ✅ Normal & Large text |
| EE Blue `#1795D4` | ✅ Normal & Large text |
| Ember `#F07C00` | ✅ Normal & Large text |
| Teal `#269C9E` | ✅ Normal & Large text |

#### On The Cloud (`#F5F5F5`) / White Background
| Text Colour | Usage |
|-------------|-------|
| Black `#212526` | ✅ Normal & Large text |
| Tech Blue `#22567C` | ✅ Normal & Large text |
| EE Blue `#1795D4` | ⚠️ Large text only |
| Teal `#269C9E` | ⚠️ Large text only |

#### On EE Blue (`#1795D4`) Background
| Text Colour | Usage |
|-------------|-------|
| Black `#212526` | ✅ Large text only |
| White `#FFFFFF` | ✅ Large text only |
| Light Grey `#F5F5F5` | ✅ Large text only |

#### On Tech Blue (`#22567C`) Background
| Text Colour | Usage |
|-------------|-------|
| White `#FFFFFF` | ✅ Normal & Large text |
| Light Grey `#F5F5F5` | ✅ Normal & Large text |

#### On Transform Teal (`#269C9E`) Background
| Text Colour | Usage |
|-------------|-------|
| Black `#212526` | ✅ Normal & Large text |
| White `#FFFFFF` | ✅ Large text only |
| Light Grey `#F5F5F5` | ✅ Large text only |

#### On Equal Ember (`#F07C00`) Background
| Text Colour | Usage |
|-------------|-------|
| Black `#212526` | ✅ Normal & Large text |

---

## Logo

### Brand Mark

The Equal Experts logo consists of:
- **Brand mark**: Square brackets containing an equals sign `[=]`
- **Word mark**: "EQUAL EXPERTS" text

### Logo Usage Rules

**DO:**
- Use the full colour logo on white or light backgrounds
- Use monochrome (black or white) versions when needed for contrast
- Maintain minimum width of **100px (26.5mm)**
- Provide clear space around the logo equal to the width of one bracket and equals sign

**DON'T:**
- ❌ Rotate any part of the logo
- ❌ Distort or skew the logo
- ❌ Change the layout of the logo
- ❌ Change the transparency
- ❌ Use different colours
- ❌ Use the word mark alone (without the brand mark)
- ❌ Recreate with a different font
- ❌ Use shadows or other effects
- ❌ Add extra words to the logo
- ❌ Use on busy backgrounds

### Brand Mark Only

The brand mark `[=]` alone can be used when:
- Space is limited
- Logo must fit in a square or circle
- Used as a design element on presentations

### Logo Colours

| Version | Brand Mark | Text |
|---------|-----------|------|
| Full Colour | EE Blue `#1795D4` | Dark Data `#212526` |
| Monochrome Light | White `#FFFFFF` | White `#FFFFFF` |
| Monochrome Dark | Black `#212526` | Black `#212526` |

---

## Component Styling Suggestions

### Buttons

```css
/* Primary Button */
.btn-primary {
  background-color: var(--ee-blue);
  color: var(--ee-white);
  font-family: var(--font-family);
  font-weight: 400;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
}

.btn-primary:hover {
  background-color: var(--ee-tech-blue);
}

/* Secondary Button */
.btn-secondary {
  background-color: var(--ee-white);
  color: var(--ee-tech-blue);
  font-family: var(--font-family);
  font-weight: 400;
  padding: 12px 24px;
  border: 2px solid var(--ee-tech-blue);
  border-radius: 4px;
}

/* Accent Button */
.btn-accent {
  background-color: var(--ee-ember);
  color: var(--ee-dark);
  font-family: var(--font-family);
  font-weight: 700;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
}
```

### Cards

```css
.card {
  background-color: var(--ee-white);
  border-left: 4px solid var(--ee-blue);
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-family: var(--font-family);
  font-weight: 400;
  font-size: 24px;
  color: var(--ee-tech-blue);
  margin-bottom: 12px;
}

.card-body {
  font-family: var(--font-family);
  font-weight: 300;
  font-size: 16px;
  color: var(--ee-dark);
  line-height: 1.5;
}
```

### Section Headers

```css
.section-label {
  font-family: var(--font-family);
  font-weight: 500;
  font-size: 14px;
  color: var(--ee-blue);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.section-title {
  font-family: var(--font-family);
  font-weight: 400;
  font-size: 32px;
  color: var(--ee-tech-blue);
}
```

### Hero Section

```css
.hero {
  background-color: var(--ee-blue);
  padding: 80px 40px;
}

.hero-title {
  font-family: var(--font-family);
  font-weight: 400;
  font-size: 45px;
  color: var(--ee-white);
}

.hero-subtitle {
  font-family: var(--font-family);
  font-weight: 300;
  font-size: 20px;
  color: var(--ee-white);
}
```

### Quote Block

```css
.quote-block {
  background-color: var(--ee-tech-blue);
  padding: 48px;
  position: relative;
}

.quote-block::before {
  content: '"';
  font-family: var(--font-family);
  font-size: 120px;
  color: var(--ee-blue);
  position: absolute;
  top: 0;
  left: 24px;
  line-height: 1;
}

.quote-text {
  font-family: var(--font-family);
  font-weight: 300;
  font-size: 24px;
  color: var(--ee-white);
  font-style: normal;
}

.quote-attribution {
  font-family: var(--font-family);
  font-weight: 300;
  font-size: 16px;
  color: var(--ee-white);
  margin-top: 24px;
}
```

---

## Complete CSS Variables Template

```css
:root {
  /* Colours - Primary */
  --ee-blue: #1795D4;
  --ee-tech-blue: #22567C;
  --ee-teal: #269C9E;
  --ee-ember: #F07C00;

  /* Colours - Neutral */
  --ee-dark: #212526;
  --ee-cloud: #F5F5F5;
  --ee-white: #FFFFFF;

  /* Typography */
  --font-family: 'Lexend', sans-serif;

  /* Font Sizes */
  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 16px;
  --text-lg: 19px;
  --text-xl: 24px;
  --text-2xl: 32px;
  --text-3xl: 40px;
  --text-4xl: 45px;

  /* Font Weights */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.15;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  --spacing-3xl: 64px;

  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(33, 37, 38, 0.1);
  --shadow-md: 0 2px 4px rgba(33, 37, 38, 0.1);
  --shadow-lg: 0 4px 8px rgba(33, 37, 38, 0.15);
}
```

---

## Tailwind CSS Configuration

If using Tailwind CSS, add these to your `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'ee-blue': '#1795D4',
        'ee-tech-blue': '#22567C',
        'ee-teal': '#269C9E',
        'ee-ember': '#F07C00',
        'ee-dark': '#212526',
        'ee-cloud': '#F5F5F5',
      },
      fontFamily: {
        'lexend': ['Lexend', 'sans-serif'],
      },
    },
  },
}
```

---

## Quick Reference

| Element | Colour | Font |
|---------|--------|------|
| Primary brand colour | `#1795D4` (EE Blue) | - |
| Headings | `#22567C` (Tech Blue) | Lexend 400/500 |
| Body text | `#212526` (Dark Data) | Lexend 300 |
| Links | `#22567C` (Tech Blue) | Lexend 300, underlined |
| Accent/CTA | `#F07C00` (Ember) | Lexend 700 |
| Background light | `#F5F5F5` (Cloud) | - |
| Background dark | `#22567C` (Tech Blue) | - |

---

*Based on Equal Experts Brand Guidelines - Logo, Colours, and Typography*

