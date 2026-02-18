"""Download strategy definitions for bypassing restrictions."""


class DownloadStrategy:
    """Encapsulates a single download strategy with fallback options."""
    
    STRATEGIES = [
        {
            "name": "Standard",
            "description": "Standard YouTube extraction",
            "extra": {}
        },
        {
            "name": "Android Bypass",
            "description": "Uses Android player client",
            "extra": {'extractor_args': {'youtube': {'player_client': ['android']}}}
        },
        {
            "name": "iOS Bypass",
            "description": "Uses iOS player client",
            "extra": {'extractor_args': {'youtube': {'player_client': ['ios']}}}
        },
        {
            "name": "TV Bypass",
            "description": "Uses TV player client",
            "extra": {'extractor_args': {'youtube': {'player_client': ['tv']}}}
        }
    ]
    
    @classmethod
    def get_all(cls):
        """Get all available download strategies."""
        return cls.STRATEGIES
    
    @classmethod
    def get_strategy(cls, name):
        """Get a specific strategy by name."""
        for strategy in cls.STRATEGIES:
            if strategy["name"].lower() == name.lower():
                return strategy
        return None
