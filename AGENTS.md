# Project Guidelines

## Project

Academic project for Práctica Profesional I (IFTS N.º 18): "Aproximación al campo laboral — Proyecto Parcial".

The main deliverable is a polished presentation about the day-to-day work of a Full Stack Freelance Developer, built with Reveal.js. A Python-based remote controller for controlling slides from a phone over the local network is a future component.

## General Rules

* Inspect the existing repository before making changes.
* Preserve the existing Reveal.js installation and its license.
* Do not replace, delete, or reorganize existing files without a clear reason.
* Prefer simple, maintainable solutions over unnecessary abstractions or dependencies.
* Explain the plan before making substantial changes.
* Implement incrementally and verify changes after each step.
* Do not add dependencies unless they provide clear value.
* Keep custom presentation code separate from the Reveal.js framework.
* Do not commit changes unless explicitly requested.

## Presentation

* Keep custom slides in `presentation/slides/`.
* Keep custom styles in `presentation/styles/`.
* Treat `presentation/reveal.js/` as the existing framework source.
* Aim for a modern, coherent, accessible, responsive visual design.
* Keep slide content concise and suitable for an oral presentation.

## Future Remote Controller

* Keep the controller separate from the presentation implementation.
* Use Python for the backend and a mobile-friendly web interface for the phone.
* Consider FastAPI and WebSockets for local-network communication.
* Do not implement this component until explicitly requested.
* Do not introduce Bluetooth or other communication methods in the initial version.

## Working Style

* Before coding, summarize the repository structure and propose the next steps.
* Ask before making decisions that substantially change the architecture or scope.
* Report which files were changed and how the changes were verified.

