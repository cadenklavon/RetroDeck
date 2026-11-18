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

## Stage 3: Emulator integration and packaging
- [x] Create a central catalog of standalone emulator candidates
- [x] Define default emulator mappings for detected systems
- [x] Search configured paths, architecture-specific and legacy bundle folders, Debian game directories, and system PATH
- [x] Add a modular process launcher with configurable argument templates
- [x] Add unit tests for executable discovery and launch command construction
- [x] Document the platform-specific packaging and first-run installation design
- [x] Start third-party license and redistribution tracking
- [ ] Select exact standalone emulator releases for each supported system
- [ ] Verify licenses, bundled dependencies, notices, and source obligations for every selected build
- [ ] Build and test Mupen64Plus for Raspberry Pi OS ARM64
- [ ] Test Dolphin installed from the Debian ARM64 package on Raspberry Pi 5
- [ ] Test mGBA and Nestopia installed from Debian ARM64 packages
- [ ] Select and validate standalone SNES, DS, and PSP emulators
- [ ] Create reproducible ARM64 build scripts and release assets
- [x] Add a versioned package manifest structure and SHA-256 verification engine\n- [x] Add safe archive extraction and per-user versioned emulator storage
- [x] Add an emulator setup/status page backed by the managed package catalog
- [x] Publish the first checksum-pinned official Raspberry Pi OS ARM64 package (melonDS 1.1)
- [x] Add automatic missing-package checks during startup
- [x] Add background package downloads and an installation progress indicator
- [ ] Validate melonDS AppImage launch and runtime dependencies on Raspberry Pi 5
- [ ] Add more verified ARM64 packages, then implement update, repair, rollback, and removal
- [x] Connect selected games in the Library page to the emulator launcher
- [ ] Test real games and report missing firmware or runtime dependencies

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
- [ ] Choose and add an open-source license for RetroDeck, if desired
