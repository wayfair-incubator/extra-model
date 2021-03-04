# Using a Custom Base Class

## Abstract

`extra-model` exposes a class factory that allows you to create the 
`ExtraModel` class with a custom base class. `extra-model` was initially 
developed as an internal project at Wayfair, and this functionality exists 
to allow for continued use of the open source package with Wayfair base 
classes. Use of this feature is not required to run `extra-model` and 
most users can just ignore this feature.

## Quickstart

Create `ExtraModel` with a custom base class
```python
from extra_model import extra_factory
from custom_bases import MyBaseClass

ExtraModel = extra_factory(MyBaseClass)
```

## Reference

::: extra_model._models.extra_factory
