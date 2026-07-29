from dataclasses import dataclass, field


@dataclass(slots=True)
class ClaimResult:
    """
    Result of verifying a single factual claim.
    """

    claim: str
    verdict: str
    evidence: list[str] = field(default_factory=list)


@dataclass(slots=True)
class HallucinationResult:
    """
    Final hallucination detection output.
    """

    score: float

    supported_claims: list[ClaimResult] = field(default_factory=list)

    unsupported_claims: list[ClaimResult] = field(default_factory=list)

    contradicted_claims: list[ClaimResult] = field(default_factory=list)

    summary: str = ""
