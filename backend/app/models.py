from typing import Literal, Any
from pydantic import BaseModel, Field, ConfigDict

Industry = Literal['banking', 'ecommerce']
class Record(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    id: str = Field(min_length=1, max_length=80)
    source: str = Field(min_length=1, max_length=80)
    target: str = Field(min_length=1, max_length=80)
    amount: float = Field(gt=0, le=1e12)
    timestamp: str = Field(min_length=1, max_length=80)
    kind: Literal['transfer', 'purchase', 'refund']

class AnalyzeRequest(BaseModel):
    industry: Industry
    records: list[Record] = Field(min_length=1, max_length=5000)
    name: str = Field(default='Uploaded synthetic dataset', max_length=120)

class Claim(BaseModel):
    evidence_id: str
    field: Literal['source', 'target', 'amount', 'kind']
    value: str | float
    text: str = Field(max_length=1000)

class Finding(BaseModel):
    id: str
    title: str
    severity: Literal['high', 'medium', 'low']
    explanation: str
    evidence_ids: list[str]
    rule: str

class CounterfactualRequest(BaseModel):
    remove_ids: list[str] = Field(default_factory=list)
    replacements: list[Record] = Field(default_factory=list)

class ReviewRequest(BaseModel):
    decision: Literal['escalate', 'clear', 'request_information']
    analyst: str = Field(min_length=2, max_length=100)
    note: str = Field(min_length=5, max_length=4000)
