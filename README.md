# Eggslist Backend Application
## Deploy
For a local app run use:
`python manage.py runserver`
### Environment
`.env` file is reuqired in the root directory:
```
# Main
SECRET_KEY
ENVIRONMENT # choice of local, development, prod – affects which settings is used
# Database
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
# Redis
REDIS_PASSWORD
REDIS_HOST
REDIS_PORT
REDIS_DB
# Email
EMAIL_HOST
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL
EMAIL_PORT
# Static and Media Bucket Info
DO_ACCESS_KEY_ID
DO_SECRET_ACCESS_KEY
DO_STORAGE_BUCKET_NAME
# Social Auth
GOOGLE_CLIENT_ID
GOOGLE_SECRET_KEY
FACEBOOK_CLIENT_ID
FACEBOOK_SECRET_KEY
```
### CI/CD
CI/CD is set up through GitHub Actions with 2 possible environments: development and production. \
All of the secrest are stored in a secret storage and could be adjusted by repo admins.
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
`Release Oct 25: Revision Location Cookies`
