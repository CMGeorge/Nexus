# ADR-0013: Desktop App — Qt/QML with MVVM Architecture

## Status
Accepted

## Date
2026-07-16

## Context
Nexus needs a desktop application for field technicians and business managers who work from laptops/desktops rather than mobile devices. The desktop app must:

1. **Run natively** on Windows, macOS, and Linux — our target market (Romanian service businesses) uses all three
2. **Work offline** — technicians in basements, rural areas, or buildings with poor connectivity must still see their schedule and complete jobs
3. **Sync when online** — queue changes locally, push when connectivity returns
4. **Feel native** — not a web wrapper; proper native menus, system tray, notifications
5. **Match mobile parity** — same features as iOS/Android apps, plus desktop-only features (bulk operations, keyboard shortcuts, multi-window)
6. **Integrate with REST API** — same backend as web and mobile; no separate backend

## Decision
**Build the desktop app with Qt 6.11 LTS, QML for UI, C++17 for business logic, using the MVVM architectural pattern.**

### Tech Stack
| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **UI** | QML (Qt Quick) | Declarative, data-binding to C++ properties, hardware-accelerated rendering |
| **Business Logic** | C++17 | Type-safe, performant, direct interop with Qt framework |
| **Architecture** | MVVM (Model-View-ViewModel) | Qt's `Q_PROPERTY` + signal/slot is purpose-built for MVVM |
| **HTTP** | Qt Network (`QNetworkAccessManager`) | Native, async, TLS support, cookie/redirect handling |
| **Local DB** | SQLite via Qt SQL (`QSqlDatabase`) | Zero-config, embedded, battle-tested offline store |
| **Build** | CMake 3.21+ | Cross-platform, Qt's first-class build system |
| **Package** | Qt Installer Framework / AppImage / MSIX | Platform-native distribution |

### MVVM Architecture
```
┌─────────────────────────────────────────────────────────┐
│  QML Views (Declarative UI)                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │ LoginPage│ │ JobsPage │ │ DetailPg │  ...            │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘                │
│       │ bind to      │           │                       │
├───────┼──────────────┼───────────┼───────────────────────┤
│  C++ ViewModels (State + Commands)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │LoginVM   │ │ JobsVM   │ │ DetailVM │  ...            │
│  │ Q_PROPERTY│ │ Q_PROPERTY│ │ Q_PROPERTY│              │
│  │ signals:  │ │ signals:  │ │ signals:  │              │
│  │ slots:    │ │ slots:    │ │ slots:    │              │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘                │
│       │ call         │           │                       │
├───────┼──────────────┼───────────┼───────────────────────┤
│  C++ Repositories (Data Access)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │AuthRepo  │ │ JobsRepo │ │CacheRepo │  ...            │
│  │ REST API │ │ REST API │ │ SQLite   │                 │
│  └──────────┘ └──────────┘ └──────────┘                │
└─────────────────────────────────────────────────────────┘
```

- **QML Views**: Pure declarative UI, no business logic. Bind to ViewModel properties via `Binding` and `Connections`.
- **C++ ViewModels**: Expose state via `Q_PROPERTY`, handle user actions via `public slots:`. Emit signals when state changes. QML automatically re-renders bound properties.
- **Repositories**: Stateless classes that call the REST API (via `QNetworkAccessManager`) or local SQLite. ViewModels own and call them.

### Offline-First with SQLite
```
┌──────────────────────────────────────────────────────────┐
│  Write Path (always local first)                         │
│  User action → ViewModel slot → write to SQLite           │
│                                → push to API (if online)  │
│                                → queue in outbox (if off) │
│                                                           │
│  Read Path (local cache, server as source of truth)      │
│  ViewModel init → read from SQLite (instant)              │
│                → fetch from API in background             │
│                → update SQLite + emit signal if changed   │
│                                                           │
│  Sync Engine                                              │
│  ConnectivityMonitor (QNetworkInformation)                │
│    → online: drain outbox queue (FIFO)                    │
│    → offline: queue writes, show sync badge               │
│  Conflict resolution: last-write-wins with server         │
│    timestamps (acceptable for scheduling use case)        │
└──────────────────────────────────────────────────────────┘
```

### Project Structure
```
desktop/
├── CMakeLists.txt              # Top-level CMake
├── src/
│   ├── main.cpp                # QApplication, engine setup
│   ├── app/
│   │   ├── AppEngine.h/cpp     # QML context, ViewModel registry
│   │   └── Navigation.h/cpp    # Stack-based navigation controller
│   ├── viewmodels/             # One ViewModel per screen
│   │   ├── LoginViewModel.h/cpp
│   │   ├── JobsViewModel.h/cpp
│   │   ├── JobDetailViewModel.h/cpp
│   │   ├── AppointmentsViewModel.h/cpp
│   │   ├── CustomersViewModel.h/cpp
│   │   ├── InvoicesViewModel.h/cpp
│   │   ├── TasksViewModel.h/cpp
│   │   ├── ChatViewModel.h/cpp
│   │   └── SettingsViewModel.h/cpp
│   ├── repositories/           # REST API + local DB access
│   │   ├── AuthRepository.h/cpp
│   │   ├── JobsRepository.h/cpp
│   │   ├── CacheRepository.h/cpp    # SQLite wrapper
│   │   └── SyncEngine.h/cpp         # Offline queue + drain
│   ├── models/                 # Plain C++ data structs
│   │   ├── Job.h
│   │   ├── Appointment.h
│   │   ├── Customer.h
│   │   ├── Invoice.h
│   │   └── User.h
│   └── network/
│       ├── ApiClient.h/cpp     # QNetworkAccessManager wrapper
│       ├── AuthInterceptor.h/cpp   # JWT attach + refresh
│       └── TenantInterceptor.h/cpp # X-Tenant-ID header
├── qml/                        # QML views
│   ├── main.qml                # ApplicationWindow + StackView
│   ├── pages/
│   │   ├── LoginPage.qml
│   │   ├── DashboardPage.qml
│   │   ├── JobsPage.qml
│   │   ├── JobDetailPage.qml
│   │   ├── AppointmentsPage.qml
│   │   ├── CustomersPage.qml
│   │   ├── InvoicesPage.qml
│   │   ├── TasksPage.qml
│   │   ├── ChatPage.qml
│   │   └── SettingsPage.qml
│   └── components/             # Reusable QML components
│       ├── StatusBadge.qml
│       ├── SearchBar.qml
│       ├── DataTable.qml
│       └── ToastNotification.qml
├── resources/
│   ├── icons/                  # SVG icons (from Hallmark design)
│   ├── fonts/                  # DM Serif Display, Figtree
│   └── qml.qrc                # Qt resource file
└── tests/
    ├── CMakeLists.txt
    ├── tst_JobsViewModel.cpp
    ├── tst_ApiClient.cpp
    └── tst_SyncEngine.cpp
```

## Rationale

### Why Qt/QML over Electron?
| Factor | Qt/QML | Electron |
|--------|--------|----------|
| **Startup time** | <1s (native binary) | 3-8s (Chromium + Node.js) |
| **Memory (idle)** | ~50MB | ~250MB+ |
| **Offline DB** | SQLite via Qt SQL (native, fast) | SQLite via better-sqlite3 (JS wrapper, slower) |
| **Native feel** | Platform-native rendering, menus, tray | Chromium wrapper, feels like a web page |
| **Distribution** | ~30MB binary (compiled) | ~150MB+ (bundled Chromium) |
| **Battery** | Native GPU rendering, efficient | Chromium rendering, significant drain |
| **Romanian market** | Works on older hardware | Struggles on 4GB RAM laptops common in RO |

Electron has a larger developer pool, but Nexus is targeting field workers on varied hardware. Qt's efficiency and native feel are non-negotiable for this audience.

### Why Qt over Flutter Desktop?
- Flutter Desktop is still immature for Linux (our technician target). Qt has 25+ years on Linux.
- Qt provides native OS integration (system tray, notifications, file dialogs) without plugins.
- Flutter uses Skia for rendering — it draws every pixel itself, which means non-native text selection, scrolling physics, and accessibility.

### Why Qt over .NET MAUI?
- MAUI is Windows-first; macOS/Linux support is community-driven and incomplete.
- Romanian businesses are split ~60% Windows / 30% macOS / 10% Linux. Qt covers all three equally.
- MAUI's XAML binding is less ergonomic than QML's JavaScript-like property binding.

### Why MVVM over MVC/MVP?
- Qt's signal/slot mechanism is MVVM-native: `Q_PROPERTY` notifies → QML auto re-renders.
- MVC requires controllers to manually push updates to views — extra boilerplate.
- MVVM allows designers to work on QML independently from C++ ViewModel logic.
- No need for a separate "Controller" layer — QML handles user input directly, ViewModels handle commands.

### Why C++17 over C++20/23?
- Qt 6.11 LTS officially supports C++17 as the recommended standard.
- C++17 features (`std::optional`, `std::variant`, structured bindings, `if constexpr`) are sufficient.
- C++20 modules are not yet well-supported in CMake + Qt builds (as of 2026).

## Consequences

### Positive
- **True native performance**: Startup under 1 second, smooth 60fps UI on 10-year-old hardware
- **Offline-first**: SQLite local cache means full functionality without internet
- **Single codebase, 3 platforms**: One C++/QML codebase → Windows, macOS, Linux
- **Future-proof**: Qt 6.11 LTS has commercial support through 2029
- **No JavaScript bridge overhead**: C++ talks directly to QML via meta-object system

### Negative
- **C++ expertise required**: Hiring pool is smaller than JavaScript/TypeScript developers
- **Qt commercial license**: LGPL allows free use, but static linking or proprietary modifications require a commercial license (~$500/developer/year for Qt for Application Development)
- **Build complexity**: CMake + Qt toolchain is more complex than `npm install && npm start`
- **UI iteration slower**: QML changes require recompilation (though `qmlscene` enables hot-reload for pure QML)
- **Qt maintenance burden**: Must track Qt LTS releases and security patches independently

### Mitigations
- Train existing C++ developers on Qt specifics via internal documentation
- Budget Qt commercial license in operational costs
- Use Qt Creator IDE for rapid QML prototyping with live preview
- Automate Qt SDK installation in CI/CD pipeline

## Validation Plan

| Test | Expected Result |
|------|----------------|
| **Startup time** (cold launch on reference hardware: Intel i5, 8GB RAM, SSD) | **< 1 second** from click to interactive UI |
| **Memory usage** (idle at dashboard, no jobs loaded) | **< 80 MB** RSS |
| **Offline mode** (disable network, perform full CRUD on jobs) | Create, read, update, delete jobs work without internet; changes queued in SQLite outbox |
| **Sync on reconnect** (restore network after offline changes) | Queued changes pushed to API; conflicts resolved (last-write-wins); UI updates automatically |
| **Cross-platform build** (`cmake --build .` on Windows, macOS, Linux) | Same C++/QML codebase compiles without platform-specific `#ifdef` changes |
| **QML binding** (change ViewModel property via C++) | QML UI reflects change within one frame (16ms); no manual `update()` calls |
| **Login + JWT refresh** (authenticate, let token expire, trigger API call) | AuthInterceptor automatically refreshes token; API call succeeds without user intervention |
| **Tenant isolation on desktop** (switch branch in UI) | X-Tenant-ID and X-Branch-ID headers update; subsequent API calls scoped to new branch |

If any test fails, this ADR must be reconsidered.

| Alternative | Rejected Because |
|-------------|-----------------|
| **Electron** | 250MB+ memory idle, slow startup, poor battery life, feels non-native. Romanian technicians use varied hardware, many with 4GB RAM. |
| **Flutter Desktop** | Immature Linux support, non-native rendering (Skia draws everything), no system tray API without plugins. |
| **.NET MAUI** | Windows-first ecosystem. macOS/Linux are second-class. Romanian market is 30% macOS. |
| **Tauri** | Too new (v2 in 2025), Rust learning curve adds hiring friction, WebView-based (same non-native feel as Electron). |
| **SwiftUI (macOS only)** | Single-platform. 60% of Romanian businesses use Windows. Non-starter. |
| **PWA (Progressive Web App)** | No native system tray, limited offline storage (IndexedDB quota), no file system access, feels like a website. |

## References
- Redmine desktop epic: #523 (Nexus SaaS)
- Redmine desktop task-packets: #524 (Design), #525 (Scaffold), #526 (API Client), #528 (Tests), #529 (SQLite)
- AGENTS.md: Desktop tech stack definition (line 61)
- Qt 6.11 LTS Documentation: https://doc.qt.io/qt-6/