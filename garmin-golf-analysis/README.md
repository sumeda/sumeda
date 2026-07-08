# Garmin Golf Analysis

Small Python utilities for summarizing Garmin Golf scorecard exports.

This project was created for analyzing repeated rounds at the same course and
green, such as Nippon Country Club B green. Personal scorecard data is kept
outside the repository by default.

## Usage

Prepare a JSON file with rounds in this shape:

```json
[
  {
    "date": "2026-07-05",
    "course": "Nippon Country Club",
    "green": "B",
    "tees": "Regular Tees",
    "out": 42,
    "in": 50,
    "putts": 30,
    "fairways_hit": 3,
    "fairways_total": 14,
    "gir_hit": 1,
    "gir_total": 18,
    "holes": [
      {"hole": 1, "par": 5, "score": 6, "putts": 2}
    ]
  }
]
```

Run:

```bash
python3 garmin_golf_analysis.py rounds.json
```

The script prints a Markdown report with score trends, fairway and GIR rates,
putting averages, and hardest/easiest holes.

## Privacy

Do not commit private Garmin exports unless you intentionally want them in the
repository. Store personal data in a local JSON file or in a private repository.
