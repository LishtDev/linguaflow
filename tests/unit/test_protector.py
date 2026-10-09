from app.services.protection.element_protector import ElementProtector


def test_protect_inline_code_roundtrip():
    p = ElementProtector()
    text = "Appelez la fonction `print()` pour afficher."
    protected, ph = p.protect(text)
    assert "print()" not in protected
    assert p.restore(protected, ph) == text


def test_protect_url_email_path():
    p = ElementProtector()
    text = "Voir https://example.com/doc et admin@site.fr, fichier /etc/hosts."
    protected, ph = p.protect(text)
    restored = p.restore(protected, ph)
    assert restored == text


def test_protect_code_block():
    p = ElementProtector()
    text = "Exemple:\n```python\nx = 1\n```\nfin."
    protected, ph = p.protect(text)
    assert "x = 1" not in protected
    assert p.restore(protected, ph) == text


def test_custom_protected_terms_whole_word():
    p = ElementProtector(custom_protected=["Acme Corp"])
    text = "Acme Corp augmente ses ventes."
    protected, ph = p.protect(text)
    assert "Acme Corp" not in protected
    assert p.restore(protected, ph) == text


def test_glossary_restores_to_target_term():
    p = ElementProtector(glossary={"cloud computing": "informatique en nuage"})
    text = "Le cloud computing est utile."
    protected, ph = p.protect(text)
    assert "cloud computing" not in protected
    out = p.restore(protected, ph)
    assert "informatique en nuage" in out
    assert "cloud computing" not in out


def test_no_leftover_placeholders_after_restore():
    p = ElementProtector(custom_protected=["Python"])
    text = "Python est utilisé avec https://python.org et `pip install`."
    protected, ph = p.protect(text)
    restored = p.restore(protected, ph)
    assert not p.has_leftover_placeholders(restored)
    assert restored == text


def test_does_not_break_common_words():
    p = ElementProtector()
    text = "We should return the class and function to the user."
    protected, ph = p.protect(text)
    # Ordinary English words must remain translatable.
    originals = [x["original"].lower() for x in ph]
    for word in ("return", "class", "function", "user"):
        assert word not in originals


class _ManglingEngine:
    """Engine that destroys placeholder tokens, to exercise the fallback."""
    name = "mangler"
    mode = "local"

    def translate(self, text, source_lang=None, target_lang="fr"):
        # Simulate an engine that mangles the placeholder delimiters.
        return text.replace("%", "")


def test_translate_fallback_preserves_when_tokens_mangled():
    p = ElementProtector()
    engine = _ManglingEngine()
    text = "Contact admin@example.com to use `run_task()` now."
    out = p.translate(engine, text, "en", "fr")
    # Both elements must survive verbatim even though the engine mangled tokens.
    assert "admin@example.com" in out
    assert "`run_task()`" in out
    assert not p.has_leftover_placeholders(out)


def test_translate_fastpath_preserves_exact_when_engine_keeps_tokens():
    class _EchoEngine:
        def translate(self, text, source_lang=None, target_lang="fr"):
            return text

    p = ElementProtector(glossary={"cloud computing": "informatique en nuage"})
    out = p.translate(_EchoEngine(), "We use cloud computing daily.", "en", "fr")
    assert "informatique en nuage" in out
    assert "cloud computing" not in out
