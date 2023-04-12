# CommunityNetwork
This aims to define pairings for CommunityNetwork.


## Directory Structure

root
- app
- data
  - input
    - `<iteration>`
  - output
    - `<iteration>`
- diagrams


## Expected input files

Compulsory files
- Roster file: 
  - file name: `./data/input/<iteration>/<iteration>_Roster.xlsx`
  - sheet name: `Roster`
- Interest file: 
  - file name: `./data/input/<iteration>/<iteration>_Interest.xlsx`
  - sheet name: `Interest`

Optional file
- Pair file:
  - file name: `./data/input/<iteration>/<iteration>_Pair.xlsx`
  - sheet name: `Pair`
If the pair file is not provided, pairs will be calculated based on existing data in the database.


## Expected output files
- Enriched Match file: `./data/output/<iteration>/"enriched_matched_<iteration>.json"`
- Matched file: `./data/output/<iteration>/"matched_<iteration>.json"`
- Unmatched file: `./data/output/<iteration>/"unmatched_<iteration>.json"`


## Meeting Pairing rules

- [x] Last pairing was over 8 iterations ago
- [x] No pairings between PML and counsellee
- [ ] Managers should have at most 2 meetings with juniors
- [ ] Prioritise people that have not been paired before
- [ ] Prioritise people that are in the same location
- [ ] Prioritise people that are in the same timezone


## Data organisation
- Collections:
  - [x] Roster
  - [ ] Relationships
  - [x] Meetings
  - [x] Interest


### Collections

- CSE Roster
```json
    {
      "_id": "",
      "emp_name": "", 
      "emp_pref_name": "", 
      "emp_email": "", 
      "job_level": "", 
      "job_family": "", 
      "pml": ""
    }
```


- Meetings
```json
      {
        "iteration_name": "",
        "iteration_number": "",
        "junior": "",
        "senior": ""
      }
```


- Interest
```json
  [
      {
        "iteration_number": "",
        "iteration_name": "",
        "emp_email": ""
      }
  ]
```
