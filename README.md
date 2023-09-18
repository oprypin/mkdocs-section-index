# mkdocs-section-index

**[Plugin][] for [MkDocs][] to allow clickable sections that lead to an index page**

[![PyPI](https://img.shields.io/pypi/v/mkdocs-section-index)](https://pypi.org/project/mkdocs-section-index/)
[![GitHub](https://img.shields.io/github/license/oprypin/mkdocs-section-index)](https://github.com/oprypin/mkdocs-section-index/blob/master/LICENSE.md)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/oprypin/mkdocs-section-index/ci.yml.svg)](https://github.com/oprypin/mkdocs-section-index/actions?query=event%3Apush+branch%3Amaster)

```shell
pip install mkdocs-section-index
```

[mkdocs]: https://www.mkdocs.org/
[plugin]: https://www.mkdocs.org/user-guide/plugins/

## [Example](example/)

![Screencast with comparison](https://user-images.githubusercontent.com/371383/99844559-8c4caa00-2b73-11eb-9e97-fad82447746c.gif)

With this `nav` in *mkdocs.yml* (or without `nav` but with [an equivalent directory structure](example/docs/)):

```yaml
nav:
  - Frob: index.md
  - Baz: baz.md
  - Borgs:
    - borgs/index.md
    - Bar: borgs/bar.md
    - Foo: borgs/foo.md

plugins:
  - search
  - section-index
```

The *borgs/index.md* page is merged as the index of the "Borgs" section. Normally sections in [MkDocs][] cannot be clickable as pages themselves, but this plugin makes that possible.

**See also: [a realistic demo site](https://oprypin.github.io/crystal-book/syntax_and_semantics/literals/).**

## Theme support

This plugin requires per-theme overrides (implemented within the plugin), or [support from themes themselves](#implementation-within-themes).

Currently supported [themes][] are:

* [material](https://github.com/squidfunk/mkdocs-material)
* [readthedocs](https://www.mkdocs.org/user-guide/styling-your-docs/#readthedocs)
* [nature](https://github.com/waylan/mkdocs-nature)

[themes]: https://github.com/mkdocs/mkdocs/wiki/MkDocs-Themes

## Usage notes

The kind of *nav* as shown above also happens to be what MkDocs produces when `nav` is omitted; it detects [`index.md` and `README.md`][nav-gen] pages and automatically puts them as the first item.

To make writing this kind of `nav` more natural ([in YAML there's no better option](https://github.com/mkdocs/mkdocs/pull/1042#issuecomment-290787554)), consider using the **[literate-nav][] plugin** along with this; then the above *nav* might be written like this:

```markdown
* [Frob](index.md)
* [Baz](baz.md)
* [Borgs](borgs/index.md)
    * [Bar](borgs/bar.md)
    * [Foo](borgs/foo.md)
```

[literate-nav]: https://oprypin.github.io/mkdocs-literate-nav/

## [Implementation](https://github.com/oprypin/mkdocs-section-index/blob/master/mkdocs_section_index/plugin.py)

### "Protocol"

Normally in MkDocs [`nav`][nav], the items can be one of:

* a [`Section`][Section], which has a `title` and `children`.
    * (`url` is always `None`)
* a [`Page`][Page], which has a `title` and `url`.
    * (`title` can be omitted, and later deduced from the page content)
    * ([`children`][children] is always `None`)
* a [`Link`][Link] (inconsequential for our purposes).

This plugin introduces a [hybrid kind of `Page`](https://github.com/oprypin/mkdocs-section-index/blob/master/mkdocs_section_index/__init__.py), which has all of these properties:

* `title`: `str`
* `url`: `str`
* `children`: `list`
* `is_page` = `True`
* `is_section` = `True`

Such a special item gets put into a nav in the place of a `Section` which has a `Page` with an intentionally omitted title as its first child. Those two are naturally combined into a special [section-page](https://github.com/oprypin/mkdocs-section-index/blob/master/mkdocs_section_index/__init__.py) that's a hybrid of the two.

[nav]: https://www.mkdocs.org/user-guide/custom-themes/#nav
[Section]: https://www.mkdocs.org/user-guide/custom-themes/#section
[Page]: https://www.mkdocs.org/user-guide/custom-themes/#page
[children]: https://github.com/mkdocs/mkdocs/blob/2f833a1a29095733e53a04d062d315629d974ebe/mkdocs/structure/pages.py#L26
[Link]: https://www.mkdocs.org/user-guide/custom-themes/#link

### Implementation within themes

Then all that a theme's template needs to do is to meaningfully support such nav items -- ones that have both a `url` and `children`. The item should be directly clickable to go to the corresponding page, and also be able to house sub-items.

Of course, currently templates don't expect such a case; or if they did, it would be purely by chance. So currently this plugin "hacks into" templates of supported themes, [patching their source on the fly](https://github.com/oprypin/mkdocs-section-index/blob/master/mkdocs_section_index/rewrites.py) to fit its needs. The hope is that, once this plugin gains enough traction, theme authors will be happy to directly support this scenario (which is totally non-intrusive and backwards-compatible), and then the patches could be dropped.

### "Alternatives considered"

Even if all the template patches are gone, this plugin will still remain as the implementation of this special nav "protocol", and as the **opt-in mechanism**. In the author's view, such an approach is advantageous, because:

* This is too controversial to be enabled by default, or even be part of MkDocs at all. This has been [discussed in the past and dropped](https://github.com/mkdocs/mkdocs/pull/1042#issuecomment-260813540). The main reason is that in MkDocs there's no requirement for a *nav*'s structure to follow the actual directory structure of the doc files. Consequently, there's no natural way to deduce that a document should become the index page of a section just from its location, even if it's named *index.md*. Although if the *nav* is [omitted & generated][nav-gen], then yes, such an assumption works. It also works in the vast majority of actual usages *with* a *nav*, but that doesn't help.

* Themes themselves also probably shouldn't directly try to detect logic such as "first child of a section if it has no title" and manually collapse the child *within Jinja template code*, as that's too messy. This also shouldn't be enabled by default. And even though templates could also make this opt-in, a centralized approach like this one ensures that accessing this feature is done uniformly. Not to mention that templates might never implement this themselves.

[nav-gen]: https://www.mkdocs.org/user-guide/writing-your-docs/#configure-pages-and-navigation
