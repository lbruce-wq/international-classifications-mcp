from international_classifications_mcp.server import mcp


def test_server_identity_and_tools():
    assert mcp.name == "International Classifications MCP"
    names = {tool.name for tool in mcp._tool_manager.list_tools()}
    assert {
        "list_classifications",
        "recommend_classifications",
        "search_codes",
        "map_codes",
        "export_choice_list",
    } <= names
