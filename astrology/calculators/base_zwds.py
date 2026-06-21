from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

class AbstractZWDSCalculator(ABC):
    """
    Abstract Base Class for the Chinese Zi Wei Dou Shu (ZWDS) calculation engine.
    """
    
    @abstractmethod
    async def calculate_chart(
        self,
        tlt_datetime: datetime,
        gender: str = "M",
        latitude: float = 0.0,
        longitude: float = 0.0,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Calculates the ZWDS structural matrix.
        """
        pass
