# RetroDeck Development Roadmap

This roadmap describes planned work. Items are not complete until implemented and tested.

## Stage 1: UI design
- [x] Initial PySide6 window and navigation prototype
- [x] Home, Library, Systems, Search, and Settings destinations
- [x] Dark/light theme toggle
- [x] Console-inspired wide-screen visual design
- [x] Sample game tiles and sample-library filtering
- [x] Basic keyboard shortcuts for page navigation
- [ ] Test layout and readability on the Raspberry Pi 7-inch display and a 16:9 monitor
- [ ] Refine visual design after testing on actual hardware

## Stage 2: Game library
- [ ] Define a game metadata model
- [ ] Let users configure ROM directories
- [ ] Scan supported file extensions without moving user files
- [ ] Group games by system
- [ ] Search, sort, and filter detected games
- [ ] Favorites and recently played
- [ ] Handle duplicate filenames and missing files cleanly

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
- [ ] Persist library settings, favorites, and play history
- [ ] Add backup/export for settings

## Stage 6: Raspberry Pi testing and release preparation
- [ ] Document supported Raspberry Pi OS versions
- [ ] Provide a clean installation guide
- [ ] Add automated tests and basic CI
- [ ] Test performance and usability on Raspberry Pi 5
- [ ] Add screenshots of the real application
- [ ] Choose and add an open-source license, if desired
