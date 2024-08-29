# README: About pyOpenSci peer review metrics
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

This is a dashboard created using mystmd [![Made with MyST](https://img.shields.io/badge/made%20with-myst-orange)](https://myst.tools). Myst-md is a community developed tool that makes it easier for scientists to create fully reproducible (and interactive) workflows and reports that are easily shared.

## How to Contribute

### 1. **Fork and Clone the Repo:**

To begin, fork this repository to your GitHub account. Then, clone it
locally to work on a branch from your computer.

### 2. Create your GitHub token

The code in this repository uses the GitHub REST API. To ensure that you can
access and make requests to the API, you will need to create a token in your
GitHUb account.

Through the pyOpenSci [`pyosMeta`](https://github.com/pyOpenSci/pyosMeta)
package. This package was created to parse through pyOpenSci software review
issues, and obtain both contributor and package metadata. To use this package,
you need to supply a GitHub access
token. This token can be created from your personal GitHub account.

NOTE: You do not need special access to the pyOpenSci organization for this workflow
because all of our repositories are public!

#### Create your token

In GitHub, click on your profile image and navigate to "Settings", and then
"Developer Settings".

![Image of GitHub Developer Settings page](images/developer_settings.png "Developer Settings page")
<br/><br/>
Create a new fine-grained personal access token, adding a name, expiration,
description, and ensure the "Repository Access" is set to "Public Repositories
(read-only)". No other configuration needed. At the bottom of the page, click
"Generate token".

![Image of personal access token](images/token.png "Token configuration page")
<br/><br/>

### 3. Store token information in an `.env` file

Copy the `.env-default` file in this repository and
rename it to `.env`. You will paste your GitHub token value that you created
above into this file.

Copy the token string and paste it into the `.env` file next to `GITHUB_TOKEN=`.
It should look somethign like this

`GITHUB_TOKEN=yourtokenvaluehere`

You are now setup to process pyOpenSci peer review and contributor metadata
using `pyosMeta`.

## Build the website using Nox

You can use `nox` to build the site locally. `Nox` will create an `venv`
environment for you with all needed dependencies to run the code and build
the peer review metrics dashboard.

To start, install [nox](https://nox.thea.codes/en/stable/):

Using `pip`:

`python -m pip install nox`

or [`pipx` for global install](https://pipx.pypa.io/stable/):

`pipx install nox`

### Build a static html website

To build the html version of the dashboard use

`nox -s build`

### Build a live local server dashboard

To build the dashboard as a local server that will update
as you update the files use:

`nox -s serve`

One a mac you can use `ctrl + d` to stop a live server.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/kaiyamag"><img src="https://avatars.githubusercontent.com/u/98053751?v=4?s=100" width="100px;" alt="kaiyamag"/><br /><sub><b>kaiyamag</b></sub></a><br /><a href="https://github.com/pyOpenSci/peer-review-metrics/commits?author=kaiyamag" title="Code">💻</a> <a href="https://github.com/pyOpenSci/peer-review-metrics/pulls?q=is%3Apr+reviewed-by%3Akaiyamag" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ehinman"><img src="https://avatars.githubusercontent.com/u/121896266?v=4?s=100" width="100px;" alt="Elise Hinman"/><br /><sub><b>Elise Hinman</b></sub></a><br /><a href="https://github.com/pyOpenSci/peer-review-metrics/commits?author=ehinman" title="Code">💻</a> <a href="https://github.com/pyOpenSci/peer-review-metrics/pulls?q=is%3Apr+reviewed-by%3Aehinman" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.santisoler.com"><img src="https://avatars.githubusercontent.com/u/11541317?v=4?s=100" width="100px;" alt="Santiago Soler"/><br /><sub><b>Santiago Soler</b></sub></a><br /><a href="https://github.com/pyOpenSci/peer-review-metrics/commits?author=santisoler" title="Code">💻</a> <a href="https://github.com/pyOpenSci/peer-review-metrics/pulls?q=is%3Apr+reviewed-by%3Asantisoler" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/fwkoch"><img src="https://avatars.githubusercontent.com/u/9453731?v=4?s=100" width="100px;" alt="Franklin Koch"/><br /><sub><b>Franklin Koch</b></sub></a><br /><a href="https://github.com/pyOpenSci/peer-review-metrics/commits?author=fwkoch" title="Code">💻</a> <a href="https://github.com/pyOpenSci/peer-review-metrics/pulls?q=is%3Apr+reviewed-by%3Afwkoch" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/agoose77"><img src="https://avatars.githubusercontent.com/u/1248413?v=4?s=100" width="100px;" alt="Angus Hollands"/><br /><sub><b>Angus Hollands</b></sub></a><br /><a href="https://github.com/pyOpenSci/peer-review-metrics/commits?author=agoose77" title="Code">💻</a> <a href="https://github.com/pyOpenSci/peer-review-metrics/pulls?q=is%3Apr+reviewed-by%3Aagoose77" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://batalex.github.io"><img src="https://avatars.githubusercontent.com/u/11004857?v=4?s=100" width="100px;" alt="Alex Batisse"/><br /><sub><b>Alex Batisse</b></sub></a><br /><a href="https://github.com/pyOpenSci/peer-review-metrics/commits?author=batalex" title="Code">💻</a> <a href="https://github.com/pyOpenSci/peer-review-metrics/pulls?q=is%3Apr+reviewed-by%3Abatalex" title="Reviewed Pull Requests">👀</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
