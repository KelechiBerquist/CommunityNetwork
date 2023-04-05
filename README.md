# Skip Levels
This aims to define pairings for SkipLevels.

## Directory Structure

root
- src
- data
  - input
    - iteration
  - output
    - iteration
- diagrams


## Meeting Pairing rules

- Last pairing was over a year ago
- No pairings between PML and counsellee
- Managers should have at most 2 meetings with juniors
- Prioritise people that have not been paired before
- Prioritise people that are in the same location
    - Prioritise people that are in the same timezone


## Data organisation
- Database: SkipLevels
- Collections:
  - Roster
  - Relationships
  - Meetings
  - Interest

### Collections

- CSE Roster
```json
    {
      "_id": "",
      "name": "", 
      "preferred_name": "", 
      "email": "", 
      "level": "", 
      "location": "", 
      "pml": "", 
      "spml": "", 
      "office_region": ""
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
