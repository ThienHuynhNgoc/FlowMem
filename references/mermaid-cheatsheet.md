# Mermaid Cheatsheet — All 26 Diagram Types

Quick syntax reference for every Mermaid diagram type supported as of Mermaid 11.x.

---

## 1. Flowchart

```mermaid
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Process]
    B -->|No| D[Skip]
    C --> E[End]
    D --> E
```

**Directions:** `TD` (top-down), `LR` (left-right), `BT` (bottom-top), `RL` (right-left)

**Node shapes:** `[rect]` `(rounded)` `{diamond}` `((circle))` `>flag]` `[/parallelogram/]` `[(cylinder)]` `[\\trapezoid/]`

**Link types:** `-->` `---` `-.->` `==>` `--text-->` `-->|label|`

---

## 2. Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant API
    participant DB

    User->>API: GET /data
    API->>DB: SELECT *
    DB-->>API: rows
    API-->>User: 200 OK
    Note over API: Cached for 60s
    loop Retry
        API->>DB: ping
    end
```

**Arrows:** `->>` (solid) `-->>` (dashed) `-x` (cross) `-)` (open/async)

**Blocks:** `loop`, `alt/else`, `opt`, `par`, `critical`, `break`, `rect`

---

## 3. Class Diagram

```mermaid
classDiagram
    class Animal {
        +String name
        #int age
        -bool alive
        +makeSound() String
        +move(distance int) void
    }
    class Dog {
        +fetch() void
    }
    Animal <|-- Dog : extends
    Dog --> Bone : uses
    Animal --o Zoo : part-of
```

**Relationships:** `<|--` (inherit) `*--` (composition) `o--` (aggregation)
`-->` (association) `..>` (dependency) `<..` (realization) `--` (link)

**Visibility:** `+` public  `-` private  `#` protected  `~` package

---

## 4. State Diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Active : trigger
    Active --> Idle : reset
    Active --> Error : fail
    Error --> [*]

    state Active {
        [*] --> Loading
        Loading --> Ready
    }
```

**Features:** Composite states, forks (`<<fork>>`), joins (`<<join>>`), history (`[H]`), notes

---

## 5. ER Diagram

```mermaid
erDiagram
    CUSTOMER {
        int id PK
        string name
        string email UK
    }
    ORDER {
        int id PK
        int customer_id FK
        date placed_at
    }
    CUSTOMER ||--o{ ORDER : places
```

**Cardinalities:** `||` (exactly one) `|o` (zero or one) `}|` (one or more) `}o` (zero or more)

---

## 6. Gantt

```mermaid
gantt
    title Project Plan
    dateFormat YYYY-MM-DD
    excludes weekends
    section Phase 1
    Task A  :done,  t1, 2026-01-01, 7d
    Task B  :active, t2, after t1, 5d
    section Phase 2
    Task C  :t3, after t2, 3d
    Milestone :milestone, m1, after t3, 0d
```

**Status:** `done` `active` `crit` `milestone`

---

## 7. Pie Chart

```mermaid
pie showData
    title Distribution
    "TypeScript" : 45
    "Python" : 30
    "Bash" : 15
    "Other" : 10
```

---

## 8. Git Graph

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "feat-a"
    commit id: "feat-b"
    checkout main
    merge develop id: "merge" tag: "v1.0"
    commit id: "hotfix"
```

---

## 9. Mind Map

```mermaid
mindmap
  root((Central Topic))
    Branch A
      Leaf 1
      Leaf 2
    Branch B
      Leaf 3
      ::icon(fa fa-star)
      Subbranch
        Deep leaf
```

**Shapes:** `((circle))` `[square]` `(rounded)` `))cloud((` `{{hexagon}}`

---

## 10. Timeline

```mermaid
timeline
    title Key Events
    section 2024
        Jan : Event one
        Mar : Event two : Detail note
    section 2025
        Jun : Launch
```

---

## 11. Kanban

```mermaid
kanban
    column1[Backlog]
        task1[Write tests]
        task2[Update docs]
    column2[In Progress]
        task3[Fix bug #42]
    column3[Done]
        task4[Deploy v2]
```

---

## 12. Quadrant Chart

```mermaid
quadrantChart
    title Risk vs Reward
    x-axis Low Risk --> High Risk
    y-axis Low Reward --> High Reward
    quadrant-1 High Value
    quadrant-2 Proceed Carefully
    quadrant-3 Avoid
    quadrant-4 Quick Wins
    Feature A: [0.8, 0.9]
    Feature B: [0.3, 0.7]
    Feature C: [0.5, 0.2]
```

---

## 13. Requirement Diagram

```mermaid
requirementDiagram
    requirement UserAuth {
        id: REQ-001
        text: Must support OAuth2
        risk: high
        verifymethod: test
    }
    functionalRequirement DataExport {
        id: REQ-002
        text: Export to CSV and JSON
        risk: low
        verifymethod: inspection
    }
    element AuthModule {
        type: component
    }
    UserAuth - satisfies -> AuthModule
```

---

## 14. C4 Diagram

```mermaid
C4Context
    title System Context
    Person(user, "End User")
    System(app, "My App", "Core system")
    System_Ext(email, "Email Service")
    Rel(user, app, "Uses", "HTTPS")
    Rel(app, email, "Sends emails", "SMTP")
```

**Diagram levels:** `C4Context` `C4Container` `C4Component` `C4Dynamic` `C4Deployment`

---

## 15. Sankey

```mermaid
sankey-beta
    Revenue,Product Sales,500
    Revenue,Services,300
    Product Sales,COGS,200
    Product Sales,Profit,300
    Services,Labor,150
    Services,Profit,150
```

---

## 16. XY Chart (beta)

```mermaid
xychart-beta
    title "Monthly Commits"
    x-axis [Jan, Feb, Mar, Apr, May, Jun]
    y-axis "Commits" 0 --> 100
    bar [45, 62, 38, 71, 55, 83]
    line [45, 62, 38, 71, 55, 83]
```

---

## 17. User Journey

```mermaid
journey
    title User Onboarding
    section Sign Up
      Visit landing page: 5: User
      Click Sign Up: 4: User
      Fill form: 3: User
    section First Use
      Complete tutorial: 4: User, System
      Create first project: 5: User
```

---

## 18. Architecture (beta)

```mermaid
architecture-beta
    group cloud(cloud)[Cloud]
    service api(internet)[API Gateway] in cloud
    service db(database)[Database] in cloud
    service cache(server)[Redis Cache] in cloud
    api:R --> L:db
    api:B --> T:cache
```

---

## 19. Block Diagram (beta)

```mermaid
block-beta
    columns 3
    A["Module A"] B["Module B"] C["Module C"]
    A --> B
    B --> C
```

---

## 20. Packet (beta)

```mermaid
packet-beta
    title TCP Header
    0-3: "Source Port"
    4-7: "Dest Port"
    8-15: "Sequence Number"
    16-23: "Ack Number"
    24-27: "Offset"
```

---

## 21. ZenUML

```mermaid
zenuml
    Client->Server: Request
    Server->DB: Query
    DB-->Server: Result
    Server-->Client: Response
```

---

## 22. Radar (Spider)

```mermaid
radar
    title Team Skills
    Developer : 85
    Designer : 60
    Devops : 70
    Security : 55
    Testing : 90
```

---

## 23. Treemap (experimental)

```mermaid
treemap
    root
        src 80
            components 45
            utils 20
            hooks 15
        tests 20
        docs 10
```

---

## 24. Venn (experimental)

```mermaid
venn
    sets [{"label": "Frontend"}, {"label": "Backend"}, {"label": "DevOps"}]
    intersections [[0,1,"Fullstack"], [1,2,"SRE"], [0,1,2,"Platform Eng"]]
```

---

## 25. Ishikawa / Fishbone

```mermaid
---
config:
  theme: neutral
---
%%{init: {"look": "handDrawn"}}%%
fishbone
    title Production Bug
    Method
        Manual deploy
    Machine
        Old server
    People
        No review
    Environment
        Config drift
```

---

## 26. Tree View (experimental)

```mermaid
treeView
    root[Project Root]
        src[src/]
            components[components/]
            utils[utils/]
        tests[tests/]
        docs[docs/]
```

---

## Mermaid Init Options

```
%%{init: {
  "theme": "default",
  "themeVariables": {
    "primaryColor": "#6366f1",
    "edgeLabelBackground": "#fff"
  }
}}%%
```

**Themes:** `default` `dark` `forest` `neutral` `base`
