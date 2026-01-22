from asr_coffee_os.physics import boiling_point_c_at_altitude, extraction_yield_percent

def test_boiling_point_decreases_with_altitude():
    assert boiling_point_c_at_altitude(0) == 100.0
    assert boiling_point_c_at_altitude(1000) < 100.0

def test_extraction_yield_basic():
    ey = extraction_yield_percent(tds_percent=1.35, beverage_g=300, dose_g=18)
    assert 10.0 < ey < 30.0
