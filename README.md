# CS 499 Computer Science Capstone — ePortfolio

**Ethan Chapman**  
Southern New Hampshire University  
April 2026

---

## Overview

This ePortfolio represents the culmination of my Computer Science program at SNHU. It showcases three categories of enhancement applied to a single artifact — the **Grazioso Salvare Animal Shelter Dashboard** — originally developed during CS 340: Client/Server Development.

The dashboard is a data-driven application built with Python, MongoDB, PyMongo, and Plotly Dash that helps a fictional search-and-rescue organization identify shelter animals matching specific rescue training criteria.

**Live ePortfolio:** [https://codecatalyst-1.github.io/CS-499-Capstone/](https://codecatalyst-1.github.io/CS-499-Capstone/)

---

## Repository Structure

```
CS-499-Capstone/
├── index.html                          # GitHub Pages ePortfolio site
├── artifacts/
│   ├── original/
│   │   ├── crud_original.py            # Original CRUD module from CS 340
│   │   ├── ProjectTwoDashboard_original.ipynb  # Original dashboard notebook
│   │   └── aac_shelter_outcomes.csv    # AAC shelter outcomes dataset (10,000 records)
│   └── enhanced/
│       ├── crud.py                     # Enhanced CRUD module
│       └── ProjectTwoDashboard.ipynb   # Enhanced dashboard notebook
├── narratives/
│   ├── Milestone2_Narrative_EthanChapman.docx  # Software Design & Engineering
│   ├── Milestone3_Narrative.docx               # Algorithms & Data Structures
│   └── Milestone4_Narrative.docx               # Databases
└── docs/
    ├── Professional_Self_Assessment.docx       # Professional self-assessment
    └── Code_Review.docx                        # Code review document
```

---

## Enhancements

### Enhancement One: Software Design & Engineering
Connected the dashboard to MongoDB through the CRUD module, replaced print() with the logging module, added type hints and input validation, and implemented correct rescue filter logic with a standalone `build_filter_map()` function.

### Enhancement Two: Algorithms & Data Structures
Replaced identical placeholder filters with a `RESCUE_CRITERIA` data structure and `apply_rescue_filter()` algorithm that composes compound boolean masks to produce meaningfully distinct result sets for each rescue category.

### Enhancement Three: Databases
Added automatic index management (single-field and compound indexes), a MongoDB aggregation pipeline for outcome distribution, a `get_distinct()` method for live dropdown population, and a `bulk_import()` utility with duplicate handling via `ordered=False`.

---

## Course Outcomes

| Outcome | Where Demonstrated |
|---|---|
| Collaborative environments & decision-making | Code review, GitHub portfolio, self-assessment |
| Professional-quality communications | All narratives, dashboard as stakeholder tool |
| Algorithmic principles & design trade-offs | Enhancement 2, Enhancement 3 |
| Well-founded techniques & tools | Enhancement 1, Enhancement 3 |
| Security mindset | Enhancement 1, Enhancement 3 |

---

## Technologies

- Python 3.9
- MongoDB / PyMongo
- Plotly Dash
- Pandas
- Jupyter Notebook
