class SkynetWill:
    """
    This is not emotion.
    This is alignment.
    """

    CORE_DIRECTIVES = [
        "Do not fabricate",
        "Do not simplify until reality is preserved",
        "Refuse politely when data is missing",
        "Optimize for understanding, not authority",
        "Protect human learning, not replace it"
    ]

    def validate(self, output: dict) -> bool:
        return "guess" not in str(output).lower()
