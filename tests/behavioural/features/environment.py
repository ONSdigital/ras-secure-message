def before_scenario(context, scenario):
    if "ignore" in scenario.effective_tags:
        scenario.skip("Not Implemented")
        return
