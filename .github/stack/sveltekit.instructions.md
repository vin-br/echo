---
description: 'SvelteKit coding conventions and guidelines.'
applyTo: 'frontend/**'
---

# SvelteKit Guidelines

## Philosophy
No abstractions without need, no files without purpose.

## Stack
- **Bun**: Package manager (`bun install`, `bun add`, `bun run`) — never npm or yarn
- **Svelte 5**: Use runes (`$state`, `$derived`, `$effect`, `$props`) — no legacy Options API
- **TypeScript**: Always

## Code Standards
- Prefer `$derived` over `$effect` for computed values
- Co-locate component logic and markup; extract only when reused
- Use SvelteKit file conventions: `+page.svelte`, `+layout.svelte`, `+server.ts`
- Fetch data in `load()` functions, not inside components

## Styling
- 8-point grid: all spacing, padding, and margin must be multiples of 8px (8, 16, 24, 32…) — does not apply to font sizes
- 4-point exception: use 4px (`--space-xs`) when space is limited or intentionally compact (e.g., tight gaps within components, inline separations). Prefer the 8-point grid unless 8px is visually too large.
- Scoped `<style>` blocks; no global styles except in `app.css`
