"""Model for institutions associated with an author."""
from __future__ import annotations


class AssociatedInstitution:
    """Institution linked with an author."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str,
        relationship: str,
        ror: str | None = None,
        country_code: str | None = None,
        type_: str | None = None,
    ) -> None:
        self.id = id
        self.ror = ror
        self.display_name = display_name
        self.country_code = country_code
        self.type = type_
        self.relationship = relationship

