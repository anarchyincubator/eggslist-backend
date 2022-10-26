# Eggslist Backend Application

## Contribution
### Pull Requests
Please, create pull requests with base: **development** and compare: your feature branch. Nothing should go to **production** bypassing the **development** and review of eggslist team.
### Commit message guide
#### Feature commit (goes to any feature branch or to **development** branch)
Commit names should follow the structure: \
`commit-key-word`: `issue` -- `message` \
`optional-message-body` \
If commit does not address any issue from issue tracker it should look like: \
`commit-key-word`: `message` \
`optional-message-body` \
`commit-key-word` and `message` supposed to be capitalized.
Subject line should be less than or equal to 50 characters in length.
Body line length limited to 80 characters. Multiple body lines are allowed.
`commit-key-word` is a key word briefly explaining what type of a problem current commit addreses. Available `commit-key-word` options:
* Feat - feature;
* Fix - bug fix;
* Refactor – code refactoring;
* Chore – project internal updates like library update or CI/CD pipeline update;
* Test – writing tests

Examples: \
`Feat: #24 -- Implement Google and Facebook auth` \
`Fix: #54 -- Login email case insensetivity` \
`Fix: Location Cookie Mechanics`

#### Production merge commit (goes to **production** branch)
Production branch can be changed only via pull requests. Subject line of commit message should be less than or equal to 50 characters in length. 
Body line length limited to 80 characters. Multiple body lines are allowed.
Production branch commit follows the structure:
Release `Month Day`: `message` \
`optional-message-body`

Examples: \
`Release Oct 25: Revision Location Cookies` \
