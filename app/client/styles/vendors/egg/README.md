# egg

*egg* is the successor to [egghsell](https://github.com/Wiredcraft/eggshell) and keeps the same overall goal; providing a SASS/Bourbon boilerplate. It was developed originally for building Web apps at [Wiredcraft](https://wiredcraft.com) (things like [devo.ps](http://devo.ps)).

**More on the official page: http://wiredcraft.github.io/egg/#about**.

## How to use?

*egg* is supposed to be a simple starting point for your styles rather than a
dependency;

1. **Dependencies**; `bower install` to add bourbon and normalize (scss version) or edit the `egg.scss` to change the import path for these dependencies.
2. **Hack**; you could simply `@import egg.scss` and override the styles, or start
modifying the files. `partials/` is definitely fair game, `modules/` too if you
know what you're doing.

**More details at http://wiredcraft.github.io/egg/#how-to/**.

## /docs

To build the styles for the public page (in `docs/`):

    cd docs
    sass --sourcemap=none --style compressed --watch styles.scss:styles.css

Obviously, drop the `--watch` option if you're not actively working on it.
