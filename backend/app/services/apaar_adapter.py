from dataclasses import dataclass


@dataclass
class APaarVerificationResult:
    verified: bool
    mode: str
    message: str


class APaarVerificationAdapter:
    def verify(self, apaar_id: str, name: str) -> APaarVerificationResult:
        raise NotImplementedError


class SimulatedAPaarVerificationAdapter(APaarVerificationAdapter):
    def verify(self, apaar_id: str, name: str) -> APaarVerificationResult:
        if apaar_id.startswith("APAAR") and len(name.strip()) >= 3:
            return APaarVerificationResult(
                verified=True,
                mode="simulated",
                message="Simulated verification succeeded. Not an official government response.",
            )
        return APaarVerificationResult(
            verified=False,
            mode="simulated",
            message="Simulated verification failed. Not an official government response.",
        )


class OfficialAPaarVerificationAdapter(APaarVerificationAdapter):
    def verify(self, apaar_id: str, name: str) -> APaarVerificationResult:
        raise RuntimeError("Official APAAR integration is not configured.")
