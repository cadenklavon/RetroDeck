# RetroDeck Development Roadmap

This roadmap describes planned work. Items are not complete until implemented and tested.

## Phase 1: UI foundation
- [x] Initial PySide6 window and navigation prototype
- [x] Home, Library, Consoles, Search, and Settings destinations
- [x] Dark/light theme toggle
- [ ] Modularize pages and reusable components
- [ ] Add focus states and keyboard/controller navigation
- [ ] Add responsive layout for 16:9 displays

## Phase 2: Game library
- [ ] Define a game metadata model
- [ ] Let users configure ROM directories
- [ ] Scan supported file extensions without moving user files
- [ ] Group games by system
- [ ] Search, sort, and filter the library
- [ ] Favorites and recently played

## Phase 3: Emulator integration
- [ ] Define configurable emulator profiles
- [ ] Allow executable path and launch arguments to be configured
- [ ] Launch a selected game in an external emulator
- [ ] Report missing emulator paths and launch errors
- [ ] Support per-system defaults and optional per-game overrides

## Phase 4: Artwork and metadata
- [ ] Support local cover images first
- [ ] Adapt artwork presentation to image dimensions
- [ ] Review terms before adding optional metadata providers
- [ ] Cache artwork locally
- [ ] Provide a fallback when artwork is missing

## Phase 5: Persistence and settings
- [ ] Add SQLite database and schema migrations
- [ ] Persist library settings, favorites, and play history
- [ ] Add backup/export for settings
- [ ] Add theme and interface preferences

## Phase 6: Controller support and polish
- [ ] Detect connected game controllers
- [ ] Add configurable input mapping
- [ ] Make key actions accessible without a mouse
- [ ] Add loading, empty, and error states
- [ ] Test performance and usability on Raspberry Pi 5

## Phase 7: Release preparation
- [ ] Document supported Raspberry Pi OS versions
- [ ] Provide an installation guide
- [ ] Add automated tests and basic CI
- [ ] Add screenshots of the real application
- [ ] Choose and add an open-source license, if desired
