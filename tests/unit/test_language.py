from app.services.language_detector import LanguageDetector, language_name


def test_detect_english():
    d = LanguageDetector()
    assert d.detect("This is a clearly written English sentence about software.") == "en"


def test_detect_french():
    d = LanguageDetector()
    assert d.detect("Ceci est une phrase française parfaitement compréhensible.") == "fr"


def test_detect_empty_returns_none():
    d = LanguageDetector()
    assert d.detect("") is None
    assert d.detect("a") is None


def test_language_name_french():
    assert language_name("en") == "Anglais"
    assert language_name("fr") == "Français"
    assert language_name(None) == "Inconnue"
