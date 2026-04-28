# Docscriptor Working Notes

This file is the shared memory for ongoing work on this repository. Keep it readable for the project owner, future Codex sessions, and other LLMs.

## Operating Rule

- Continue updating this file as the project evolves. Record design philosophy, API direction, compatibility rules, and decisions that future work should remember.
- Prefer explicit, author-friendly APIs over hidden magic. Docscriptor should feel like writing a document in Python, not like configuring a renderer.
- Keep one source document renderable to DOCX, PDF, and HTML. New components should define behavior for all supported renderers or clearly document limitations.
- Preserve existing examples and tests unless a user explicitly asks to change the public behavior.
- When adding a feature, update tests and examples enough that another contributor can see the intended usage.

## Current Direction

- The project builds structured documents from Python objects and exports them to DOCX, PDF, and HTML.
- Journal-style and usage-guide examples are important living specifications. They should stay realistic and readable.
- Cross-renderer consistency matters more than perfect renderer-specific fidelity.

## User Requests To Remember

- Keep this shared note file and include the instruction to keep updating it.
- Add page color support.
- Add an explicit page break feature. Possible names discussed: `break_page` method or `PageBreaker()` instance. Prefer an object component if it fits the existing block model.
- Add unit support beyond inches, including centimeters. Objects should support units locally, and the whole document should also be able to set an overall unit. If that exists, arguments such as `width_inches` can move toward clearer `width` names.

## API Compatibility Notes

- Existing names such as `width_inches` should remain usable while introducing newer, unit-aware names.
- Prefer document-level defaults through `DocumentSettings` so authors can make unit choices once and still override locally where needed.
