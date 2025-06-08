"""Short form of a publication source."""
from __future__ import annotations

from collections.abc import Iterable


class DehydratedSource:
    """Minimal details about a source."""

    def __init__(
        self,
        *,
        id: str,
        display_name: str | None = None,
        issn_l: str | None = None,
        issn: Iterable[str] | None = None,
        is_oa: bool | None = None,
        is_in_doaj: bool | None = None,
        is_core: bool | None = None,
        host_organization: str | None = None,
        host_organization_name: str | None = None,
        host_organization_lineage: Iterable[str] | None = None,
        type: str | None = None,
    ) -> None:
        self.id = id
        self.display_name = display_name
        self.issn_l = issn_l
        self.issn = list(issn) if issn is not None else None
        self.is_oa = is_oa
        self.is_in_doaj = is_in_doaj
        self.is_core = is_core
        self.host_organization = host_organization
        self.host_organization_name = host_organization_name
        self.host_organization_lineage = (
            list(host_organization_lineage)
            if host_organization_lineage is not None
            else None
        )
        self.type = type
