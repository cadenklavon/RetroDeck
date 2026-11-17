# RetroDeck Development Roadmap

Items are marked complete only when implemented. Raspberry Pi hardware validation is tracked separately from implementation.

## Stage 1: UI foundation
- [x] PySide6 desktop window and navigation
- [x] Home, Library, Systems, Search, and Settings pages
- [x] Dark/light theme toggle
- [x] Console-inspired wide-screen visual design
- [x] Keyboard shortcuts for page navigation
- [x] Initial launch confirmed on the user's Raspberry Pi 5
- [ ] Test layout and readability on the Raspberry Pi 7-inch display and a 16:9 monitor
- [ ] Refine visual design after testing on actual hardware

## Stage 2: Game library
- [x] Define a game metadata model
- [x] Let users configure ROM directories
- [x] Scan supported file extensions without moving user files
- [x] Group detected games by system
- [x] Search and filter detected games
- [x] Sort scan results consistently
- [x] Deduplicate files when folders overlap
- [x] Report missing or invalid folders
- [x] Add automated tests for scanner behavior
- [ ] Favorites and recently played
- [ ] Handle multi-disc games and per-folder system overrides

## Stage 3: Emulator integration
- [ ] Define configurable emulator profiles
- [ ] Allow executable path and launch arguments to be configured
- [ ] Launch a selected game in an external emulator
- [ ] Report missing emulator paths and launch errors
- [ ] Support per-system defaults and optional per-game overrides
- [ ] Test Mupen64Plus and Dolphin on Raspberry Pi OS

## Stage 4: Controller support
- [ ] Detect connected game controllers
- [ ] Add configurable input mapping
- [ ] Make all key actions accessible without a mouse
- [ ] Test navigation and selection with an Xbox controller
- [ ] Handle controller disconnect/reconnect

## Stage 5: Artwork, metadata, and persistence
- [ ] Support local cover images first
- [ ] Adapt artwork presentation to image dimensions
- [ ] Review terms before adding optional metadata providers
- [ ] Cache artwork locally
- [ ] Add SQLite database and schema migrations
- [ ] Persist favorites and play history
- [ ] Add backup/export for settings

## Stage 6: Raspberry Pi testing and release preparation
- [ ] Document supported Raspberry Pi OS versions
- [ ] Provide a clean installation guide
- [ ] Add automated tests and basic CI
- [ ] Test performance and usability on Raspberry Pi 5
- [ ] Add screenshots of the real application
- [ ] Choose and add an open-source license, if desired
