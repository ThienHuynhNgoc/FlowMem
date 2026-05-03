# FlowMem Chart Selector — Decision Matrix

Use this guide to decide which Mermaid chart type to generate for each type of content.

---

## Primary Decision Matrix

| Content You Have | Chart Type | Syntax Keyword | Method | Script |
|---|---|---|---|---|
| Module/file import graph | Flowchart (LR) | `flowchart LR` | script | `scan_imports.py` |
| Class/interface/type hierarchy | Class Diagram | `classDiagram` | script | `scan_ast.py` / `scan_ts_exports.js` |
| API call sequences, request/response | Sequence Diagram | `sequenceDiagram` | ai | — |
| State machine, lifecycle, FSM | State Diagram | `stateDiagram-v2` | ai | — |
| Database schema, ORM models | ER Diagram | `erDiagram` | ai | read schema files |
| Feature roadmap, sprint plan | Gantt | `gantt` | ai | — |
| System layers (C4 style) | C4 Architecture | `C4Context` | ai | — |
| Task board, feature status | Kanban | `kanban` | ai | — |
| Tech debt topics, TODO clusters | Mind Map | `mindmap` | script+ai | `scan_todos.py` |
| Git commit history, branches | Git Graph | `gitGraph` | script | `scan_git.sh` |
| Complexity vs. value analysis | Quadrant Chart | `quadrantChart` | script | `scan_metrics.py` |
| Data/resource/energy flows | Sankey | `sankey` | ai | — |
| Project/changelog timeline | Timeline | `timeline` | ai | `scan_git.sh` optional |
| Test coverage heatmap | Radar | `radar` | ai | read coverage report |
| Bug/issue type distribution | Pie Chart | `pie` | script | grep issue labels |
| System requirements traceability | Requirement Diagram | `requirementDiagram` | ai | — |
| User journey / UX flow | User Journey | `journey` | ai | — |
| Network infrastructure | Architecture (beta) | `architecture-beta` | ai | — |
| Cause-and-effect / RCA | Ishikawa/Fishbone | `---` (not yet stable) | ai | — |
| File size breakdown | Pie Chart | `pie` | script | `scan_files.sh` |
| npm dependency tree | Flowchart (TB) | `flowchart TB` | script | `scan_packages.js` |
| XY metrics scatter | XY Chart (beta) | `xychart-beta` | script | `scan_metrics.py` |

---

## Layer Assignment

Once you select a chart type, assign it to a layer:

| Layer | Contains | Load when... |
|---|---|---|
| `structure` | flowchart (imports), classDiagram, architecture | understanding code organization |
| `behavior` | sequenceDiagram, stateDiagram | tracing execution flows |
| `data` | erDiagram, sankey | understanding data models or flows |
| `project` | gantt, kanban, timeline, requirementDiagram | planning or feature context |
| `quality` | mindmap (debt), pie (distribution), radar, quadrantChart, gitGraph | health and history |

---

## Chart Type Examples

### flowchart LR — Module Dependencies

```mermaid
flowchart LR
    main --> auth
    main --> api
    auth --> db
    api --> db
    api --> cache
```

### classDiagram — Class Hierarchy

```mermaid
classDiagram
    class Animal {
        +String name
        +makeSound() void
    }
    class Dog {
        +fetch() void
    }
    Animal <|-- Dog
```

### sequenceDiagram — API Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant AuthAPI
    participant DB

    User->>Frontend: Submit login form
    Frontend->>AuthAPI: POST /auth/login
    AuthAPI->>DB: SELECT user WHERE email=?
    DB-->>AuthAPI: User record
    AuthAPI-->>Frontend: JWT token
    Frontend-->>User: Redirect to dashboard
```

### stateDiagram-v2 — Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Running : start()
    Running --> Paused : pause()
    Paused --> Running : resume()
    Running --> Done : finish()
    Done --> [*]
```

### erDiagram — Database Schema

```mermaid
erDiagram
    USER {
        int id PK
        string email
        string password_hash
        timestamp created_at
    }
    WORKSPACE {
        int id PK
        int user_id FK
        string name
        text mermaid_text
    }
    USER ||--o{ WORKSPACE : owns
```

### gantt — Roadmap

```mermaid
gantt
    title Feature Roadmap Q3 2026
    dateFormat YYYY-MM-DD
    section Core
    Auth System       :done,    a1, 2026-04-01, 2026-04-15
    Workspace CRUD    :done,    a2, 2026-04-15, 2026-05-01
    section Next
    Export Bundle     :active,  b1, 2026-05-01, 2026-05-20
    Desktop App       :         b2, 2026-05-20, 2026-06-15
```

### mindmap — Tech Debt

```mermaid
mindmap
  root((Tech Debt))
    Auth
      TODO: rotate JWT secret
      FIXME: logout race condition
    Database
      TODO: add indexes
      HACK: raw SQL fallback
    Frontend
      TODO: extract shared hooks
      FIXME: stale state on nav
```

### gitGraph — Branch History

```mermaid
gitGraph
    commit id: "init"
    branch feature/auth
    checkout feature/auth
    commit id: "add login"
    commit id: "add JWT"
    checkout main
    merge feature/auth
    commit id: "v1.0.0"
```

### pie — File Distribution

```mermaid
pie title File Types in /src
    "TypeScript" : 62
    "CSS" : 18
    "JSON" : 12
    "Markdown" : 8
```

### radar — Coverage

```mermaid
radar
    title Test Coverage by Module
    Auth : 92
    API : 78
    Database : 85
    Frontend : 44
    Engine : 70
```

### kanban — Feature Board

```mermaid
kanban
    Backlog
        task1[Add dark mode]
        task2[Export to PDF]
    In Progress
        task3[Fix auth bug]
    Done
        task4[Docker deploy]
        task5[JWT refresh]
```

### C4Context — System Architecture

```mermaid
C4Context
    title System Context — FlowMem
    Person(user, "Developer", "Uses FlowMem to index repos")
    System(flowmem, "FlowMem Skill", "Generates Mermaid memory")
    System_Ext(vscode, "VS Code", "Views .mmd files")
    System_Ext(flowskill, "FlowSkill", "Renders and executes diagrams")

    Rel(user, flowmem, "Triggers skill")
    Rel(flowmem, vscode, "Writes .mmd files")
    Rel(user, flowskill, "Pastes charts")
```

### timeline — Project History

```mermaid
timeline
    title Development Timeline
    2026-01 : Project started
             : Initial scaffolding
    2026-02 : Auth system added
             : Docker integration
    2026-03 : Desktop app (Tauri)
    2026-04 : FlowMem v1.0 released
```

### quadrantChart — Complexity vs Value

```mermaid
quadrantChart
    title Feature Complexity vs Business Value
    x-axis Low Complexity --> High Complexity
    y-axis Low Value --> High Value
    quadrant-1 Do Now
    quadrant-2 Plan Carefully
    quadrant-3 Deprioritize
    quadrant-4 Quick Wins
    Auth: [0.7, 0.9]
    Export: [0.5, 0.8]
    Dark Mode: [0.2, 0.4]
    Admin Panel: [0.8, 0.6]
```

### requirementDiagram — Formal Requirements

```mermaid
requirementDiagram
    requirement AuthRequirement {
        id: 1
        text: Users must authenticate with JWT
        risk: high
        verifymethod: test
    }
    element LoginEndpoint {
        type: interface
    }
    AuthRequirement - verifies -> LoginEndpoint
```

---

## Choosing Between Similar Types

**flowchart vs. sequenceDiagram:**
- Use `flowchart` for static structure (module relationships, code paths)
- Use `sequenceDiagram` for dynamic runtime interactions (who calls whom and when)

**classDiagram vs. erDiagram:**
- Use `classDiagram` for code-level class/interface/type relationships
- Use `erDiagram` for database-level entity and column relationships

**gantt vs. kanban vs. timeline:**
- Use `gantt` for time-boxed planning with start/end dates
- Use `kanban` for current-state task board (what's in progress now)
- Use `timeline` for historical milestones (what already happened)

**mindmap vs. pie:**
- Use `mindmap` when debt/issues have category hierarchy
- Use `pie` for flat distribution/proportion data
