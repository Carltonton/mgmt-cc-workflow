---
type: dashboard
title: "Recent Activity"
purpose: "Auto-updated feed of recent changes across the knowledge base"
date_created: "YYYY-MM-DD"
tags:
  - dashboard
---

# Recent Activity

```dataview
TABLE WITHOUT ID
  file.link AS Note,
  type AS Type,
  file.mtime AS Last_Modified
FROM "knowledge-base"
SORT file.mtime DESC
LIMIT 30
```
