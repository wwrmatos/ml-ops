import pandera as pa
from pandera.typing import Series

class ChurnSchema(pa.DataFrameModel):
    tenure: Series[int] = pa.Field(ge=0, le=72)
    MonthlyCharges: Series[float] = pa.Field(ge=0)
    TotalCharges: Series[float] = pa.Field(ge=0)
    Churn: Series[str] = pa.Field(isin=["Yes", "No"])

    class Config:
        coerce = True
        strict = False