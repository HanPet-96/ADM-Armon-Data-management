from adm_app.update_check import is_newer_version, normalize_version


def test_normalize_version() -> None:
    assert normalize_version("v1.0.0.2") == (1, 0, 0, 2)
    assert normalize_version("1.0.1") == (1, 0, 1)
    assert normalize_version("v2.1.0-beta1") == (2, 1, 0)
    assert normalize_version("") == (0,)


def test_is_newer_version() -> None:
    assert is_newer_version("1.0.0.1", "v1.0.0.2")
    assert is_newer_version("1.0.0.9", "1.0.1")
    assert not is_newer_version("1.0.0.2", "1.0.0.2")
    assert not is_newer_version("1.2.0", "1.1.9")
