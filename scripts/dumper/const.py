# List of data types, sorted by ability to store data
type_BOOL = 1
type_INT = 2
type_FLOAT = 3
type_STR = 4
# List of reasons, stating why some data row was removed
removal_FILTER = 1  # Removed by explicit filter
removal_NO_REF_TO = 2  # Removed as nothing references it
removal_BROKEN_REF = 3  # Removed as contains broken references
# In-EVE constants
group_EFFECTBEACON = 920
category_SHIP = 6
category_MODULE = 7
category_CHARGE = 8
category_SKILL = 16
category_DRONE = 18
category_IMPLANT = 20
category_SUBSYSTEM = 32
attributeCategory_DEFATTR = 10  # Attributes' whose value references attribute via ID
attributeCategory_DEFTYPE = 11  # Attributes' whose value references type via ID
attributeCategory_DEFGROUP = 12  # Attributes' whose value references group via ID
