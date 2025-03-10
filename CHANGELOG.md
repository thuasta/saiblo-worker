# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.4.0] - 2025-03-10

### Added

- Build timeout configuration.

## [0.3.2] - 2025-03-09

### Fixed

- Ambiguous game host timeout message.
- Wrong judge result status when agents are forced to stop.

## [0.3.1] - 2025-03-09

### Fixed

- Ambiguous judge result status.
- Redundant build task calls.
- Disconnecting from Saiblo when waiting for Docker run.

## [0.3.0] - 2025-02-09

### Changed

- Use host Docker socket for agent containers.

## [0.2.1] - 2025-02-09

### Fixed

- Requesting judge tasks before scheduling last ones.

## [0.2.0] - 2025-02-09

### Changed

- Use ghcr.io/futrime/docker-python:27.5-py3.13 as base image.

## [0.1.1] - 2025-02-08

### Fixed

- Not notifying Saiblo that a judge task is done.

## [0.1.0] - 2025-02-07

First version

[0.4.0]: https://github.com/thuasta/saiblo-worker/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/thuasta/saiblo-worker/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/thuasta/saiblo-worker/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/thuasta/saiblo-worker/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/thuasta/saiblo-worker/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/thuasta/saiblo-worker/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/thuasta/saiblo-worker/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/thuasta/saiblo-worker/releases/tag/v0.1.0
