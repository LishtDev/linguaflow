from app.services.correction.linguistic_corrector import LinguisticCorrector


def test_corrector_spacing_before_punctuation():
    c = LinguisticCorrector()
    corrected, changes = c.correct("Bonjour!")
    assert "Bonjour !" in corrected


def test_corrector_removes_space_before_comma():
    c = LinguisticCorrector()
    corrected, _ = c.correct("Bonjour , monde")
    assert "Bonjour, monde" in corrected


def test_corrector_capitalization():
    out, _ = LinguisticCorrector().correct("bonjour tout le monde")
    assert out[0].isupper()


def test_corrector_preserves_placeholders():
    out, _ = LinguisticCorrector().correct("Utilisez [[LF1]] pour cela")
    assert "[[LF1]]" in out


def test_meaning_preserving_guard():
    assert LinguisticCorrector.is_meaning_preserving(
        "le renard brun rapide", "le rapide renard brun")
    assert not LinguisticCorrector.is_meaning_preserving(
        "bonjour", "complètement autre chose ici maintenant")
