# Data Structure – GR Election Analysis

## 1. Project overview

This project processes election data for the 2026 Dutch municipal elections (*Gemeenteraadsverkiezingen 2026*) in the municipality of Lansingerland.

The source data is provided in XML files using the Election Markup Language (EML) format.

The goal is to transform these XML files into structured data that can be analysed with Python and eventually stored in a relational SQL database.

The processing workflow consists of four main steps:

1. **Extract:** Extract the original XML files from the downloaded archive.
2. **Process:** Parse the XML files and transform their contents into Python data structures.
3. **Validate:** Check relationships, identifiers and vote totals for consistency.
4. **Load:** Store the processed data in a SQL database.

The original XML files are retained as raw source data.

---

## 2. Source XML files

The project currently uses five XML files. Each file contains a different part of the election data.

| XML file | Root element | Purpose |
|---|---|---|
| `Verkiezingsdefinitie` | `ElectionEvent` | Contains the election definition and general metadata. |
| `Kandidatenlijsten` | `CandidateList` | Contains participating parties/lists and their candidates. |
| `Telling` | `Count` | Contains vote counts and statistics for individual polling stations. |
| `Totaaltelling` | `Count` | Contains aggregated vote counts for the entire municipality. |
| `Resultaat` | `Result` | Contains the final election results, including rankings and elected status. |

All five files belong to the same election:

- Election: Gemeenteraad Lansingerland 2026
- Election date: 18 March 2026
- Municipality: Lansingerland
- Election identifier: `GR2026_Lansingerland`

### 2.1 Election definition

The `Verkiezingsdefinitie` file contains general information about the election.

Important information includes:

- Election identifier
- Election date
- Municipality
- Election category
- Number of available council seats
- Preference threshold
- Registered parties
- Voting method

This information describes the election itself and provides context for the other XML files.

### 2.2 Candidate lists

The `Kandidatenlijsten` file contains the participating parties or electoral lists (*affiliations*) and their candidates.

The main structure is:

```text
CandidateList
└── Election
└── Affiliation
    ├── AffiliationIdentifier
    ├── RegisteredName
    ├── Type
    └── Candidate
        ├── CandidateIdentifier
        ├── CandidateFullName
        ├── PersonName
        ├── Gender
        └── QualifyingAddress
```

An `Affiliation` represents a participating party or electoral list.

Each affiliation has an `AffiliationIdentifier`, which identifies the list within the election.

Each `Candidate` belongs to an affiliation and has a `CandidateIdentifier`.

Candidate information includes their name, gender and address information where available.

The current files contain 8 affiliations and 193 candidates.

**Important:** Candidate identifiers are not globally unique. For example, multiple parties can have a candidate with identifier `1`.

Therefore, a candidate must be identified using both the affiliation identifier and the candidate identifier, together with the election identifier when storing data across multiple elections.

---

### 2.3 Polling-station counts (`Telling`)

The `Telling` file contains the vote counts for individual polling stations (*reporting units*).

Its main structure includes:

```text
Count
├── Election
├── ReportingUnitVotes
│   ├── ReportingUnitIdentifier
│   ├── TotalVotes
│   │   └── Selection
│   │       ├── AffiliationIdentifier OR Candidate
│   │       └── ValidVotes
│   └── ReportingUnitInvestigations
├── Cast
├── TotalCounted
├── RejectedVotes
└── UncountedVotes
```

Each `ReportingUnitVotes` element represents a polling station.

A polling station is identified by its `ReportingUnitIdentifier`. This includes an identifier and a name.

Within each polling station, `TotalVotes` contains multiple `Selection` elements.

A `Selection` represents a vote count associated with either:

- An affiliation (party/list), identified by `AffiliationIdentifier`.
- A candidate, identified by `Candidate` and `CandidateIdentifier`.

The `ValidVotes` element contains the corresponding vote count.

The file also contains additional voting statistics, such as:

- `Cast`: number of ballots cast.
- `TotalCounted`: number of ballots counted.
- `RejectedVotes`: rejected ballots, with a reason code.
- `UncountedVotes`: uncounted voting documents or other reported quantities, with a reason code.
- `ReportingUnitInvestigations`: additional checks or investigations recorded for a polling station.

The meaning of each reason code should be retained when processing these statistics.

---

### 2.4 Aggregated counts (`Totaaltelling`)

The `Totaaltelling` file uses the same general `Count` structure as the polling-station file.

However, it contains aggregated figures for the entire municipality rather than separate records for each polling station.

It includes:

- Total votes per affiliation.
- Total votes per candidate.
- Overall voting statistics.
- Rejected and uncounted vote information.

This file is useful for analysing the overall election outcome and comparing aggregated results with the sum of the polling-station results.

The aggregated results should be kept distinguishable from individual polling-station records.

---

### 2.5 Final election results (`Resultaat`)

The `Resultaat` file contains the final election results.

Its main structure includes:

```text
Result
└── Selection
    ├── AffiliationIdentifier OR Candidate
    ├── Elected
    └── Ranking
```

The `Selection` elements identify affiliations and candidates.

The result data includes:

- The affiliation or candidate identifier.
- Whether a candidate was elected (`Elected`).
- The candidate's ranking (`Ranking`), where provided.

This file is used to determine the final election outcome.

It is important to distinguish this file from the vote-counting files: `Telling` and `Totaaltelling` describe votes, while `Resultaat` describes the final result and elected status.

---

## 3. Relationships between the data

The XML files describe different parts of the same election. Their identifiers allow the information to be connected.

The main relationships are:

```text
Election
│
├── Affiliations
│   │
│   └── Candidates
│
├── Reporting Units
│   │
│   └── Vote Counts
│       ├── Affiliation Votes
│       └── Candidate Votes
│
├── Aggregated Vote Counts
│
└── Election Results
    ├── Affiliation Results
    └── Candidate Results
```

### 3.1 Election and affiliations

One election can contain multiple affiliations.

Each affiliation has an identifier that is used to connect the party/list information in the candidate-list file to the vote-counting and result files.

### 3.2 Affiliations and candidates

One affiliation can contain multiple candidates.

A candidate belongs to exactly one affiliation within the candidate list for this election.

The combination of `AffiliationIdentifier` and `CandidateIdentifier` is needed to identify a candidate correctly.

### 3.3 Reporting units and votes

One election can contain multiple reporting units (polling stations).

Each reporting unit has vote counts for affiliations and their candidates.

The vote records therefore need to reference:

- The election.
- The reporting unit.
- The affiliation.
- The candidate, where the record concerns an individual candidate.

### 3.4 Votes and final results

The vote-counting files contain the number of votes received.

The result file contains the final outcome, including ranking and elected status.

These datasets can be connected using the election, affiliation and candidate identifiers.

---

## 4. Proposed SQL data model

The following relational structure is a proposed design for the processed data. It is not yet the final database schema.

| Table | Description |
|---|---|
| `elections` | General election information, such as date, municipality and number of seats. |
| `affiliations` | Participating parties and electoral lists. |
| `candidates` | Candidate information, linked to an affiliation. |
| `reporting_units` | Polling stations and their identifiers. |
| `affiliation_votes` | Vote counts per affiliation and polling station. |
| `candidate_votes` | Vote counts per candidate and polling station. |
| `election_results` | Final ranking and elected status for candidates. |
| `vote_statistics` | Statistics such as ballots cast, counted, rejected and uncounted. |

### 4.1 Candidate identification

The candidate table should preserve the identifiers from the XML.

A candidate can be identified by:

```text
election_id
affiliation_id
candidate_id
```

This avoids conflicts when different parties have candidates with the same candidate number.

### 4.2 Candidate vote records

A candidate vote record should contain:

```text
election_id
reporting_unit_id
affiliation_id
candidate_id
valid_votes
```

Each record represents the number of valid votes received by one candidate at one polling station.

### 4.3 Affiliation vote records

An affiliation vote record should contain:

```text
election_id
reporting_unit_id
affiliation_id
valid_votes
```

Each record represents the vote count associated with one affiliation at one polling station.

Affiliation-level and candidate-level vote counts should be stored separately. They should not automatically be added together, because they represent different levels of the same voting results.

### 4.4 Aggregated vote records

The aggregated vote counts from `Totaaltelling` should be distinguishable from the individual polling-station counts.

This makes it possible to compare the municipality-wide totals with the sum of the polling-station records.

---

## 5. Data validation

Before loading the processed data into SQL, several checks should be performed.

Examples include:

- Every candidate references an existing affiliation.
- Every vote record references a valid election.
- Every polling-station vote record references an existing reporting unit.
- Candidate identifiers are interpreted within the correct affiliation.
- Every vote count is converted into an integer.
- Aggregated vote counts are compared with the sum of polling-station counts.
- Affiliation vote totals are compared with the sum of their candidate vote counts, where the source data supports this comparison.
- The final result records reference valid affiliations and candidates.

Validation is important because a structurally valid XML file does not necessarily guarantee that the processed data has been linked correctly.

---

## 6. Processing principles

The following principles guide the implementation:

1. Keep the original XML files unchanged.
2. Separate XML parsing from database operations.
3. Preserve the original election, affiliation, candidate and reporting-unit identifiers.
4. Convert numeric values into appropriate Python types.
5. Keep polling-station counts separate from aggregated election totals.
6. Keep vote counts separate from final election results.
7. Validate relationships and totals before inserting data into SQL.

The Python processing modules should return structured data, such as dictionaries or lists of dictionaries. A separate database-loading module will handle inserting this data into SQL.

This separation makes the XML processing easier to test, maintain and reuse.