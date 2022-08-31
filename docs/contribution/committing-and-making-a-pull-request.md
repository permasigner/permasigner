---
description: Learn how to contribute and manage your changes.
---

# Committing and making a Pull Request

## Commit and Push changes

After every change you make and test, you should commit your changes. In VSCode, this is as easy as clicking the Source Control icon on the left, typing in a short description, and clicking commit. You can also sync changes to your fork (where the Actions will make sure the script still works, if enabled).&#x20;

In a terminal `git add .`, `git commit -am "Your description here"`, and `git push -u origin main` will give the same result. Don't miss the dot at the end of the add command!

If you want to test the package, you can run `make build`, and it'll create a `whl` file in the `dist` directory. You can then run `pip install dist/the-name-of-the.whl`, and use `permasigner` to run it.

## Make a pull request

After you're finished implementing your changes, you'll want to request them to be added to the main repository.

* Make sure all your changes are pushed, as shown above
* Navigate to [this URL](https://github.com/permasigner/permasigner/compare) to open a new pull request
  * Keep base as main (which is Permasigner's main branch), and set compare as your fork's main branch (or the branch you were working in)
* Follow the template and create your pull request
  * It'll be reviewed as soon as possible
