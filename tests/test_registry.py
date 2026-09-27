from international_classifications_mcp.registry import (
    browse_hierarchy,
    export_choices,
    get_code,
    list_classifications,
    list_codelists,
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
        "mics7_responses",
        "icls_lfs19",
        "icatus2016", "cofog1999", "copni1999", "copp1999", "unece_rec20", "unece_rec21",
        "dhs8_responses", "wg_responses", "jmp2018_responses", "who_vax_responses", "fao_wca2020_responses",
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
    assert counts["icc11"] >= 190
    assert counts["icatus2016"] > 700
    assert counts["cofog1999"] > 180
    assert counts["copni1999"] > 60
    assert counts["copp1999"] > 50
    assert counts["unece_rec20"] > 2000
    assert counts["unece_rec21"] > 400
    assert counts["iscedf2013"] > 100
    assert counts["iccs1"] > 300


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
    assert catalog["mics7_responses"].coverage == "curated"
    assert "mics7_indicators" not in catalog
    assert "mics7_modules" not in catalog
    assert get_code("mics7_responses", "CF.DIFFICULTY.A_LOT").label == "A lot of difficulty"


def test_mics7_questionnaire_discovery():
    result = recommend(
        "What is the household's main source of drinking water?",
        ["Piped into dwelling", "Borehole", "Surface water"],
        "MICS household questionnaire",
    )
    assert result.recommendations[0].classification_id == "mics7_responses"
    search = search_codes("birth registration", ["mics7_responses"], 10)
    assert search.total >= 1
    indicator = recommend("What proportion of under-five children are stunted in MICS?")
    assert not indicator.recommendations
    assert "Development Indicators MCP" in indicator.next_action


def test_mics_codelists_are_independent_and_exportable():
    lists = {item.codelist_id: item for item in list_codelists("mics7_responses")}
    assert lists["BR.STATUS"].option_count == 4
    assert lists["CF.DIFFICULTY"].option_count == 4
    result = search_codes("vaccination source", ["mics7_responses"], 20)
    assert {item.codelist_id for item in result.results} == {"IM.SOURCE"}
    export = export_choices("mics7_responses", format="xlsform", codelist_id="BR.STATUS")
    assert export.option_count == 4
    assert {row["list_name"] for row in export.rows} == {"BR.STATUS"}
    try:
        export_choices("mics7_responses")
        assert False, "MICS export should require a codelist"
    except ValueError as error:
        assert "codelist_id is required" in str(error)


def test_search_safely_handles_fts_punctuation():
    for query in ["zzzzzz-no-such-code", "x:y", '(quoted)', '"operator"', "teacher's", "water—source"]:
        result = search_codes(query, None, 5)
        assert result.total >= 0
    assert search_codes("zzzzzz-no-such-code", None, 5).total == 0


def test_priority_three_questionnaire_ecosystems_are_separate_codelists():
    expected = {
        "dhs8_responses": "DHS8.CONTRACEPTION",
        "wg_responses": "WG.DIFFICULTY",
        "jmp2018_responses": "JMP.WATER.LADDER",
        "who_vax_responses": "WHO.VAX.EVIDENCE",
        "fao_wca2020_responses": "WCA.LAND_USE",
    }
    for classification_id, codelist_id in expected.items():
        ids = {item.codelist_id for item in list_codelists(classification_id)}
        assert codelist_id in ids
        exported = export_choices(classification_id, codelist_id=codelist_id)
        assert exported.option_count > 1


def test_regression_search_routing_and_validation():
    assert search_codes("nurse", ["isco08"], 10).total > 0
    labour = recommend("Was the respondent employed, unemployed, or outside the labour force last week?")
    assert labour.recommendations[0].classification_id == "icls_lfs19"
    field = recommend("What was the field of your degree or qualification?")
    assert field.recommendations[0].classification_id == "iscedf2013"
    try:
        search_codes("teacher", ["not_real"], 10)
        assert False, "unknown classification should fail"
    except ValueError as error:
        assert "Unknown classification_id" in str(error)
    try:
        search_codes("teacher", ["isco08"], -1)
        assert False, "negative limit should fail"
    except ValueError as error:
        assert "limit must be" in str(error)
