# Contributing to this project

###### How to Contribute to _DQT_

## 👋 Greetings!

Thanks for considering contributing to this open-source project! Both beginners 
and experts are very welcome here.

If you want to contribute to this project, I recommend taking the time to read 
these contributing guidelines (or even use your AI assistant to summarize this 
document for you).

---

## 📝 Table of Contents

- [✨ Contributions You Can Make](#-contributions-you-can-make)
- [📐 Requirements](#-requirements)
- [🚦 Opening Issues](#-opening-issues)
  - [🐛 Reporting Bugs](#-reporting-bugs)
  - [☝️ Suggesting Features](#-suggesting-features)
- [🧭 Pull Request Guidelines](#-pull-request-guidelines)
  - [⚠️ THINGS TO KEEP IN MIND](#-things-to-keep-in-mind)
- [🧑‍💻 Code Guidelines](#-code-guidelines)
- [🧰 Making Your First Contribution](#-making-your-first-contribution)


---

## ✨ Contributions You Can Make

There are many ways you can contribute: 
- [Suggesting or adding a feature](#-suggesting-features)
- [Finding and reporting bugs](#-reporting-bugs)
- Reformatting, refactoring, or enhancing code
- Improving documentation
- [Participating in discussions][repo-disc]
- Helping to review or give feedback to pull requests or issues
- Suggesting task issues (by opening a discussion)
- ...and more!

Any addition to the project will be very much appreciated, even small or minor 
ones.

[^ TOC](#-table-of-contents)

## 📐 Requirements

- **Python 3.12 and above** (recommended)
- A recognized IDE / code editor, for example:
  - Visual Studio Code (with a proper linter or code analyzer installed)
  - JetBrains IDEs (PyCharm, IntelliJ, WebStorm, etc.)
  - Eclipse
  - Xcode
  - **NOT** the GitHub web editor or a basic text editor

[^ TOC](#-table-of-contents)

---

## 🚦 Opening Issues

**We highly recommend [opening an issue][repo-issues]** before creating a 
pull request. This is to ensure all changes are discussed properly (and you 
don't waste your time creating a PR that ends up getting closed). 

This is also to prevent automatically-generated pull requests created by 
automated bot accounts that usually come with low effort and minimal engagement.

### 🐛 Reporting Bugs

To report a bug:
1. On the repository on GitHub, go to the [Issues][repo-issues] tab.
2. Select "New issue".
3. **Template selection: Choose "Bug report"**.
4. Describe the issue thoroughly, using the template as a guide
   - If your issue description severely lacks information, maintainers may 
     close it.
5. Submit the issue.

### ☝️ Suggesting Features

To suggest a feature:
1. On the repository on GitHub, go to the [Issues][repo-issues] tab.
2. Select "New issue".
3. **Template selection: Choose "Feature request"**
4. Describe the feature thoroughly, using the template as a guide.
    - If your issue description severely lacks information, maintainers may 
      close it.
5. Submit the issue.

...or add a comment under a [discussion][repo-disc] describing the feature.

[^ TOC](#-table-of-contents)

---

## 🧭 Pull Request Guidelines

(NOTE: Read "[Opening Issues](#-opening-issues)" first if you plan on adding an 
enhancement to the project or fixing a bug)

1. Create a fork of [the repository][repo].
2. Clone the forked repository to your local machine.
3. Create a new branch with a meaningful name (include the type of change 
   followed by a slash; use hierarchical branch naming).

   | Prefix           | Description                                    |
   |------------------|------------------------------------------------|
   | `bugfix`/`fix`   | Bug fix (minor, not urgent)                    |
   | `hotfix`         | Urgent, critical fix                           |
   | `feature`        | New feature/functionality                      |
   | `ui`             | Affects user interface only                    |
   | `docs`           | Documentation only                             |
   | `format`/`style` | Formatting fixes                               |
   | `refactor`       | Code improvements that do not affect behaviour |
   | `test`           | Changes to test files                          |
   | `experiment`     | Temporary, experimental code; playground       |
   | `mix`            | A combination of different fixes/changes       |
   | `misc`           | Other; miscellaneous                           |

   - e.g.) `feature/feature-name`, `fix/issue-12`
   
4. Make and commit your changes.
   - Commit messages should be in the imperative tone without a period.
     - e.g.: `Add test files`, `Fix this function`, `Update README`
5. Push commits to GitHub (if you have made changes locally on your machine).
6. Create and submit a pull request.
7. Optional: Request a review from a maintainer.

Please try to stay engaged with your PR and **avoid abandoning your work**. 

You should receive a notification/email once your changes have been merged into 
upstream main.

### ⚠️ THINGS TO KEEP IN MIND
- **Rebase > Merge**: When updating a branch, **always use a rebase** and 
  resolve conflicts.
- **Do not work directly on `main`**; always create a new branch on your fork.
- To avoid conflicts, **always remember to update your local fork** 
  (`git pull`) before working.
- If you forgot to update your fork before working, run `git pull --rebase` 
  and resolve conflicts (if any).
  - If you run into any trouble during conflict resolution, or are not sure 
    how to resolve a conflict, tag a maintainer/reviewer in an appropriate 
    issue or PR comments section for help.

[^ TOC](#-table-of-contents)

## 🧑‍💻 Code Guidelines

Here are **3 rules** you should remember when writing code:

> `1.` Styling matters

Writing properly styled and formatted code ensures that your code can be easily 
read and understood by everyone.

For Python code, follow [PEP 8][pep-8].

Key things to keep in mind include:
- **Line lengths** (try to keep lines **below 80 characters**; PEP 8 says 79 but
  both work)
- **Naming conventions** (module, variable, class, and function names)
  - `variable_must_be_named_like_this`
  - `functions_too`
  - `also_modules`
  - `ClassesMustBeNamedLikeThis`
- **Docstring and comments formatting**
- **Line separations** (2 blank lines around classes and functions, etc.)
- **Order of import statements** (standard → third-party → local)

—————————————————————————————————————————————————————————————————————

> `2.` Always assume the user doesn't know what they're doing

Special cases (almost) always exist. Make sure you take into account as many 
input possibilities as you can, even those that anyone in their right mind 
would never think of. Ensure that you any documentation is written clearly and
avoid _too_ much jargon or unnecessarily complicated language

—————————————————————————————————————————————————————————————————————

> `3.` Don't be boring

Give your code some _✨personality✨_. Avoid dull, flavorless code. You can 
even add a little joke comment if your code starts to look sleep-inducing.

[^ TOC](#-table-of-contents)

## 🤖 AI-Assisted Contributions

AI tools can be helpful during development, and contributors are allowed to use
them as **assistive tools**. However, this project does **not accept 
contributions that are noticeably and mostly AI-generated**.

When submitting a pull request:
- **A human must be responsible** for the work submitted.
- **You must personally review, understand, and test** any code you submit.
- Contributors must be able to **explain their changes and respond to review 
  feedback**.

Pull requests that appear to be:
- primarily AI-generated (including PR descriptions or comments),
- created by a bot/automated account,
- or lacking human oversight
may be **closed without merging**.

Just so you know, it is quite easy to tell AI-generated code apart from 
human-writen code.

[^ TOC](#-table-of-contents)

## 🧰 Making Your First Contribution

If you're new here or are not familiar with contributing to repositories on 
GitHub, here are some links with information that might help:

- https://docs.github.com/get-started/exploring-projects-on-github/contributing-to-a-project
- https://docs.github.com/get-started/exploring-projects-on-github/contributing-to-open-source
- https://github.com/firstcontributions/first-contributions

[^ TOC](#-table-of-contents)

[repo]: https://github.com/TheGittyPerson/day-quality-tracker
[repo-issues]: https://github.com/TheGittyPerson/day-quality-tracker/issues
[repo-disc]: https://github.com/TheGittyPerson/day-quality-tracker/discussions
[pep-8]: https://peps.python.org/pep-0008/
