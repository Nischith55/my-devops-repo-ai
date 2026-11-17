from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel,Field

var_row_number = "Row Number"

class PlantSchema(BaseModel): # pragma: no cover
    """
    Schema for plant data including code, name, company, region, and status.
    Used for API requests and responses involving plant records.
    Fields map to the Plant model and support CRUD operations.
    Enables validation and serialization of plant-related data.
    Utilized in: plants.py
    """
    plant_id: int
    plant_code: str
    plant_name: str
    company_name: Optional[str] = None
    region_id: int
    status: str
    crop_category_id: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ExPlantSchemaDummy(BaseModel):  # pragma: no cover
    """
    Schema for a minimal plant representation with name and region.
    Used for lightweight plant lookups or dropdowns in the UI.
    Supports scenarios where only basic plant info is needed.
    Useful for reference and mapping operations.
    """
    plant_name: str
    region_id: int


class UpdatePlantSchema(BaseModel):  # pragma: no cover
    """
    Schema for updating plant records, excluding plant_id.
    Used in update endpoints to validate incoming plant data.
    Supports partial updates and ensures field consistency.
    Maps to the Plant model for update operations.
    Utilized in: masters_mapping_new.py
    """
    # plant_id: int
    plant_code: str
    plant_name: str
    company_name: Optional[str] = None
    region_id: int
    status: str
    crop_category_id: Optional[int] = None
    pgt_plant_name: str


class PlantSchemaDummy(BaseModel):  # pragma: no cover
    """
    Schema for plant data used in master mapping and reference.
    Excludes status and plant_id for simplified use cases.
    Used in nested schemas and mapping payloads.
    Supports UI and API scenarios requiring plant details.
    Utilized in: masters_mapping_new.py
    """
    # plant_id: int
    plant_code: str
    plant_name: str
    company_name: Optional[str] = None
    region_id: int
    # status: str
    crop_category_id: Optional[int] = None
    pgt_plant_name: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PlantSiteGrowingAreaMappingDummy(BaseModel):  # pragma: no cover
    """
    Schema for mapping plant names to growing areas and vendor site codes.
    Used in master mapping and plant-site association APIs.
    Supports validation and serialization of mapping data.
    Enables linking of plants, areas, and vendor sites in the UI.
    """
    plant_name: str
    growing_area: str
    Vendor_Site_Code: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GrowingAreaDummy(BaseModel):  # pragma: no cover
    """
    Schema for growing area dummy data, including status, country, and period/week info.
    Used for quick reference, dropdowns, and mapping operations.
    Supports UI forms and master data mapping.
    Enables validation of growing area attributes in lightweight scenarios.
    """
    ga_status: Optional[str] = "ACTIVE"
    country: str
    ga_desc: str
    fp_start: int
    fp_end: int
    fw_start: int
    fw_end: int
    sp_start: int
    sw_start: int


class VendorSiteCodeDummy(BaseModel):  # pragma: no cover
    """
    Schema for vendor site code dummy data, mainly for status.
    Used in master mapping and reference scenarios.
    Supports UI dropdowns and mapping payloads.
    Enables validation of vendor site code status.
    """
    vsc_status: Optional[str] = "ACTIVE"


class MastersMapping(BaseModel):  # pragma: no cover
    """
    Schema for master mapping of plant, site, growing area, and vendor site code.
    Used to aggregate and validate master data relationships.
    Supports complex payloads for master data APIs.
    Enables structured mapping between core master entities.
    Utilized in: masters_mapping_new.py
    """
    plant: PlantSchemaDummy
    psga_map: PlantSiteGrowingAreaMappingDummy
    growing_area: GrowingAreaDummy
    vsc: VendorSiteCodeDummy


class MastersMappingExPlant(BaseModel):# pragma: no cover
    """
    Schema for master mapping with ExPlant, site, growing area, and vendor site code.
    Used for export and reference scenarios with minimal plant info.
    Supports APIs requiring lightweight master data mapping.
    Enables structured export and mapping of master entities.
    Utilized in: masters_mapping_new.py
    """
    plant: ExPlantSchemaDummy
    psga_map: PlantSiteGrowingAreaMappingDummy
    growing_area: GrowingAreaDummy
    vsc: VendorSiteCodeDummy


class UpdateGrowingAreaSchema(BaseModel):# pragma: no cover
    """
    Schema for updating growing area records, including all editable fields.
    Used in update endpoints to validate growing area data.
    Supports partial and full updates of growing area attributes.
    Maps to the growing_area model for update operations.
    Utilized in: masters_mapping_new.py
    """
    growing_area_name: str
    region: int
    country: str
    status: str
    growing_area_desc: Optional[str] = None
    fresh_period_start: Optional[int] = None
    fresh_week_start: Optional[int] = None
    fresh_period_end: Optional[int] = None
    fresh_week_end: Optional[int] = None
    storage_period_start: Optional[int] = None
    storage_week_start: Optional[int] = None
    storage_period_end: Optional[int] = None
    storage_week_end: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    pgt_growing_area: str


class GrowingAreaSchemaMasters(BaseModel):# pragma: no cover
    """
    Schema for growing area master data, used in master mapping APIs.
    Includes all relevant growing area fields for reference and mapping.
    Supports UI forms and master data payloads.
    Enables validation and serialization of growing area master records.
    Utilized in: masters_mapping_new.py
    """
    growing_area_name: str
    region: int
    country: str
    growing_area_desc: Optional[str] = None
    fresh_period_start: Optional[int] = None
    fresh_week_start: Optional[int] = None
    fresh_period_end: Optional[int] = None
    fresh_week_end: Optional[int] = None
    storage_period_start: Optional[int] = None
    storage_week_start: Optional[int] = None
    storage_period_end: Optional[int] = None
    storage_week_end: Optional[int] = None
    pgt_growing_area: str


class GrowingAreaSchema(BaseModel):# pragma: no cover
    """
    Schema for growing area data, including ID, name, region, and status.
    Used for API requests and responses involving growing area records.
    Fields map to the growing_area model and support CRUD operations.
    Enables validation and serialization of growing area data.
    Utilized in: growingarea.py
    """
    growing_area_id: int
    growing_area_name: str
    region: int
    country: str
    status: str
    growing_area_desc: Optional[str] = None
    fresh_period_start: Optional[int] = None
    fresh_week_start: Optional[int] = None
    fresh_period_end: Optional[int] = None
    fresh_week_end: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class edit_gr_grarea_masters(BaseModel):# pragma: no cover
    """
    Schema for editing grower and growing area master mappings.
    Used to update associations between growers and multiple growing areas.
    Supports batch update operations in master data management.
    Enables validation of grower-to-area mapping payloads.
    Utilized in: masters_mapping_new.py
    """
    grower_name: str
    grower_id: int
    growing_area_name: List[str]
    growing_area_id: List[int]


class GrowersDummy(BaseModel):  # pragma: no cover
    """
    Schema for dummy grower data, including name, owner, region, and volume.
    Used for quick reference, dropdowns, and mapping operations.
    Supports UI forms and master data mapping.
    Enables validation of grower attributes in lightweight scenarios.
    Utilized in: masters_mapping_new.py
    """
    grower_name: str
    owner: str
    region: int
    country: str
    status: str
    volume: int
    grower_abbreviation_code: str
    pgt_grower_name: str

class GrowersDummyMulti(BaseModel):  # pragma: no cover
    """
    Schema for multi-grower dummy data, including parent and master IDs.
    Used for batch operations and hierarchical grower mapping.
    Supports UI and API scenarios requiring grower groupings.
    Enables validation of multi-grower mapping payloads.
    """
    grower_name: str
    owner: str
    region: int
    country: str
    status: str
    volume: int
    grower_abbreviation_code: str
    pgt_grower_name: str
    is_parent: str
    master_id: int


class GrAreaMapDummy(BaseModel):  # pragma: no cover
    """
    Schema for dummy growing area map, listing area names.
    Used for mapping growers to multiple growing areas.
    Supports UI forms and batch mapping operations.
    Enables validation of area mapping payloads.
    """
    growing_area_name: List[str]


class MastersMappingGrowers(BaseModel):  # pragma: no cover
    """
    Schema for master mapping of growers and growing area maps.
    Used to aggregate and validate grower-to-area relationships.
    Supports complex payloads for master data APIs.
    Enables structured mapping between growers and areas.
    Utilized in: masters_mapping_new.py
    """
    growers: GrowersDummy
    gr_area_map: GrAreaMapDummy


class ExGrowersDummy(BaseModel):  # pragma: no cover
    """
    Schema for grower data with old and new growing area names.
    Used for migration, mapping, and update scenarios.
    Supports UI and API operations involving area changes.
    Enables validation of grower area transition payloads.
    """
    grower_name: str
    ex_growing_area_name: str
    new_growing_area_name: str


class MastersMappingExGrowers(BaseModel):  # pragma: no cover
    """
    Schema for master mapping of growers with area transitions.
    Used for export and reference scenarios involving area changes.
    Supports APIs requiring grower area migration mapping.
    Enables structured export and mapping of grower transitions.
    Utilized in: masters_mapping_new.py
    """
    growers_gr_area: ExGrowersDummy


class GrowerSchema(BaseModel):# pragma: no cover
    """
    Schema for grower data, including name, owner, region, and volume.
    Used for API requests and responses involving grower records.
    Fields map to the growers model and support CRUD operations.
    Enables validation and serialization of grower data.
    Utilized in: growers.py
    """
    grower_name: str
    owner: str
    region: int
    country: str
    status: str
    volume: str
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Region(BaseModel):# pragma: no cover
    """
    Schema for region data, including name, country, and status.
    Used for API requests and responses involving region records.
    Fields map to the region model and support CRUD operations.
    Enables validation and serialization of region data.
    Utilized in: region.py
    """
    region_name: str
    country: str
    status: str
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UpdateRegion(BaseModel):# pragma: no cover
    """
    Schema for updating region records, including editable fields.
    Used in update endpoints to validate region data.
    Supports partial and full updates of region attributes.
    Maps to the region model for update operations.
    Utilized in: region.py
    """
    region: str
    country: Optional[str] = None
    status: Optional[str] = None
    updated_time: Optional[datetime] = None
    updated_by: Optional[str] = None


class PlantGrowingMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping plants to growing areas by their IDs.
    Used for associating plants with specific growing areas.
    Supports batch and single mapping operations in APIs.
    Enables validation of plant-to-area mapping payloads.
    Utilized in: plant_site_growing_area_mapping.py
    """
    plant_id: int
    growing_area_id: int


class ActiveAllocation(BaseModel):# pragma: no cover
    """
    Schema for active allocation data, including category, year, and volumes.
    Used for API requests and responses involving allocation records.
    Fields map to the allocation model and support CRUD operations.
    Enables validation and serialization of allocation data.
    Utilized in: allocation.py
    """
    allocation_id: str
    category_name: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    period: Optional[int] = None
    target_volume: Optional[float] = None
    actual_volume: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class AllocationPayload(BaseModel):# pragma: no cover
    """
    Schema for a payload containing a list of active allocations.
    Used for batch operations and bulk allocation updates.
    Supports API endpoints requiring multiple allocation records.
    Enables validation of allocation list payloads.
    Utilized in: allocation.py
    """
    data: List[ActiveAllocation]


class Category(BaseModel):# pragma: no cover
    """
    Schema for crop category data, including name, country, and status.
    Used for API requests and responses involving category records.
    Fields map to the category model and support CRUD operations.
    Enables validation and serialization of category data.
    Utilized in: category.py
    """
    category_name: str
    country: str
    status: str
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OwnershipGrowerGrowingSchema(BaseModel):# pragma: no cover
    """
    Schema for ownership-grower-growing area mapping, including contract and crop details.
    Used for API requests and responses involving ownership mappings.
    Fields map to the OwnershipGrowerGrowing model and support CRUD operations.
    Enables validation and serialization of ownership mapping data.
    Utilized in: OwnershipGrowerGrowing.py
    """
    row_id: str
    growing_area_id: Optional[int] = None
    grower_id: Optional[int] = None
    contract: Optional[int] = None
    year: Optional[int] = None
    shrinkage: Optional[float] = None
    shrinkage_volume: Optional[float] = None
    contract_erp: Optional[float] = None
    market: Optional[float] = None
    flex: Optional[float] = None
    ownership_id: str
    crop_type: Optional[str] = None
    crop_year: str
    status: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UpdateOwnershipGrowerGrowing(BaseModel):# pragma: no cover
    """
    Schema for updating a list of ownership-grower-growing area mappings.
    Used for batch update operations in ownership management APIs.
    Supports validation of multiple ownership mapping records.
    Enables efficient update of ownership mapping data.
    Utilized in: OwnershipGrowerGrowing.py
    """
    PayloadOwnership: List[OwnershipGrowerGrowingSchema]


class Pcusage(BaseModel):# pragma: no cover
    """
    Schema for PC usage data, including plant, period, week, and forecasted value.
    Used for API requests and responses involving PC usage records.
    Fields map to the pcusage model and support CRUD operations.
    Enables validation and serialization of PC usage data.
    Utilized in: pcusage.py
    """
    pcusage_id: str
    year: int
    period: int
    week_no: int
    plant_id: int
    forecasted_value: float
    country: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PlantSiteGrowingAreaMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for plant-site-growing area mapping, including all relevant IDs and codes.
    Used for API requests and responses involving plant-site mappings.
    Fields map to the PlantSiteGrowingAreaMapping model and support CRUD operations.
    Enables validation and serialization of mapping data.
    Utilized in: plant_site_growing_area_mapping.py
    """
    row_id: int
    vendor_site_code: str
    growing_area_code: str
    plant_name: str
    vendor_site_id: int
    plant_id: int
    growing_area_id: int


class EditPSGAMastersSchema(BaseModel):# pragma: no cover
    """
    Schema for editing plant-site-growing area master mappings.
    Used to update associations between plants, areas, and vendor sites.
    Supports batch update operations in master data management.
    Enables validation of plant-site-area mapping payloads.
    Utilized in: masters_mapping_new.py
    """
    plant_name: str
    plant_id: int
    growing_area: List[str]
    vsc: List[str]
    ga_id: List[int]
    vs_id: List[int]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightCostRateSchema(BaseModel):# pragma: no cover
    """
    Schema for freight cost rate details, including currency, miles, and audit fields.
    Used for API requests and responses involving freight cost rates.
    Supports CRUD operations and validation for freight cost rate records.
    Utilized in: freightcost.py
    """
    currency: Optional[str] = None
    comment: Optional[str] = None
    miles: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightCostMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping freight cost rates to years and round trips.
    Used for associating rates with specific years and trip types in APIs.
    Enables validation and serialization of freight cost mapping data.
    Utilized in: freightcost.py
    """
    year: Optional[int] = None
    rate: Optional[float] = None
    round_trip: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class FreightMilesSchema(BaseModel):# pragma: no cover
    """
    Schema for freight miles data, including period, year, country, and fuel coefficient.
    Used for API requests and responses involving freight miles calculations.
    Supports validation and serialization of freight miles records.
    Utilized in: freightcost.py
    """
    period: Optional[int] = None
    year: Optional[int] = None
    country: Optional[str] = None
    fuel_cf: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class FreightCostRatesSchema(BaseModel):# pragma: no cover
    """
    Schema for detailed freight cost rates, including plant, area, vendor site, and audit fields.
    Used for API requests and responses involving freight cost rates by location.
    Supports CRUD operations and validation for freight cost rate records.
    Utilized in: freightcost.py
    """
    plant_id: Optional[int] = None
    growing_area_id: Optional[int] = None
    vendor_site_id: Optional[int] = None
    currency: Optional[str] = None
    comment: Optional[str] = None
    miles: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class FreightMiles(BaseModel):# pragma: no cover
    """
    Schema for freight miles by plant, growing area, and vendor site.
    Used for mapping and calculating distances in logistics APIs.
    Supports validation and serialization of freight miles data.
    Utilized in: freightcost.py
    """
    plant_id: Optional[int] = None
    growing_area_id: Optional[int] = None
    vendor_site_id: Optional[int] = None
    miles: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OwnershipSchema(BaseModel):# pragma: no cover
    """
    Schema for ownership records, including contract, crop, and shipment details.
    Used for API requests and responses involving ownership and contract management.
    Supports CRUD operations and validation for ownership data.
    Utilized in: ownership.py
    """
    ownership_id: str
    growing_area_id: int
    contract: int
    contract_erp_value: Optional[int] = None
    shrinkage: float
    to_ship: int
    crop_type: str
    crop_year: str
    market_and_flex: Optional[int] = None
    total_ship: Optional[int] = None
    year: Optional[int] = None
    extension: Optional[float] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    final_extension: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PlantMatrix(BaseModel):# pragma: no cover
    """
    Schema for plant matrix data, including plant, area, period, and crop details.
    Used for API requests and responses involving plant matrix calculations.
    Supports validation and serialization of plant matrix records.
    Utilized in: plant_mtrx.py
    """
    plant_matrix_id: str
    plant_id: Optional[int] = None
    year: Optional[int] = None
    period: Optional[int] = None
    region_id: Optional[int] = None
    week: Optional[int] = None
    growing_area_id: Optional[int] = None
    value: Optional[float] = None
    crop_type: Optional[str] = None
    crop_year: Optional[str] = None
    status: Optional[str] = None
    type : Optional[str] = None
    update : Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UpdateOwnership(BaseModel):# pragma: no cover
    """
    Schema for updating ownership records in bulk.
    Contains a list of ownership data for batch update operations.
    Used in endpoints that process multiple ownership updates at once.
    Utilized in: ownership.py
    """
    DataContracted: List[OwnershipSchema]


class PlantMtrxPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of plant matrix records.
    Used for batch operations and bulk updates of plant matrix data.
    Enables validation of plant matrix list payloads.
    Utilized in: plant_mtrx.py
    """
    data: List[PlantMatrix]


class plantMtrx_template(BaseModel):# pragma: no cover
    """
    Schema for plant matrix template, specifying plant, period, week, area, and percentage value.
    Used for template-based plant matrix operations and UI forms.
    Enables validation of plant matrix template payloads.
    Utilized in: plant_mtrx_templt.py
    """
    plant_id: int
    period: int
    week_no: int
    growing_area_id: int
    percentage_value: float


class VendorSiteCodeSchemaMasters(BaseModel):# pragma: no cover
    """
    Schema for vendor site code master data, including region and code fields.
    Used for master data management and mapping in APIs.
    Supports validation and serialization of vendor site code master records.
    Utilized in: masters_mapping_new.py
    """
    VENDOR_SITE_CODE: Optional[str] = None
    region_id: Optional[int] = None
    pgt_vsc: str


class UpdateVendorSiteCodeSchema(BaseModel):# pragma: no cover
    """
    Schema for updating vendor site code records, including audit and status fields.
    Used for update endpoints and validation of vendor site code data.
    Supports partial and full updates of vendor site code attributes.
    Utilized in: masters_mapping_new.py
    """
    VENDOR_SITE_CODE: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    status: Optional[str] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None
    region_id: Optional[int] = None
    pgt_vsc: str


class VendorSiteCodeSchema(BaseModel):# pragma: no cover
    """
    Schema for vendor site code data, including audit and region fields.
    Used for API requests and responses involving vendor site code records.
    Supports CRUD operations and validation for vendor site code data.
    Utilized in: vendor_site_code.py
    """
    VENDOR_SITE_CODE: Optional[int] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    status: Optional[str] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None
    region_id: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class SolidRatesSchema(BaseModel):# pragma: no cover
    """
    Schema for solid rates, including year, area, currency, and audit fields.
    Used for API requests and responses involving solid rate records.
    Supports CRUD operations and validation for solid rate data.
    Utilized in: solidrates.py
    """
    year: Optional[int] = None
    growing_area_id: Optional[int] = None
    currency: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


class PotatoRatesSchema(BaseModel):# pragma: no cover
    """
    Schema for potato rates, including year, area, currency, and audit fields.
    Used for API requests and responses involving potato rate records.
    Supports CRUD operations and validation for potato rate data.
    Utilized in: potatorates.py
    """
    year: Optional[int] = None
    growing_area_id: Optional[int] = None
    currency: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


class potatoRateMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping potato rates to periods, weeks, and years.
    Used for associating rates with specific timeframes in APIs.
    Supports validation and serialization of potato rate mapping data.
    Utilized in: potatorates.py
    """
    __tablename__ = "potato_rate_mapping"
    period: Optional[int] = None
    potato_rate_id: Optional[int] = None
    week: Optional[int] = None
    p_year: Optional[int] = None
    rate: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class potatoRateMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of potato rate mappings.
    Used for batch operations and bulk updates of potato rate mapping data.
    Enables validation of potato rate mapping list payloads.
    Utilized in: potatorates.py
    """
    data: List[potatoRateMappingSchema]


class solidRateMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping solid rates to periods and years.
    Used for associating solid rates with specific timeframes in APIs.
    Supports validation and serialization of solid rate mapping data.
    Utilized in: solidrates.py
    """
    __tablename__ = "solid_rate_mapping"
    period: Optional[int] = None
    solids_rate_id: Optional[int] = None
    rate: Optional[float] = None
    period_year: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class solidRateMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of solid rate mappings.
    Used for batch operations and bulk updates of solid rate mapping data.
    Enables validation of solid rate mapping list payloads.
    Utilized in: solidrates.py
    """
    data: List[solidRateMappingSchema]


class OffContractInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for off-contract task information, including name, description, status, and audit fields.
    Used for API requests and responses involving off-contract tasks.
    Supports CRUD operations and validation for off-contract task data.
    Utilized in: offcontractinfo.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None
    order_position: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OffContractTaskMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping off-contract tasks to periods, years, and companies.
    Used for associating off-contract tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of off-contract task mapping data.
    Utilized in: offcontractinfo.py
    """
    period: Optional[int] = None
    off_contract_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OffContractTaskMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of off-contract task mappings.
    Used for batch operations and bulk updates of off-contract task mapping data.
    Enables validation of off-contract task mapping list payloads.
    Utilized in: offcontractinfo.py
    """
    data: List[OffContractTaskMappingSchema]
    
class OffContractPlanInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for off-contract plan task information, including name, description, status, and audit fields.
    Used for API requests and responses involving off-contract plan tasks.
    Supports CRUD operations and validation for off-contract plan task data.
    Utilized in: offcontractplaninfo.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OffContractPlanTaskMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping off-contract plan tasks to periods, years, and companies.
    Used for associating off-contract plan tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of off-contract plan task mapping data.
    Utilized in: offcontractplaninfo.py
    """
    period: Optional[int] = None
    off_contract_plan_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class OffContractPlanTaskMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of off-contract plan task mappings.
    Used for batch operations and bulk updates of off-contract plan task mapping data.
    Enables validation of off-contract plan task mapping list payloads.
    Utilized in: offcontractplaninfo.py
    """
    data: List[OffContractPlanTaskMappingSchema]


class FreightTaskInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for freight task information, including name, description, status, and audit fields.
    Used for API requests and responses involving freight tasks.
    Supports CRUD operations and validation for freight task data.
    Utilized in: freighttaskinfo.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightTaskMappingsSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping freight tasks to periods, years, and companies.
    Used for associating freight tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of freight task mapping data.
    Utilized in: freighttaskinfo.py
    """
    period: Optional[int] = None
    freight_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightTaskMappingsPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of freight task mappings.
    Used for batch operations and bulk updates of freight task mapping data.
    Enables validation of freight task mapping list payloads.
    Utilized in: freighttaskinfo.py
    """
    data: List[FreightTaskMappingsSchema]
    

class FreightTaskPlanInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for freight task plan information, including name, description, status, and audit fields.
    Used for API requests and responses involving freight task plan tasks.
    Supports CRUD operations and validation for freight task plan data.
    Utilized in: freighttaskplaninfo.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightTaskPlanMappingsSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping freight task plan tasks to periods, years, and companies.
    Used for associating freight task plan tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of freight task plan mapping data.
    Utilized in: freighttaskplaninfo.py
    """
    period: Optional[int] = None
    freight_task_plan_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FreightTaskPlanMappingsPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of freight task plan mappings.
    Used for batch operations and bulk updates of freight task plan mapping data.
    Enables validation of freight task plan mapping list payloads.
    Utilized in: freighttaskplaninfo.py
    """
    data: List[FreightTaskPlanMappingsSchema]


class GeneralAdministrativeTaskSchema(BaseModel):# pragma: no cover
    """
    Schema for general administrative task information, including name, description, status, and audit fields.
    Used for API requests and responses involving general administrative tasks.
    Supports CRUD operations and validation for general administrative task data.
    Utilized in: generaladministrative.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GeneralAdministrativeMappingsSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping general administrative tasks to periods, years, and companies.
    Used for associating general administrative tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of general administrative mapping data.
    Utilized in: generaladministrative.py
    """
    period: Optional[int] = None
    general_administrative_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GeneralAdministrativeMappingsPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of general administrative mappings.
    Used for batch operations and bulk updates of general administrative mapping data.
    Enables validation of general administrative mapping list payloads.
    Utilized in: generaladministrative.py
    """
    data: List[GeneralAdministrativeMappingsSchema]
    
class GeneralAdministrativePlanTaskSchema(BaseModel):# pragma: no cover
    """
    Schema for general administrative plan task information, including name, description, status, and audit fields.
    Used for API requests and responses involving general administrative plan tasks.
    Supports CRUD operations and validation for general administrative plan task data.
    Utilized in: generaladministrative_plan.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GeneralAdministrativePlanMappingsSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping general administrative plan tasks to periods, years, and companies.
    Used for associating general administrative plan tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of general administrative plan mapping data.
    Utilized in: generaladministrative_plan.py
    """
    period: Optional[int] = None
    general_administrative_plan_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class GeneralAdministrativePlanMappingsPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of general administrative plan mappings.
    Used for batch operations and bulk updates of general administrative plan mapping data.
    Enables validation of general administrative plan mapping list payloads.
    Utilized in: generaladministrative_plan.py
    """
    data: List[GeneralAdministrativePlanMappingsSchema]


class ExtensionMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for extension ownership mapping, including extension, area, period, crop, and plant distribution details.
    Used for API requests and responses involving extension allocation and mapping.
    Supports CRUD operations and validation for extension mapping data.
    Utilized in: extensionMapping.py
    """
    extension_id: str
    growing_area_id: Optional[int] = None
    period: Optional[int] = None
    week: Optional[int] = None
    crop_type: Optional[str] = None
    crop_year: Optional[str] = None
    total_value: Optional[float] = None
    split: str
    year: int
    status: Optional[str] = None
    plant_distribution: Optional[List[dict]] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ExtensionOwnershipPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of extension mappings.
    Used for batch operations and bulk updates of extension mapping data.
    Enables validation of extension mapping list payloads.
    Utilized in: extensionMapping.py
    """
    ExtensionData: List[ExtensionMappingSchema]

class ExtensionMappingDeleteSchema(BaseModel):# pragma: no cover
    """
    Schema for deleting extension mappings in bulk, specifying crop year, year, and region.
    Used for batch delete operations in extension allocation APIs.
    Enables validation of bulk extension mapping delete payloads.
    Utilized in: extensionMapping.py
    """
    crop_year: str
    year: int
    region: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class ExtensionMappingMultiPlantSchema(BaseModel):# pragma: no cover
    """
    Schema for multi-selecting plants for extension allocation, including extension, area, period, and crop details.
    Used for batch allocation of extensions to multiple plants in APIs.
    Enables validation of multi-plant extension allocation payloads.
    Utilized in: extensionMapping.py
    """
    extension_id: str
    growing_area_id: Optional[int] = None
    period: Optional[int] = None
    week: Optional[int] = None
    crop_type: Optional[str] = None
    crop_year: Optional[str] = None
    year: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PriceVarianceMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping price variance tasks to periods, years, and companies.
    Used for associating price variance tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of price variance mapping data.
    Utilized in: summary_price_variance.py
    """
    period: Optional[int] = None
    price_variance_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PriceVarianceMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of price variance mappings.
    Used for batch operations and bulk updates of price variance mapping data.
    Enables validation of price variance mapping list payloads.
    Utilized in: summary_price_variance.py
    """
    data: List[PriceVarianceMappingSchema]


class InflationDeflationMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping inflation/deflation tasks to periods, years, and companies.
    Used for associating inflation/deflation tasks with specific timeframes and companies in APIs.
    Utilized in: inflation_deflation.py
    """
    period: Optional[int] = None
    inflation_deflation_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class InflationDeflationMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of inflation/deflation task mappings.
    Used for batch operations and bulk updates of inflation/deflation mapping data.
    Utilized in: inflation_deflation.py
    """
    data: List[InflationDeflationMappingSchema]


class p4pMasterInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for P4P master information, including name, description, status, and audit fields.
    Used for API requests and responses involving P4P master records.
    Utilized in: p4p_master_info.py
    """
    p4p_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class p4pTaskMappingsSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping P4P tasks to periods, years, and companies.
    Used for associating P4P tasks with specific timeframes and companies in APIs.
    Utilized in: p4p_master_info.py
    """
    period: Optional[int] = None
    p4p_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class p4pTaskMappingsPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of P4P task mappings.
    Used for batch operations and bulk updates of P4P task mapping data.
    Utilized in: p4p_master_info.py
    """
    data: List[p4pTaskMappingsSchema]


class TaskItemDataObject(BaseModel):# pragma: no cover
    """
    Schema for task item data, including plan and actuals values.
    Used for representing individual task metrics in API payloads.
    Utilized in: p4p_master_info.py
    """
    plan: int
    actuals: int


class TaskItemPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing task IDs and associated solids/defects data.
    Used for batch operations and updates of task metrics.
    Utilized in: p4p_master_info.py
    """
    taskId: int
    solids: TaskItemDataObject
    defects: TaskItemDataObject


class MarketFlexMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping market flex values to growers, areas, and ownerships.
    Used for associating market flex data with specific entities in APIs.
    """
    row_id: str
    growing_area_id: Optional[int] = None
    grower_id: Optional[int] = None
    ownership_id: Optional[str] = None
    status: Optional[str] = None
    market_flex_value: Optional[int] = None


class SolidTaskMasterSchema(BaseModel):# pragma: no cover
    """
    Schema for solid task master data, including name, description, status, and audit fields.
    Used for API requests and responses involving solid task master records.
    Utilized in: summary_solids.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None
    order_position: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class MarketFlexPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of market flex mappings.
    Used for batch operations and bulk updates of market flex data.
    Enables validation of market flex mapping list payloads.
    Utilized in: MarketFlexMapping.py
    """
    Payload_MarketFlex: List[MarketFlexMappingSchema]


class SolidsTaskMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping solids tasks to periods, years, and country codes.
    Used for associating solids tasks with specific timeframes in APIs.
    Supports validation and serialization of solids task mapping data.
    Utilized in: summary_solids.py
    """
    period: Optional[int] = None
    solids_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    country_code: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class SolidsTaskMappingSchemaPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of solids task mappings.
    Used for batch operations and bulk updates of solids task mapping data.
    Enables validation of solids task mapping list payloads.
    Utilized in: summary_solids.py
    """
    data: List[SolidsTaskMappingSchema]


class CountryDivisionNameName(BaseModel):# pragma: no cover
    """
    Schema for country division name data, including division name, task description, and status.
    Used for API requests and responses involving country division records.
    Supports CRUD operations and validation for country division data.
    """
    division_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None


class PlantMtrxTemplateSchema(BaseModel):# pragma: no cover
    """
    Schema for plant matrix template data, including period, plant, week, and growing area IDs.
    Used for template-based plant matrix operations and UI forms.
    Enables validation of plant matrix template payloads.
    Utilized in: plant_mtrx_templt.py
    """
    period: Optional[int] = None
    plant_id: Optional[int] = None
    week: Optional[int] = None
    growing_area_id: Optional[int] = None


class planVolumeUsageSchema(BaseModel):# pragma: no cover
    """
    Schema for plan volume usage data, including crop type, period, week, year, and volume.
    Used for API requests and responses involving volume usage planning records.
    Supports CRUD operations and validation for plan volume usage data.
    Utilized in: dashboard.py
    """
    __tablename__ = "plan_volume_usage"
    plan_volume_id: str
    crop_type: Optional[int] = None
    period: Optional[int] = None
    week: Optional[int] = None
    year: Optional[int] = None
    volume: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class planVolumeUsagePayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of plan volume usage records.
    Used for batch operations and bulk updates of plan volume usage data.
    Enables validation of plan volume usage list payloads.
    Utilized in: dashboard.py
    """
    data: List[planVolumeUsageSchema]

class pcVolumePlanUsageSchema(BaseModel):
    """
    Schema for PC volume plan usage data, including crop type, period, week, year, and volume.
    Used for API requests and responses involving PC volume plan usage records.
    Supports CRUD operations and validation for PC volume plan usage data.
    Utilized in: dashboard_plan.py
    """
    __tablename__ = "pc_volume_usage_plan"
    pc_volume_plan_id: str
    crop_type: Optional[int] = None
    period: Optional[int] = None
    week: Optional[int] = None
    year: Optional[int] = None
    volume: Optional[float] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class pcVolumePlanUsagePayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of PC volume plan usage records.
    Used for batch operations and bulk updates of PC volume plan usage data.
    Enables validation of PC volume plan usage list payloads.
    Utilized in: dashboard_plan.py
    """
    data: List[pcVolumePlanUsageSchema]


class UserInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for user information data, including email, country, name, and status.
    Used for API requests and responses involving user records.
    Supports CRUD operations and validation for user information data.
    Utilized in: user_info.py
    """
    email: Optional[str] = None
    country: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_status: Optional[bool] = None
    is_admin: Optional[bool] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class EditActiveStatusSchema(BaseModel):# pragma: no cover
    """
    Schema for editing user active status, including email and status flag.
    Used for API requests to update user active/inactive status.
    Supports validation of user status update payloads.
    Utilized in: user_info.py
    """
    email: Optional[str] = None
    user_status: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
class NewUserInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for new user information data, including email, page, access, and country.
    Used for API requests involving new user creation and page mapping.
    Supports validation of new user information payloads.
    Utilized in: user_info.py
    """
    email: Optional[str] = None
    page_name: Optional[str] = None
    access_name: Optional[str] = None
    country_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class NewUserInfoPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of new user information records.
    Used for batch operations and bulk creation of new user mappings.
    Enables validation of new user information list payloads.
    Utilized in: user_info.py
    """
    data: List[NewUserInfoSchema]        

class UserCreationPayload(BaseModel):# pragma: no cover
    """
    Schema for user creation payload, including email and admin flag.
    Used for API requests involving user creation operations.
    Supports validation of user creation payloads.
    Utilized in: user_info.py
    """
    email: Optional[str] = None
    is_admin: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UpdateUserInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for updating user information, including email, page, access, country, and admin flag.
    Used for API requests involving user information updates.
    Supports validation of user update payloads.
    Utilized in: user_info.py
    """
    email: Optional[str] = None
    page_name: Optional[str] = None
    access_name: Optional[str] = None
    country_name: Optional[str] = None
    is_admin: Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class UpdateUserInfoPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of user information updates.
    Used for batch operations and bulk updates of user information data.
    Enables validation of user update list payloads.
    Utilized in: user_info.py
    """
    data: List[UpdateUserInfoSchema] 


class CountryInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for country information data, including country name.
    Used for API requests and responses involving country records.
    Supports CRUD operations and validation for country information data.
    Utilized in: page_info.py
    """
    country_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class AccessInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for access information data, including access name and value.
    Used for API requests and responses involving access type records.
    Supports CRUD operations and validation for access information data.
    Utilized in: page_info.py
    """
    access_name: Optional[str] = None
    access_value: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class PageInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for page information data, including page name, description, status, and audit fields.
    Used for API requests and responses involving page records.
    Supports CRUD operations and validation for page information data.
    Utilized in: page_info.py
    """
    page_name: Optional[str] = None
    page_description: Optional[str] = None
    page_status: Optional[bool] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None
    is_read_only:Optional[bool] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UserlogSchema(BaseModel):# pragma: no cover
    """
    Schema for user log data, including email, date/time, and date.
    Used for API requests and responses involving user activity logs.
    Supports CRUD operations and validation for user log data.
    Utilized in: user_log.py
    """
    email: str
    date_time: datetime
    date: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class ExportExcelPayloadSchema(BaseModel): # pragma: no cover
    """
    Schema for export Excel payload, including payload ID and payload data.
    Used for API requests involving Excel export operations.
    Supports validation of export payload data.
    Utilized in: export_excel.py
    """
    Payload_ID: int
    Payload: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
    

class ExportExcelFinanceSummarySolids(BaseModel): # pragma: no cover
    """
    Schema for finance summary solids export data, including conversion factor, impact values, and forecast data.
    Used for Excel export operations involving finance summary solids metrics.
    Supports validation and serialization of finance summary solids export data.
    Utilized in: export_excel.py
    """
    conversion_factor: float= Field(..., alias="Conversion_Factor")
    delta_m_imp: float= Field(..., alias="Delta M$ Imp")
    fore_plan: float =Field(..., alias="FORE_PLAN")
    m_dollar_impact: float =Field(..., alias="M_dollar_IMPACT")
    m_dollar_impact_plan: float=Field(..., alias="M_dollar_Impact-Plan")
    plan: float=Field(..., alias="Plan")
    yag_index: float=Field(..., alias="YAG_Index")
    country_code: str
    fcst_act: float
    forecast: float
    period: int
    prior: float
    year: int

   

class ExportExcelFinanceSummarySolidsList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of finance summary solids export records.
    Used for batch Excel export operations involving finance summary solids data.
    Enables validation of finance summary solids export list payloads.
    Utilized in: export_excel.py
    """
    data: List[ExportExcelFinanceSummarySolids]

class ExportExcelPlantMatrixAllocation(BaseModel): # pragma: no cover
    """
    Schema for plant matrix allocation export data, including crop, growing area, period, and plant details.
    Used for Excel export operations involving plant matrix allocation records.
    Supports validation and serialization of plant matrix allocation export data.
    Utilized in: export_excel.py
    """
    Export_date: Optional[str] = None
    crop_type: Optional[str] = None
    crop_year:Optional[str] = None
    growing_area_id: int
    growing_area_name: str
    period: int
    period_with_P: str
    plant_id: int
    plant_matrix_id: str
    plant_name: str
    value: Optional[float] = None
    week: int
    year: int

class ExportExcelPlantMatrixAllocationList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of plant matrix allocation export records.
    Used for batch Excel export operations involving plant matrix allocation data.
    Enables validation of plant matrix allocation export list payloads.
    Utilized in: export_excel.py
    """
    data: List[ExportExcelPlantMatrixAllocation]

class ExportExcelOwnership(BaseModel): # pragma: no cover
    """
    Schema for ownership export data, including A2S, contract, demand, extension, flex, and position.
    Used for Excel export operations involving ownership records.
    Supports validation and serialization of ownership export data.
    Utilized in: export_excel.py
    """
    A2S: str
    Contract: str
    Demand: str
    Extension: str
    Flex: str
    Growing_Area: str
    Market: str
    Position: str
    Shrinkage: str
    To_Ship: str

class ExportExcelOwnershipList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of ownership export records.
    Used for batch Excel export operations involving ownership data.
    Enables validation of ownership export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelOwnership]

class ExportExcelplantmatrixregionweek(BaseModel): # pragma: no cover
    """
    Schema for plant matrix region week export data, including period, region, and total value.
    Used for Excel export operations involving plant matrix region-week records.
    Supports validation and serialization of region-week export data.
    Utilized in: export_excel.py
    """
    period: int
    Export_date: Optional[str] = None
    period_with_P: str
    region_name: str
    totalValue_regionWise: Optional[float] = None
    week: int
    year: int

class ExportExcelplantmatrixregionweekList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of plant matrix region-week export records.
    Used for batch Excel export operations involving region-week data.
    Enables validation of region-week export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelplantmatrixregionweek]

class ExportExcelplantmatrixgrowerweek(BaseModel): # pragma: no cover
    """
    Schema for plant matrix grower week export data, including crop, growing area, period, and total value.
    Used for Excel export operations involving plant matrix grower-week records.
    Supports validation and serialization of grower-week export data.
    Utilized in: export_excel.py
    """
    crop_type: Optional[str] = None
    Export_date: Optional[str] = None
    crop_year: Optional[str] = None
    growing_area_id: int
    growing_area_name: str
    period: int
    period_with_P: str
    total_value: Optional[float] = None
    week: int
    year: int

class ExportExcelplantmatrixgrowerweekList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of plant matrix grower-week export records.
    Used for batch Excel export operations involving grower-week data.
    Enables validation of grower-week export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelplantmatrixgrowerweek]

class ExportExcelForecast(BaseModel): # pragma: no cover
    """
    Schema for forecast export data, including period, plant, and actual/forecast values.
    Used for Excel export operations involving forecast records.
    Supports validation and serialization of forecast export data.
    Utilized in: export_excel.py
    """
    Period_with_P: str
    period: int
    plant_id: int
    plant_name: str
    total_actual_value: Optional[float] = None
    total_forecast_value: Optional[float] = None
    week: int
    year: int

class ExportExcelForecastList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of forecast export records.
    Used for batch Excel export operations involving forecast data.
    Enables validation of forecast export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelForecast]

class ExportExcelInflationDeflation(BaseModel): # pragma: no cover
    """
    Schema for inflation/deflation export data, including impact, index, and prior year comparisons.
    Used for Excel export operations involving inflation/deflation records.
    Supports validation and serialization of inflation/deflation export data.
    Utilized in: export_excel.py
    """
    impact_bw_vs_prior_year: float = Field(..., alias="IMPACT B/W vs Prior Year ($)")
    index: float = Field(..., alias="Index (%)")
    index_frt: float = Field(..., alias="Index (%) -FRT")
    index_mat: float = Field(..., alias="Index (%) -MAT")
    bw_than_py_frt: float = Field(..., alias="b/(w) than py frt ($/u)")
    bw_than_py_matl: float = Field(..., alias="b/(w) than py matl ($/u)")
    bw_than_py_total: float = Field(..., alias="b/(w) than py total ($/u)")
    company_name: str
    freight: float
    freight_prev: float
    material: float
    material_prev: float
    period: int
    total: float
    total_prior: float
    year: int

class ExportExcelInflationDeflationList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of inflation/deflation export records.
    Used for batch Excel export operations involving inflation/deflation data.
    Enables validation of inflation/deflation export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelInflationDeflation]

class ExportExcelPvp(BaseModel): # pragma: no cover
    """
    Schema for price variance plan (PVP) export data, including freight, material, and impact values.
    Used for Excel export operations involving price variance plan records.
    Supports validation and serialization of PVP export data.
    Utilized in: export_excel.py
    """
    FREIGHT_BW_per_unit: float= Field(..., alias="FREIGHT B/(W) ($/unit)")
    IMPACT_BW_vs_Plan: float= Field(..., alias="IMPACT B/W vs Plan ($)")
    Index_percent: float= Field(..., alias="Index (%)")
    Index_percent_FRT: float= Field(..., alias="Index (%) -FRT")
    Index_percent_MAT: float= Field(..., alias="Index (%) -MAT")
    MATERIAL_BW_per_unit: float= Field(..., alias="MATERIAL B/(W) ($/unit)")
    MCWT_Volume: float
    TOTAL_per_unit: float= Field(..., alias="TOTAL ($/unit)")
    company_name: str
    m_dollar_impact: float
    period: int
    total_actual: float
    total_freight_cost_actual: float
    total_freight_cost_plan: float
    total_material_actual: float
    total_material_plan: float
    total_plan: float
    year: int

class ExportExcelPvpList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of PVP export records.
    Used for batch Excel export operations involving price variance plan data.
    Enables validation of PVP export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelPvp]

class ExportExcelPvpPv(BaseModel): # pragma: no cover
    """
    Schema for PVP price variance export data, including company, period, and task details.
    Used for Excel export operations involving price variance records.
    Supports validation and serialization of price variance export data.
    Utilized in: export_excel.py
    """
    company_name: str= Field(..., alias="company-name")
    period: int
    period_with_P: str
    price_variance_task_id: int
    value: float
    year: int

class ExportExcelPvpPvList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of PVP price variance export records.
    Used for batch Excel export operations involving price variance data.
    Enables validation of price variance export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelPvpPv]

class ExportOffContract(BaseModel): # pragma: no cover
    """
    Schema for off-contract export data, including company, task IDs, period, and value.
    Used for Excel export operations involving off-contract records.
    Supports validation and serialization of off-contract export data.
    Utilized in: export_excel.py
    """
    company_name: str
    off_contract_task_id: Optional[int] = None
    off_contract_plan_task_id: Optional[int] = None
    period: int
    row_id: int
    value: int
    year: int

class ExportOffContractList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of off-contract export records.
    Used for batch Excel export operations involving off-contract data.
    Enables validation of off-contract export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportOffContract]

class ExportExcelAdjustmentsFreight(BaseModel): # pragma: no cover
    """
    Schema for freight adjustments export data, including company, task IDs, period, and value.
    Used for Excel export operations involving freight adjustment records.
    Supports validation and serialization of freight adjustments export data.
    Utilized in: export_excel.py
    """
    company_name: str
    freight_task_id: Optional[int] = None
    freight_task_plan_id:Optional[int] = None
    period: int
    row_id: int
    value: Optional[float] = None
    year: int

class ExportExcelAdjustmentsFreightList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of freight adjustments export records.
    Used for batch Excel export operations involving freight adjustments data.
    Enables validation of freight adjustments export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAdjustmentsFreight]

class ExportExcelAdjustmentsP4P(BaseModel): # pragma: no cover
    """
    Schema for P4P adjustments export data, including defects, solids, and diff values.
    Used for Excel export operations involving P4P adjustment records.
    Supports validation and serialization of P4P adjustments export data.
    Utilized in: export_excel.py
    """
    company_name: str
    defects_actual: int= Field(..., alias="defects-actual")
    defects_plan: int= Field(..., alias="defects-plan")
    diff_Defects: int
    diff_solid: int
    p4pDiff: int
    p_year: int
    periods: int
    ptdActualP4P: int
    solid_actual: int= Field(..., alias="solid-actual")
    solid_plan: int= Field(..., alias="solid-plan")
    total: int

class ExportExcelAdjustmentsP4PList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of P4P adjustments export records.
    Used for batch Excel export operations involving P4P adjustments data.
    Enables validation of P4P adjustments export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAdjustmentsP4P]

class ExportExcelAdjustmentsGA(BaseModel): # pragma: no cover
    """
    Schema for general administrative adjustments export data, including company, task ID, period, and value.
    Used for Excel export operations involving GA adjustment records.
    Supports validation and serialization of GA adjustments export data.
    Utilized in: export_excel.py
    """
    company_name: str
    general_administrative_id: int
    period: int
    row_id: int
    value: int
    year: int

class ExportExcelAdjustmentsGAList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of GA adjustments export records.
    Used for batch Excel export operations involving GA adjustments data.
    Enables validation of GA adjustments export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAdjustmentsGA]

class ExportExcelAdjustmentsGAplan(BaseModel): # pragma: no cover
    """
    Schema for GA plan adjustments export data, including company, plan task ID, period, and value.
    Used for Excel export operations involving GA plan adjustment records.
    Supports validation and serialization of GA plan adjustments export data.
    Utilized in: export_excel.py
    """
    company_name: str
    general_administrative_plan_id: int
    period: int
    row_id: int
    value: int
    year: int

class ExportExcelAdjustmentsGAplanList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of GA plan adjustments export records.
    Used for batch Excel export operations involving GA plan adjustments data.
    Enables validation of GA plan adjustments export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAdjustmentsGAplan]

class ExportExcelAdjustmentsBTL(BaseModel): # pragma: no cover
    """
    Schema for BTL adjustments export data, including task ID, company, period, and value.
    Used for Excel export operations involving BTL adjustment records.
    Supports validation and serialization of BTL adjustments export data.
    Utilized in: export_excel.py
    """
    btl_task_id: int
    company_name: str
    period: int
    row_id: int
    value: int
    year: int

class ExportExcelAdjustmentsBTLList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of BTL adjustments export records.
    Used for batch Excel export operations involving BTL adjustments data.
    Enables validation of BTL adjustments export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAdjustmentsBTL]

class ExportExcelAdjustmentsBTLplan(BaseModel): # pragma: no cover
    """
    Schema for BTL plan adjustments export data, including plan task ID, company, period, and value.
    Used for Excel export operations involving BTL plan adjustment records.
    Supports validation and serialization of BTL plan adjustments export data.
    Utilized in: export_excel.py
    """
    btl_plan_task_id: int
    company_name: str
    period: int
    row_id: int
    value: int
    year: int

class ExportExcelAdjustmentsBTLplanList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of BTL plan adjustments export records.
    Used for batch Excel export operations involving BTL plan adjustments data.
    Enables validation of BTL plan adjustments export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAdjustmentsBTLplan]

class ExportExcelAdjustmentsProductivity(BaseModel): # pragma: no cover
    """
    Schema for productivity adjustments export data, including company, period, task ID, and value.
    Used for Excel export operations involving productivity adjustment records.
    Supports validation and serialization of productivity adjustments export data.
    Utilized in: export_excel.py
    """
    company_name: str
    period: int
    productivity_task_id: int
    row_id: int
    value: int
    year: int

class ExportExcelAdjustmentsProductivityList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of productivity adjustments export records.
    Used for batch Excel export operations involving productivity adjustments data.
    Enables validation of productivity adjustments export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAdjustmentsProductivity]

class ExportExcelAdjustmentsProductivityPlan(BaseModel): # pragma: no cover
    """
    Schema for productivity plan adjustments export data, including company, period, plan task ID, and value.
    Used for Excel export operations involving productivity plan adjustment records.
    Supports validation and serialization of productivity plan adjustments export data.
    Utilized in: export_excel.py
    """
    company_name: str
    period: int
    productivity_plan_task_id: int
    row_id: int
    value: int
    year: int

class ExportExcelAdjustmentsProductivityPlanList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of productivity plan adjustments export records.
    Used for batch Excel export operations involving productivity plan adjustments data.
    Enables validation of productivity plan adjustments export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAdjustmentsProductivityPlan]

class ExportExcelAFreightRateVendorSiteCode(BaseModel): # pragma: no cover
    """
    Schema for freight rate vendor site code export data, including business unit, vendor site, and rate details.
    Used for Excel export operations involving freight rate vendor site code records.
    Supports validation and serialization of freight rate vendor site code export data.
    Utilized in: export_excel.py
    """
    business_unit: Optional[str] = None
    vendor_site_code: Optional[str] = None
    company_name: Optional[str] = None
    freight_cost_id: int
    fuel_cf: float
    growing_area: Optional[str] = None
    growing_area_id: int
    miles: int
    period: int
    period_with_P: str
    plant_id: int
    plant_name: Optional[str] = None
    rate: float
    round_trip: int
    vendor_site_id: int
    year: int

class ExportExcelAFreightRateVendorSiteCodeList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of freight rate vendor site code export records.
    Used for batch Excel export operations involving freight rate vendor site code data.
    Enables validation of freight rate vendor site code export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelAFreightRateVendorSiteCode]

class ExportExcelFreightRateperiod(BaseModel): # pragma: no cover
    """
    Schema for freight rate period export data, including actual/forecast spend and volume by period.
    Used for Excel export operations involving freight rate period records.
    Supports validation and serialization of freight rate period export data.
    Utilized in: export_excel.py
    """
    Row_Number: int= Field(..., alias=var_row_number)
    actual_dollar_bymcwt: float
    actual_total_dollar_spend: float
    actual_volume: float
    company_name: str
    country: str
    forecast_dollar_bymcwt: float
    forecast_total_dollar_spend: float
    forecast_volume: float
    p_year: int
    period: int
    period_with_P: str
    plant_id: int
    plant_name: str
    week: str

class ExportExcelFreightRateperiodList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of freight rate period export records.
    Used for batch Excel export operations involving freight rate period data.
    Enables validation of freight rate period export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelFreightRateperiod]

class ExportExcelFreightRateweek(BaseModel): # pragma: no cover
    """
    Schema for freight rate week export data, including actual/forecast spend and volume by week.
    Used for Excel export operations involving freight rate weekly records.
    Supports validation and serialization of freight rate week export data.
    Utilized in: export_excel.py
    """
    Total_dollor_spend_week: float
    actual_dollor_MCWT_week: float
    actual_volume: float
    company_name: str
    country: str
    forecast_dollor_cwt: float
    forecast_spend_week: float
    forecast_volume: float
    p_year: int
    period: int
    period_with_P: str
    period_with_week: str
    plant_id: int
    plant_name: str
    rate: float
    week_no: int

class ExportExcelFreightRateweekList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of freight rate week export records.
    Used for batch Excel export operations involving freight rate weekly data.
    Enables validation of freight rate week export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelFreightRateweek]

class ExportExcelFreightRateGrowingArea(BaseModel): # pragma: no cover
    """
    Schema for freight rate growing area export data, including growing area, rates, and dollar CWT.
    Used for Excel export operations involving freight rate growing area records.
    Supports validation and serialization of freight rate growing area export data.
    Utilized in: export_excel.py
    """
    growing_area_id: int
    growing_area_name: str
    p_year: int
    period: int
    period_with_P: str
    plant_id: int
    plant_name: str
    rate_actual: float
    rate_plan: float
    totaldollarcwt: float

class ExportExcelFreightRateGrowingAreaList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of freight rate growing area export records.
    Used for batch Excel export operations involving freight rate growing area data.
    Enables validation of freight rate growing area export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelFreightRateGrowingArea]

class ExportExcelPotatoRatesGrowingAreaPeriod(BaseModel): # pragma: no cover
    """
    Schema for potato rates growing area period export data, including actual/forecast values and region.
    Used for Excel export operations involving potato rates growing area period records.
    Supports validation and serialization of potato rates growing area period export data.
    Utilized in: export_excel.py
    """
    actual_total_dollor: float
    actual_volume: float
    fcst_rate: float
    fcst_total_dollor: float
    forecast_volume: float
    growing_area_id: int
    growing_area_name: str
    p_year: int
    period: int
    period_with_P: str
    price_actual: float
    region: int
    region_name: str
    week: int

class ExportExcelPotatoRatesGrowingAreaPeriodList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of potato rates growing area period export records.
    Used for batch Excel export operations involving potato rates growing area period data.
    Enables validation of potato rates growing area period export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelPotatoRatesGrowingAreaPeriod]

class ExportExcelPotatoRatesGrowingAreaWeek(BaseModel): # pragma: no cover
    """
    Schema for potato rates growing area week export data, including actual/forecast values and rate.
    Used for Excel export operations involving potato rates growing area week records.
    Supports validation and serialization of potato rates growing area week export data.
    Utilized in: export_excel.py
    """
    actual_rate: float
    actual_total_dollor: float
    actual_volume: float
    forecast_volume: float
    forecaste_total_dollor: float
    growing_area_id: int
    growing_area_name: str
    p_year: int
    period: int
    period_with_P: str
    period_with_week: str
    potato_rate_id: int
    rate: float
    region_id: int
    region_name: str
    week: int

class ExportExcelPotatoRatesGrowingAreaWeekList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of potato rates growing area week export records.
    Used for batch Excel export operations involving potato rates growing area week data.
    Enables validation of potato rates growing area week export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelPotatoRatesGrowingAreaWeek]

class ExportExcelPotatoRatesPlantViewPeriod(BaseModel): # pragma: no cover
    """
    Schema for potato rates plant view period export data, including actual/forecast spend and volume.
    Used for Excel export operations involving potato rates plant view period records.
    Supports validation and serialization of potato rates plant view period export data.
    Utilized in: export_excel.py
    """
    row_number: int= Field(..., alias=var_row_number)
    actual_dollar_bymcwt: float
    actual_total_dollar_spend: float
    actual_volume: float
    company_name: str
    country: str
    forecast_dollar_bymcwt: float
    forecast_total_dollar_spend: float
    forecast_volume: float
    p_year: int
    period: int
    period_with_P: str
    plant_id: int
    plant_name: str
    sum_rate: float
    total_sum_quantity: float
    week: str

class ExportExcelPotatoRatesPlantViewPeriodList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of potato rates plant view period export records.
    Used for batch Excel export operations involving potato rates plant view period data.
    Enables validation of potato rates plant view period export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelPotatoRatesPlantViewPeriod]

class ExportExcelPotatoRatesPlantViewWeek(BaseModel): # pragma: no cover
    """
    Schema for potato rates plant view week export data, including actual/forecast spend and volume by week.
    Used for Excel export operations involving potato rates plant view week records.
    Supports validation and serialization of potato rates plant view week export data.
    Utilized in: export_excel.py
    """
    Total_dollor_spend_week: float
    actual_dollor_MCWT_week: float
    actual_volume: float
    company_name: str
    country: str
    forecast_dollor_cwt: float
    forecast_spend_week: float
    forecast_volume: float
    p_year: int
    period: int
    period_with_P: str
    period_with_week: str
    plant_id: int
    plant_name: str
    week_no: int

class ExportExcelPotatoRatesPlantViewWeekList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of potato rates plant view week export records.
    Used for batch Excel export operations involving potato rates plant view week data.
    Enables validation of potato rates plant view week export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelPotatoRatesPlantViewWeek]

class ExportExcelSolidsGrowingAreaView(BaseModel): # pragma: no cover
    """
    Schema for solids growing area view export data, including actual/plan rates and volumes.
    Used for Excel export operations involving solids growing area view records.
    Supports validation and serialization of solids growing area view export data.
    Utilized in: export_excel.py
    """
    actual_rate: float
    actual_total_solids: float
    actual_volume: float
    forecast_volume: float
    growing_area_id: int
    growing_area_name: str
    period: int
    period_with_P: str
    plan_rate: float
    plan_total_solids: float
    region: int
    region_name: str
    year: int

class ExportExcelSolidsGrowingAreaViewList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of solids growing area view export records.
    Used for batch Excel export operations involving solids growing area view data.
    Enables validation of solids growing area view export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelSolidsGrowingAreaView]

class ExportExcelSolidsPlantView(BaseModel): # pragma: no cover
    """
    Schema for solids plant view export data, including actual/forecast solids and volumes.
    Used for Excel export operations involving solids plant view records.
    Supports validation and serialization of solids plant view export data.
    Utilized in: export_excel.py
    """
    row_number: int= Field(..., alias=var_row_number)
    actual_solids: float
    actual_total_solids: float
    actual_volume: float
    company_name: str
    country: str
    forecast_solids: float
    forecast_total_solids: float
    forecast_volume: float
    p_year: int
    period: int
    period_with_P: str
    plant_id: int
    plant_name: str
    sum_rate: float
    week: str

class ExportExcelSolidsPlantViewList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of solids plant view export records.
    Used for batch Excel export operations involving solids plant view data.
    Enables validation of solids plant view export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelSolidsPlantView]

class ExportExcelHomePopUp(BaseModel): # pragma: no cover
    """
    Schema for home popup export data, including period, category, crop type, and volume.
    Used for Excel export operations involving home popup records.
    Supports validation and serialization of home popup export data.
    Utilized in: export_excel.py
    """
    PxW: str
    category_name: str
    crop_type: int
    period: int
    period_with_P: str
    plan_volume_id: str
    volume: int
    week: int

class ExportExcelHomePopUpList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of home popup export records.
    Used for batch Excel export operations involving home popup data.
    Enables validation of home popup export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelHomePopUp]

class ExportExcelHomePopUpPlan(BaseModel): # pragma: no cover
    """
    Schema for home popup plan export data, including period, category, crop type, and volume.
    Used for Excel export operations involving home popup plan records.
    Supports validation and serialization of home popup plan export data.
    Utilized in: export_excel.py
    """
    PxW: str
    category_name: str
    crop_type: int
    pc_volume_plan_id: str
    period: int
    period_with_P: str
    volume: int
    week: int
    year: int

class ExportExcelHomePopUpPlanList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of home popup plan export records.
    Used for batch Excel export operations involving home popup plan data.
    Enables validation of home popup plan export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelHomePopUpPlan]

class ExportExcelActiveAllocationIndex(BaseModel): # pragma: no cover
    """
    Schema for active allocation index export data, including allocation ID, category, and target volume.
    Used for Excel export operations involving active allocation index records.
    Supports validation and serialization of active allocation index export data.
    Utilized in: export_excel.py
    """
    allocation_id: str
    category_name: str
    country: str
    period: int
    value: Optional[float] = None
    target_volume: Optional[float] = None
    year: int

class ExportExcelActiveAllocationIndexList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of active allocation index export records.
    Used for batch Excel export operations involving active allocation index data.
    Enables validation of active allocation index export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelActiveAllocationIndex]

class ExportExcelForecastWeek(BaseModel): # pragma: no cover
    """
    Schema for forecast week export data, including period, plant, and actual/forecast values.
    Used for Excel export operations involving forecast week records.
    Supports validation and serialization of forecast week export data.
    Utilized in: export_excel.py
    """
    Period_with_P: str
    company_name: str
    country: str
    forecasted_value: float
    pcusage_id: str
    period: int
    plant_id: int
    plant_name: str
    region_id: int
    total_actual_value: float
    week: int
    year: int

class ExportExcelForecastWeekList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of forecast week export records.
    Used for batch Excel export operations involving forecast week data.
    Enables validation of forecast week export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelForecastWeek]

class ExportExcelFreightRateFuelCostGrowingArea(BaseModel): # pragma: no cover
    """
    Schema for freight rate fuel cost growing area export data, including total fuel and miles.
    Used for Excel export operations involving fuel cost growing area records.
    Supports validation and serialization of fuel cost growing area export data.
    Utilized in: export_excel.py
    """
    company_name: str
    country: str
    growing_area_id: int
    growing_area_name: str
    period: int
    period_with_P: str
    plant_id: int
    plant_name: str
    total_fuel: float
    total_miles: int
    year: int

class ExportExcelFreightRateFuelCostGrowingAreaList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of fuel cost growing area export records.
    Used for batch Excel export operations involving fuel cost growing area data.
    Enables validation of fuel cost growing area export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelFreightRateFuelCostGrowingArea]

class ExportExcelFreightRateFuelCostPlantView(BaseModel): # pragma: no cover
    """
    Schema for freight rate fuel cost plant view export data, including total fuel and miles by plant.
    Used for Excel export operations involving fuel cost plant view records.
    Supports validation and serialization of fuel cost plant view export data.
    Utilized in: export_excel.py
    """
    company_name: str
    country: str
    period: int
    period_with_P: str
    plant_id: int
    plant_name: str
    total_fuel: float
    total_miles: int
    year: int

class ExportExcelFreightRateFuelCostPlantViewList(BaseModel): # pragma: no cover
    """
    Schema for payload containing a list of fuel cost plant view export records.
    Used for batch Excel export operations involving fuel cost plant view data.
    Enables validation of fuel cost plant view export list payloads.
    Utilized in: export_excel.py
    """
    data:List[ExportExcelFreightRateFuelCostPlantView]

class JournalEntrySchema(BaseModel):  # pragma: no cover
    """
    Schema for journal entry data, including comments, email, page name, and parent journal ID.
    Used for API requests and responses involving journal entry records.
    Supports CRUD operations and validation for journal entry data.
    Utilized in: journal.py
    """
    comments: str
    email : str
    page_name : Optional[str] = None
    img_url : Optional[str] = None
    parent_journal_id: Optional[int] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class JournalEntryOwnerSchema(BaseModel):  # pragma: no cover
    """
    Schema for journal entry owner data, including ownership ID, growing area, and comments.
    Used for API requests involving ownership-related journal entries.
    Supports validation of journal entry owner payloads.
    Utilized in: journal.py
    """
    comments: str
    email : str
    ownership_id : str
    parent_journal_id: Optional[int] = None
    growing_area_name : Optional[str] = None
    growing_area_desc : Optional[str] = None
    img_url : Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class BTLInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for BTL (Below The Line) task information, including name, description, status, and audit fields.
    Used for API requests and responses involving BTL task records.
    Supports CRUD operations and validation for BTL task data.
    Utilized in: btl.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True    
class BTLTaskMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping BTL tasks to periods, years, and companies.
    Used for associating BTL tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of BTL task mapping data.
    Utilized in: btl.py
    """
    period: Optional[int] = None
    btl_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class BTLTaskMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of BTL task mappings.
    Used for batch operations and bulk updates of BTL task mapping data.
    Enables validation of BTL task mapping list payloads.
    Utilized in: btl.py
    """
    data: List[BTLTaskMappingSchema]
    
class BTLPlanInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for BTL plan task information, including name, description, status, and audit fields.
    Used for API requests and responses involving BTL plan task records.
    Supports CRUD operations and validation for BTL plan task data.
    Utilized in: btlplan.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class BTLPlanTaskMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping BTL plan tasks to periods, years, and companies.
    Used for associating BTL plan tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of BTL plan task mapping data.
    Utilized in: btlplan.py
    """
    period: Optional[int] = None
    btl_plan_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class BTLPlanTaskMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of BTL plan task mappings.
    Used for batch operations and bulk updates of BTL plan task mapping data.
    Enables validation of BTL plan task mapping list payloads.
    Utilized in: btlplan.py
    """
    data: List[BTLPlanTaskMappingSchema]
    
class ProductivityInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for productivity task information, including name, description, status, and audit fields.
    Used for API requests and responses involving productivity task records.
    Supports CRUD operations and validation for productivity task data.
    Utilized in: productivity.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True    
class ProductivityTaskMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping productivity tasks to periods, years, and companies.
    Used for associating productivity tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of productivity task mapping data.
    Utilized in: productivity.py
    """
    period: Optional[int] = None
    productivity_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ProductivityTaskMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of productivity task mappings.
    Used for batch operations and bulk updates of productivity task mapping data.
    Enables validation of productivity task mapping list payloads.
    Utilized in: productivity.py
    """
    data: List[ProductivityTaskMappingSchema]
    
class ProductivityPlanInfoSchema(BaseModel):# pragma: no cover
    """
    Schema for productivity plan task information, including name, description, status, and audit fields.
    Used for API requests and responses involving productivity plan task records.
    Supports CRUD operations and validation for productivity plan task data.
    Utilized in: productivityplan.py
    """
    task_name: Optional[str] = None
    task_desc: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ProductivityPlanTaskMappingSchema(BaseModel):# pragma: no cover
    """
    Schema for mapping productivity plan tasks to periods, years, and companies.
    Used for associating productivity plan tasks with specific timeframes and companies in APIs.
    Supports validation and serialization of productivity plan task mapping data.
    Utilized in: productivityplan.py
    """
    period: Optional[int] = None
    productivity_plan_task_id: Optional[int] = None
    year: Optional[int] = None
    value: Optional[float] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ProductivityPlanTaskMappingPayload(BaseModel):# pragma: no cover
    """
    Schema for payload containing a list of productivity plan task mappings.
    Used for batch operations and bulk updates of productivity plan task mapping data.
    Enables validation of productivity plan task mapping list payloads.
    Utilized in: productivityplan.py
    """
    data: List[ProductivityPlanTaskMappingSchema]
    
class PlantStatusPayload(BaseModel):  # pragma: no cover
    """
    Schema for plant status payload, including plant ID, name, status, year, and actual value.
    Used for API requests involving plant status updates.
    Supports validation of plant status update payloads.
    Utilized in: plant_mtrx.py
    """
    plant_id: int
    plant_name : str
    status : str
    year : int
    actual : int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class PowerBIReport(BaseModel):  # pragma: no cover
    """
    Schema for Power BI report data, including ID, name, and URL.
    Used for API requests and responses involving Power BI report configurations.
    Supports validation of Power BI report data.
    Utilized in: powerbi_config.py
    """
    id: str
    name: str
    url: str

class PowerBIConfigIn(BaseModel):   # pragma: no cover
    """
    Schema for Power BI configuration input, containing a list of Power BI reports.
    Used for API requests involving Power BI report configuration updates.
    Supports validation of Power BI configuration payloads.
    Utilized in: powerbi_config.py
    """
    powerBIReports: List[PowerBIReport]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class PowerBiRefreshLog(BaseModel):  # pragma: no cover
    """
    Schema for Power BI refresh log data, including report name, status, and trigger details.
    Used for API requests and responses involving Power BI refresh logging.
    Supports CRUD operations and validation for Power BI refresh log data.
    Utilized in: powerbi_config.py
    """
    report_name: str
    status : str
    trigger_datetime : Optional[datetime] = None
    completion_datetime : Optional[datetime] = None
    user_name : Optional[str] = None
    user_email : Optional[str] = None
    trigger_type : Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class OwnershipGrowerVarietySchema(BaseModel):
    """
    Schema for variety-level ownership mapping.
    Used for both request payload and response.
    Utilized in: ownership.py
    """
    row_id: str
    growing_area_id: int
    grower_id: int
    variety_id: str
    contract: Optional[int]
    year: Optional[int]
    shrinkage: Optional[float]
    shrinkage_volume: Optional[float]
    market: Optional[float]
    flex: Optional[float]
    contract_erp: Optional[float]
    ownership_id: str
    crop_type: Optional[str]
    crop_year: str
    status: Optional[str]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class UpdateOwnershipGrowerVariety(BaseModel):
    """
    Payload schema for updating variety-level ownership.
    Contains a list of variety-level records.
    Utilized in: ownership.py
    """
    PayloadVariety: List[OwnershipGrowerVarietySchema]

class VarietySchema(BaseModel): # pragma: no cover
    """
    Schema for variety data, including name, mapping, description, and status.
    Used for API requests and responses involving variety records.
    Supports CRUD operations and validation for variety data.
    Utilized in: variety.py
    """
    variety_name: str
    variety_mapping: str
    description: Optional[str] = "Variety details"
    status: Optional[str] = "ACTIVE"
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_time: Optional[datetime] = None

    class Config:
        orm_mode = True

class VarietyUpdateSchema(BaseModel):  # pragma: no cover
    """
    Schema for updating variety records, including name, mapping, and description.
    Used for API requests involving variety record updates.
    Supports validation of variety update payloads.
    Utilized in: variety.py
    """
    variety_name: Optional[str] = None
    variety_mapping: Optional[str] = None
    description: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        orm_mode = True