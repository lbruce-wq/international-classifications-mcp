from international_classifications_mcp.registry import (
    browse_hierarchy,
    get_code,
    list_classifications,
    map_codes,
    recommend,
    search_codes,
    validate_codes,
)


def test_catalog_has_tier_one_families():
    items = list_classifications()
    ids = {item.id for item in items}
    assert {
        "isco08",
        "icse18",
        "isic5",
        "cpc3",
        "coicop2018",
        "hs2022",
        "sitc4",
        "bec5",
        "isced2011",
        "iscedf2013",
        "icc11",
        "icd11",
        "icf",
        "iccs1",
        "m49",
        "sdmx",
        "mics7_modules",
        "mics7_responses",
        "mics7_indicators",
    } <= ids


def test_current_full_sources_have_codes():
    counts = {item.id: item.code_count for item in list_classifications()}
    assert counts["isic5"] > 400
    assert counts["cpc3"] > 3000
    assert counts["coicop2018"] > 600
    assert counts["hs2022"] > 6000
    assert counts["sitc4"] > 5000
    assert counts["isco08"] > 500
    assert counts["m49"] > 200


def test_exact_and_full_text_lookup():
    assert get_code("isic5", "0111").label.startswith("Growing of cereals")
    result = search_codes("cereals", ["isic5"], 5)
    assert any(item.code == "0111" for item in result.results)


def test_questionnaire_recommendation_distinguishes_concepts():
    status = recommend(
        "What is your position in your main job?",
        ["Employee", "Employer", "Own-account worker", "Unpaid family worker"],
        "Labour force survey",
    )
    assert status.recommendations[0].classification_id == "icse18"
    occupation = recommend("What is your job title and what are your main tasks?")
    assert occupation.recommendations[0].classification_id == "isco08"
    industry = recommend("What goods are produced by the establishment where you work?")
    assert industry.recommendations[0].classification_id == "isic5"
    education = recommend("What is the highest level of education you completed?")
    assert education.recommendations[0].classification_id == "isced2011"


def test_validation_and_hierarchy():
    result = validate_codes("coicop2018", ["01", "01.1", "not-a-code"])
    assert result.valid_count == 2 and result.invalid_count == 1
    assert browse_hierarchy("coicop2018", "01")


def test_official_mapping_isic4_to_5():
    result = map_codes("isic4", "isic5", ["0111"])
    assert result.results[0].target_codes == ["0111"]
    assert result.results[0].official


def test_mics7_layer_is_versioned_and_separated():
    catalog = {item.id: item for item in list_classifications()}
    assert catalog["mics7_modules"].version == "7.1.9"
    assert catalog["mics7_responses"].coverage == "curated"
    assert catalog["mics7_indicators"].version == "7.1.9"
    assert get_code("mics7_responses", "CF.DIFFICULTY.A_LOT").label == "A lot of difficulty"
    assert "30 minutes" in get_code("mics7_indicators", "WASH.DRINKING_BASIC").definition


def test_mics7_questionnaire_discovery():
    result = recommend(
        "What is the household's main source of drinking water?",
        ["Piped into dwelling", "Borehole", "Surface water"],
        "MICS household questionnaire",
    )
    assert result.recommendations[0].classification_id == "mics7_responses"
    search = search_codes("birth registration", ["mics7_modules", "mics7_indicators"], 10)
    assert search.total >= 2
