# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3] - 2024-06-28
### Changed
- Use websockets instead of http
- Transition to using FastAPI from Flask

### Removed
- Removed MessagePack for now.

## [0.2] - 2022-11-05
### Added
- Using MessagePack for seralization of data
- Using REST server with flask
- API to stream offline data

### Removed
- Phidget data streaming
