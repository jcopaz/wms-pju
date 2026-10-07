# =============================================================================
# VIA WMS - models/__init__.py
# Importa TODOS os models para que o SQLAlchemy os registre no metadata.
# Assim `criar_tabelas()` enxerga todas as tabelas de uma vez.
# =============================================================================

from models.base import Base  # noqa: F401
from models.enums import *  # noqa: F401,F403
from models.organization import (  # noqa: F401
    OrganizationUnit,
    Role,
    SAPPlant,
    SAPStorageLocation,
    StorageLocation,
    User,
    UserRole,
    Warehouse,
)
from models.materials import (  # noqa: F401
    Material,
    MaterialBatch,
    MaterialSerial,
    UnitOfMeasure,
)
from models.partners import (  # noqa: F401
    AccountAssignment,
    Contract,
    Contractor,
    Recipient,
)
from models.stock import StockBalance  # noqa: F401
from models.movements import StockMovement, StockMovementItem  # noqa: F401
from models.custody import MaterialCustody, MaterialCustodyItem  # noqa: F401
from models.inventory import InventoryCount, InventorySession  # noqa: F401
from models.sap_integration import (  # noqa: F401
    Attachment,
    AuditLog,
    SAPImportBatch,
    SAPPosting,
)
