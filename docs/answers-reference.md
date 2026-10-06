# Answers file reference

The dashboard saves and loads answers as JSON, and the command-line tool reads the same format. Start from `samples/answers_template.json`.

```json
{
  "organization": {
    "name": "Your company",
    "cage_code": "",
    "employees": 0,
    "description": "What the company does for the Department of Defense",
    "system_name": "Name of the system that handles FCI",
    "system_boundary": "Computers, cloud services, and networks that handle FCI",
    "fci_types": "Kinds of Federal Contract Information handled",
    "point_of_contact": "Name, title",
    "senior_official": "Name, title"
  },
  "answers": {
    "AC1-1": {"answer": "yes", "note": "How it is done", "evidence": "What proves it"},
    "AC1-2": {"answer": "partial", "note": "What is missing"},
    "SC2-1": {"answer": "na", "note": "Why it does not apply"}
  }
}
```

- `answer` is one of `yes`, `partial`, `no`, `na`, or blank. A plain string such as `"AC1-1": "yes"` also works.
- Notes on **Yes** answers become the implementation description in the System Security Plan. Notes on **Partly** or **No** answers are recorded as gap details.
- **N/A** requires a note explaining why the item does not apply.

The question ids and their text are in `src/cmmc_kit/data/level1.json`.

The answers file describes your security weaknesses. Store it securely.
