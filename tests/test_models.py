from extra_model._models import ExtraModelBase, ModelBase, extra_factory


class MyCustomBase:
    pass


def test_extra_factory__no_custom_bases_passed__class_has_ModelBase_as_parent():

    Model = extra_factory()

    assert issubclass(Model, ModelBase)


def test_extra_factory__no_custom_bases_passed__class_has_ExtraModelBase_as_parent():

    Model = extra_factory()

    assert issubclass(Model, ExtraModelBase)


def test_extra_factory__custom_bases_passed__class_has_custom_base_as_parent():

    Model = extra_factory(MyCustomBase)

    assert issubclass(Model, MyCustomBase)


def test_extra_factory__multiple_custom_bases_passed__class_has_all_custom_bases_as_parents():
    class MyOtherCustomBase:
        pass

    Model = extra_factory((MyCustomBase, MyOtherCustomBase))

    assert issubclass(Model, MyCustomBase)
    assert issubclass(Model, MyOtherCustomBase)


def test_extra_factory__custom_bases_passed__class_does_not_have_ModelBase_as_parent():

    Model = extra_factory(MyCustomBase)

    assert not issubclass(Model, ModelBase)


def test_extra_factory__custom_bases_passed__class_has_extraModelBase_as_parent():

    Model = extra_factory(MyCustomBase)

    assert issubclass(Model, ExtraModelBase)
