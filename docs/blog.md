# extra-model Blog

## [22-10-21] Simplifying usage of `extra-model`
During the month of October it's always a good idea to clean some cobwebs that has been around for a while.
In the spirit of Hacktoberfest we've decided to clean up couple of issues that simplify how `extra-model` is called.

Before, all, but one parameter (`--debug`) that you could provide to CLI version of `extra-model` were arguments, which in `click` 
parlance meant that they were positional. That in turn meant that you could only change, e.g., embeddings path by first
specifying both output path AND output filename. Well, no longer! From now on all, but one, inputs to `extra-model` (input path), are options
which means that they can be set in any order using flags that you can see by running `extra-model --help`.
No need to thank us :).

Another tiny UX improvement is that we check the names of the columns BEFORE running `extra-model`.
With big inputs running `extra-model` can take hours, so it was a subpar user experience when it would fail after 
all this time because `CommentId` column is misspeled. Now it'll fail with descriptive error within seconds.


## [18-05-21] Simplifying install of `extra-model`

We have updated/removed all the dependencies that don't have wheels. 
In addition, we've switched to Python 3.8 as a base image (we are still testing `extra-model` in 3.7, 3.8 and 3.9).

Full list of changes is available in the CHANGELOG

## [17-03-21] Blog Setup!

`extra-model` v0.2.0 is released!