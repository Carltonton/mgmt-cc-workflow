---
type: dashboard
title: "Knowledge Base Dashboard"
purpose: "Main landing page for the research knowledge base"
date_created: "YYYY-MM-DD"
tags:
  - dashboard
---

# Knowledge Base Dashboard

[YOUR PROJECT NAME] — [YOUR NAME] ([YOUR INSTITUTION])

---

## Literature Progress

```dataview
TABLE WITHOUT ID
  length(rows) AS Total,
  length(filter(rows, (r) => r.reading_status = "complete")) AS Complete,
  length(filter(rows, (r) => r.reading_status = "reading" OR r.reading_status = "annotating")) AS In_Progress,
  length(filter(rows, (r) => r.reading_status = "unread" OR r.reading_status = "skimming")) AS Unread
FROM "knowledge-base/01-literature/notes"
FLATTEN true AS dummy
GROUP BY dummy
```

## Recent Literature Notes

```dataview
TABLE reading_status AS Status, journal AS Journal, year AS Year, thread AS Thread
FROM "knowledge-base/01-literature/notes"
SORT date_added DESC
LIMIT 15
```

## Construct Operationalization

```dataview
TABLE name_zh AS 中文名, origin_theory AS Origin, operationalization_status AS Status, measured_in_study AS Study
FROM "knowledge-base/02-theory/constructs"
SORT operationalization_status ASC
```

## Hypothesis Tracker

```dataview
TABLE hypothesis_id AS ID, direction AS Direction, status AS Status
FROM "knowledge-base/02-theory/propositions"
SORT hypothesis_id ASC
```

## Recent Activity

```dataview
TABLE WITHOUT ID
  file.link AS Note,
  choice(type = "literature-note", "Literature",
    choice(type = "construct", "Construct",
      choice(type = "hypothesis", "Hypothesis",
        choice(type = "study-note", "Study", "Other")))) AS Type,
  date_added AS Added
FROM "knowledge-base"
WHERE date_added >= date(today) - dur(30 days)
SORT date_added DESC
LIMIT 20
```

## Quick Links

- [[research-map|Research Map]]
- [[synthesis|Literature Synthesis]]

## Papers by Journal

```dataview
TABLE WITHOUT ID journal AS Journal, length(rows) AS Count
FROM "knowledge-base/01-literature/notes"
GROUP BY journal
SORT length(rows) DESC
```
