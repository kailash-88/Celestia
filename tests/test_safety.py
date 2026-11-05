import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.safety_engine import run_safety_check, check_duplicates, check_interactions, check_expiry, check_missing


def test_duplicate():
    meds = [{"name": "A", "active_ingredient": "x"}, {"name": "B", "active_ingredient": "x"}]
    r = check_duplicates(meds)
    assert r and r[0]["category"] == "duplicate_ingredient"


def test_interaction_covered():
    meds = [{"name": "W", "active_ingredient": "warfarin"}, {"name": "Asp", "active_ingredient": "aspirin"}]
    r = check_interactions(meds)
    assert any(x["category"] == "interaction" for x in r)


def test_interaction_unavailable():
    meds = [{"name": "A", "active_ingredient": "foo"}, {"name": "B", "active_ingredient": "bar"}]
    r = check_interactions(meds)
    assert any(x["category"] == "interaction_unavailable" for x in r)


def test_expiry_expired():
    meds = [{"name": "A", "active_ingredient": "x", "expiry_date": "2020-01-01"}]
    r = check_expiry(meds)
    assert r[0]["category"] == "expired"


def test_missing():
    meds = [{"name": "", "active_ingredient": ""}]
    r = check_missing(meds)
    assert r


def test_run():
    meds = [{"name": "A", "active_ingredient": "x"}]
    assert isinstance(run_safety_check(meds), list)
