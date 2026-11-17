from sqlalchemy import FLOAT
from sqlalchemy import TIMESTAMP, Column, String, ForeignKey, Integer, BigInteger, Float, MetaData,\
    Boolean, PrimaryKeyConstraint, DateTime, text, Index,Numeric
from sqlalchemy.sql import func
from datetime import datetime
from database import engine
import sqlalchemy as db
from database import Base


"""
models.py

This file defines all SQLAlchemy ORM table models for the potato sourcing matrix automation project.

Usage:
- Import this file to access database table classes for CRUD operations, queries, and schema definitions.
- Each class represents a table in the database, with columns mapped to attributes.
- Use these models with SQLAlchemy sessions for ORM-based data access.
- Table relationships are defined via foreign keys and mapped attributes, enabling complex queries and joins.
"""

metadata = MetaData()

class Plant(Base):
    """
    Represents plant information including plant code, name, company, region, and crop category.
    Each plant can be linked to growing areas via plant_growing_area_mapping and PlantSiteGrowingAreaMapping.
    Used for associating production and allocation data with specific plants.
    Interacts with FreightCostRate, plantMtrx, and other tables through plant_id.
    """
    __tablename__ = 'plant'

    plant_id = Column(Integer(), primary_key=True, autoincrement=True)
    plant_code = Column(String, nullable=False)
    plant_name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    region_id = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    crop_category_id = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())
    pgt_plant_name = Column(String, nullable=False)

class growing_area(Base):
    """
    Stores growing area details, including region, country, and period/week boundaries for fresh and storage.
    Linked to plants via plant_growing_area_mapping and PlantSiteGrowingAreaMapping.
    Used in ownership, allocation, and rate tables for crop tracking and reporting.
    Interacts with growers, plant, and rate tables through growing_area_id.
    """
    __tablename__ = 'growing_area'

    growing_area_id = Column(Integer(), primary_key=True, autoincrement=True)
    growing_area_name = Column(String, nullable=False)
    region = Column(Integer(), nullable=True)
    country = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    growing_area_desc = Column(String, nullable=True)
    fresh_period_start = Column(Integer(), nullable=True)
    fresh_week_start = Column(Integer(), nullable=True)
    fresh_period_end = Column(Integer(), nullable=True)
    fresh_week_end = Column(Integer(), nullable=True)
    storage_period_start = Column(Integer(), nullable=True)
    storage_week_start = Column(Integer(), nullable=True)
    storage_period_end = Column(Integer(), nullable=True)
    storage_week_end = Column(Integer(), nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())
    pgt_growing_area = Column(String, nullable=False)

class growers(Base):
    """
    Contains grower information such as name, owner, region, country, and volume.
    Growers are mapped to growing areas and ownership via preferred_grower and OwnershipGrowerGrowing.
    Used for tracking production and contracts at the grower level.
    Interacts with growing_area, ownership, and variety tables through grower_id.
    """
    __tablename__ = 'growers'

    grower_id = Column(Integer(), primary_key=True, autoincrement=True)
    grower_name = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    region = Column(Integer(), nullable=True)
    country = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    volume = Column(String, nullable=True)

    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())
    grower_abbreviation_code = Column(String, nullable=True)
    pgt_grower_name = Column(String, nullable=False)

class preferred_grower(Base):
    """
    Maps growers to growing areas, establishing relationships for allocation and reporting.
    Links grower_id and growing_area_id to growers and growing_area tables.
    Used for filtering and aggregating data by grower and area.
    Enables join operations between grower and area entities.
    """
    __tablename__ = 'grower_growing_area_mapping'

    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    grower_name = Column(String, nullable=True)
    grower_id = Column(Integer, nullable=True)
    growing_area_id = Column(Integer, nullable=True)
    growing_area_name = Column(String, nullable=True)


class region(Base):
    """
    Stores region information, including region name and country.
    Regions are referenced by plants and growing areas for geographic grouping.
    Used for regional analysis and reporting across multiple tables.
    Interacts with plant and growing_area tables via region_id.
    """
    __tablename__ = 'region'

    region_id = Column(Integer(), primary_key=True, autoincrement=True)
    region_name = Column(String, nullable=False)
    country = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())


class plant_growing_area_mapping(Base):
    """
    Maps plants to growing areas using plant_id and growing_area_id.
    Enables many-to-many relationships between plants and areas for allocation and production.
    Used in queries to link plant and area data for reporting.
    Interacts with plant and growing_area tables via mapping IDs.
    """
    __tablename__ = 'plant_growing_area_mapping'
    plant_mapping_id = Column(Integer(), primary_key=True, autoincrement=True)
    plant_id = Column(Integer(), nullable=True)
    growing_area_id = Column(Integer(), nullable=True)


class category(Base):
    """
    Represents crop categories, including category name and country.
    Used for grouping and filtering allocation and production data.
    Interacts with allocation and plant tables via crop_category.
    Enables category-based analysis and reporting.
    """
    __tablename__ = 'crop_category'

    crop_category = Column(Integer(), primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False)
    country = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())


class allocation(Base):
    """
    Stores allocation data for crop categories, periods, and values.
    Links to category and plant tables for allocation tracking.
    Used in planning and forecasting workflows.
    Interacts with category, plant, and growing_area tables via allocation_id and category_name.
    """
    __tablename__ = 'active_allocation'

    allocation_id = Column(String, primary_key=True)
    category_name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    country = Column(String, nullable=True)
    period = Column(Integer, nullable=False)
    value = Column(Float, nullable=True)
    backend_value = Column(Float, nullable=True)
    target_volume = Column(Float, nullable=True)

class pcusage(Base):
    """
    Tracks PC usage per plant, year, period, and week.
    Used for monitoring production and forecasting at the plant level.
    Links to plant table via plant_id for detailed analysis.
    Enables week-by-week usage reporting and aggregation.
    """
    __tablename__ = 'pc_usage'

    pcusage_id = Column(String, primary_key=True)
    year = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    week_no = Column(Integer, nullable=False)
    plant_id = Column(String, nullable=True)
    forecasted_value = Column(Float, nullable=True)
    country = Column(String, nullable=True)


class OwnershipGrowerGrowing(Base):
    """
    Maps ownership, grower, and growing area with contract and crop details.
    Links grower_id and growing_area_id to growers and growing_area tables.
    Used for contract management and ownership tracking.
    Interacts with ownership, grower, and area tables for reporting and analysis.
    """
    __tablename__ = 'ownership_grower_growing_area_mapping'

    row_id = Column(String, primary_key=True)
    growing_area_id = Column(Integer(), nullable=False)
    grower_id = Column(Integer(), nullable=False)
    contract = Column(Integer(), nullable=True)
    year = Column(Integer(), nullable=True)
    shrinkage = Column(FLOAT, nullable=True)
    shrinkage_volume = Column(Numeric(18, 3), nullable=True)
    market = Column(Float, nullable=True)
    flex = Column(Float, nullable=True)
    contract_erp = Column(FLOAT, nullable=True)
    ownership_id = Column(String, nullable=True)
    crop_type = Column(String, nullable=True)
    crop_year = Column(String, nullable=False)
    status = Column(String, nullable=True)


class PlantSiteGrowingAreaMapping(Base):
    """
    Maps vendor site codes to growing areas and plants.
    Links plant_id and growing_area_id to plant and growing_area tables.
    Used in freight cost and allocation calculations.
    Enables site-level analysis and reporting across plants and areas.
    """
    __tablename__ = 'plant_site_growing_area_mapping'
    row_id = Column(Integer(), primary_key=True, autoincrement=True)
    Vendor_Site_Code = Column(String, nullable=False)
    growing_area = Column(String, nullable=False)
    plant_name = Column(String, nullable=False)
    vendor_site_id = Column(Integer(), nullable=False)
    plant_id = Column(Integer(), nullable=False)
    growing_area_id = Column(Integer(), nullable=False)


class FreightCostRate(Base):
    """
    Stores freight cost rates for plant, growing area, and vendor site.
    Links plant_id, growing_area_id, and vendor_site_id to PlantSiteGrowingAreaMapping.
    Used for calculating logistics and transportation costs.
    Interacts with FreightCostMapping and plant tables for cost analysis.
    """
    __tablename__ = "freight_cost_rate"
    __table_args__ = (
        Index('idx_fk_composite', 'plant_id', 'growing_area_id', 'vendor_site_id'),  # Composite index for JOIN
    )

    freight_cost_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    currency = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    plant_id = Column(Integer(), ForeignKey("plant_site_growing_area_mapping.plant_id"), index=True)
    growing_area_id = Column(Integer(), ForeignKey("plant_site_growing_area_mapping.growing_area_id"), index=True)
    vendor_site_id = Column(Integer(), ForeignKey("plant_site_growing_area_mapping.vendor_site_id"), index=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())
    miles = Column(Float, nullable=True)

class FreightCostMapping(Base):
    """
    Maps freight cost rates to periods, years, and companies.
    Links freight_cost_id to FreightCostRate for detailed cost tracking.
    Used for historical and planned freight cost analysis.
    Enables company-level cost aggregation and reporting.
    """
    __tablename__ = "freight_cost_mapping"
    __table_args__ = (
        Index('idx_year_company', 'year', 'company_name'),  # Composite index for WHERE clause
    )
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    freight_cost_id = Column(Integer, nullable=False, index=True)
    year = Column(Integer, index=True, nullable=False)
    period = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)
    company_name = Column(String, nullable=True, index=True)
    round_trip = Column(Integer, nullable=True)
    fuel_cf = Column(Float, nullable=True)


class Ownership(Base):
    """
    Stores ownership details for growing areas, contracts, and crop types.
    Links growing_area_id to growing_area for area-specific ownership.
    Used for contract, shipment, and market tracking.
    Interacts with grower, area, and extension tables for ownership analysis.
    """
    __tablename__ = 'ownership'

    ownership_id = Column(String, primary_key=True)
    growing_area_id = Column(Integer(), nullable=False)
    contract = Column(Float, nullable=False)
    shrinkage = Column(Float, nullable=True)
    to_ship = Column(Float, nullable=True)
    market = Column(Float, nullable=True)
    flex = Column(Float, nullable=True)
    total_ship = Column(Float, nullable=True)
    extension = Column(Integer(), nullable=True)
    contract_erp_value = Column(Float, nullable=True)
    crop_type = Column(String, nullable=True)
    crop_year = Column(String, nullable=True)
    year = Column(Integer(), nullable=True)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())
    final_extension = Column(Float, nullable=True)


class vendor_site_code(Base):
    """
    Stores vendor site codes and related information for plants and regions.
    Links region_id to region for geographic grouping.
    Used in plant-site mapping and freight calculations.
    Enables vendor-level analysis and reporting.
    """
    __tablename__ = "vendor_site_code"

    VENDOR_SITE_ID = Column(Integer(), primary_key=True, autoincrement=True)
    VENDOR_SITE_CODE = Column(Integer, nullable=False)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    status = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    region_id = Column(Integer, nullable=False)
    pgt_vsc = Column(Integer, nullable=False)


class solids_rates(Base):
    """
    Stores solids rates for growing areas and currencies.
    Links growing_area_id to growing_area for area-specific rates.
    Used in cost and pricing calculations for solids.
    Enables area-level solids rate analysis and reporting.
    """
    __tablename__ = "solids_rates"
    solids_rate_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    growing_area_id = Column(Integer, nullable=True)
    growing_area_id_old = Column(Integer, nullable=True)
    currency = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class potato_rates(Base):
    """
    Stores potato rates for growing areas and years.
    Links growing_area_id to growing_area for area-specific rates.
    Used in cost and pricing calculations for potatoes.
    Enables area-level potato rate analysis and reporting.
    """
    __tablename__ = "potato_rates" 
    potato_rate_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=True)
    growing_area_id = Column(Integer, nullable=True)
    growing_area_id_old = Column(Integer, nullable=True)
    currency = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class plantMtrx(Base):
    """
    Stores plant matrix growing area values for periods, weeks, and crop types.
    Links plant_id and growing_area_id to plant and growing_area tables.
    Used for production planning and allocation analysis.
    Enables matrix-based reporting across plants and areas.
    """
    __tablename__ = "plant_matrix_growing_area" 

    plant_matrix_id = Column(String, primary_key=True, nullable=False)
    plant_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    period = Column(Integer, nullable=True)
    week = Column(Integer, nullable=True) 
    region_id = Column(Integer, nullable=True) 
    growing_area_id = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    crop_type = Column(String, nullable=True) 
    crop_year = Column(String, nullable=True)
    status = Column(String, nullable=True)
    type = Column(String, nullable=True)

class PlantMtrxNullLog(Base):
    """
    Logs null values in plant matrix data for debugging and audit purposes.
    Links plant_id and growing_area_id to plant and area tables.
    Used for identifying data gaps and quality issues.
    Enables traceability and error analysis in matrix data.
    """
    __tablename__ = "plant_mtrx_null_log"

    log_id            = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    plant_id          = Column(Integer, nullable=True)
    plant_name        = Column(String(50), nullable=True)
    region_id         = Column(Integer, nullable=True)
    growing_area_id   = Column(Integer, nullable=True)
    growing_area_name = Column(String(50), nullable=True)
    period            = Column(Integer, nullable=True)
    week              = Column(Integer, nullable=True)
    year              = Column(Integer, nullable=True)
    crop_type         = Column(String(500), nullable=True)
    crop_year         = Column(String(61), nullable=True)
    sumof_rec_potato  = Column(Float, nullable=True)
    bpa_number        = Column(String(500), nullable=True)   # ERP: varchar(500)
    release_no        = Column(Float, nullable=True)         # ERP: float(53)
    shipment          = Column(Float, nullable=True)         # ERP: float(53)
    line_no           = Column(Float, nullable=True)         # ERP: float(53)
    erp_unique_id     = Column(String(2048), nullable=True, index=True)
    active            = Column(Boolean, nullable=False, server_default=text("1"))
    created_time      = Column(DateTime, nullable=False)


class plantMtrx_template(Base):
    """
    Stores plant matrix template for plant, period, week, and growing area.
    Links plant_id and growing_area_id to plant and area tables.
    Used for template-driven planning and allocation.
    Enables structured matrix setup for production analysis.
    """
    __tablename__ = "plant_mtrx_template"

    plant_id = Column(String, nullable=True, primary_key=True)
    period = Column(Integer, nullable=True)
    week_no = Column(Integer, nullable=True)
    growing_area_id = Column(String, nullable=True)


class potato_rate_mapping(Base):
    """
    Maps potato rates to periods, weeks, and country codes.
    Links potato_rate_id to potato_rates for detailed rate tracking.
    Used for period and week-based rate analysis.
    Enables mapping between rates and time/country dimensions.
    """
    __tablename__ = "potato_rate_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    potato_rate_id = Column(Integer, nullable=True)
    week = Column(Integer, nullable=True)
    rate = Column(Float, nullable=True)
    p_year = Column(Integer, nullable=True)
    country_code = Column(String, nullable=True)

class solid_rate_mapping(Base):
    """
    Maps solid rates to periods and country codes.
    Links solids_rate_id to solids_rates for detailed rate tracking.
    Used for period and country-based solids rate analysis.
    Enables mapping between solids rates and time/country dimensions.
    """
    __tablename__ = "solid_rate_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    solids_rate_id = Column(Integer, nullable=True)
    rate = Column(Float, nullable=True)
    period_year = Column(Integer, nullable=True)
    country_code = Column(String, nullable=True)


class off_contract_info(Base):
    """
    Stores off-contract task information including name, description, and status.
    Used for managing off-contract tasks and tracking their lifecycle.
    Interacts with off_contract_task_mapping for period and company assignments.
    Enables task-level reporting and analysis.
    """
    __tablename__ = "off_contract_info"
    off_contract_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    order_position = Column(Integer, nullable=True)


class off_contract_task_mapping(Base):
    """
    Maps off-contract tasks to periods, years, and companies.
    Links off_contract_task_id to off_contract_info for task details.
    Used for scheduling and tracking off-contract tasks.
    Enables mapping between tasks and time/company dimensions.
    """
    __tablename__ = "off_contract_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    off_contract_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)
    
class off_contract_plan_info(Base):
    """
    Stores off-contract plan task information including name, description, and status.
    Used for managing planned off-contract tasks and tracking their lifecycle.
    Interacts with off_contract_plan_task_mapping for period and company assignments.
    Enables plan task-level reporting and analysis.
    """
    __tablename__ = "off_contract_plan_info"
    off_contract_plan_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class off_contract_plan_task_mapping(Base):
    """
    Maps off-contract plan tasks to periods, years, and companies.
    Links off_contract_plan_task_id to off_contract_plan_info for plan task details.
    Used for scheduling and tracking planned off-contract tasks.
    Enables mapping between plan tasks and time/company dimensions.
    """
    __tablename__ = "off_contract_plan_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    off_contract_plan_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class freight_task_info(Base):
    """
    Stores freight task information including name, description, and status.
    Used for managing freight tasks and tracking their lifecycle.
    Interacts with freight_task_mappings for period and company assignments.
    Enables task-level reporting and analysis for freight operations.
    """
    __tablename__ = "freight_task_info"
    freight_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class freight_task_mappings(Base):
    """
    Maps freight tasks to periods, years, and companies.
    Links freight_task_id to freight_task_info for task details.
    Used for scheduling and tracking freight tasks.
    Enables mapping between tasks and time/company dimensions for logistics.
    """
    __tablename__ = "freight_task_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    freight_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)

class freight_task_plan_info(Base):
    """
    Stores freight task plan information including name, description, and status.
    Used for managing planned freight tasks and tracking their lifecycle.
    Interacts with freight_task_plan_mappings for period and company assignments.
    Enables plan task-level reporting and analysis for logistics.
    """
    __tablename__ = "freight_task_plan_info"
    freight_task_plan_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class freight_task_plan_mappings(Base):
    """
    Maps freight task plans to periods, years, and companies.
    Links freight_task_plan_id to freight_task_plan_info for plan task details.
    Used for scheduling and tracking planned freight tasks.
    Enables mapping between plan tasks and time/company dimensions for logistics.
    """
    __tablename__ = "freight_task_plan_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    freight_task_plan_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class general_administrative_task(Base):
    """
    Stores general administrative task information including name, description, and status.
    Used for managing administrative tasks and tracking their lifecycle.
    Interacts with general_administrative_mappings for period and company assignments.
    Enables task-level reporting and analysis for administration.
    """
    __tablename__ = "general_administrative_task"
    general_administrative_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class general_administrative_mappings(Base):
    """
    Maps general administrative tasks to periods, years, and companies.
    Links general_administrative_id to general_administrative_task for task details.
    Used for scheduling and tracking administrative tasks.
    Enables mapping between tasks and time/company dimensions for administration.
    """
    __tablename__ = "general_administrative_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    general_administrative_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)
    
class general_administrative_plan_task(Base):
    """
    Stores general administrative plan task information including name, description, and status.
    Used for managing planned administrative tasks and tracking their lifecycle.
    Interacts with general_administrative_plan_mappings for period and company assignments.
    Enables plan task-level reporting and analysis for administration.
    """
    __tablename__ = "general_administrative_plan_task"
    general_administrative_plan_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class general_administrative_plan_mappings(Base):
    """
    Maps general administrative plan tasks to periods, years, and companies.
    Links general_administrative_plan_id to general_administrative_plan_task for plan task details.
    Used for scheduling and tracking planned administrative tasks.
    Enables mapping between plan tasks and time/company dimensions for administration.
    """
    __tablename__ = "general_administrative_plan_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    general_administrative_plan_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class p4p_master_info(Base):
    """
    Stores P4P master information including name, description, and status.
    Used for managing P4P tasks and tracking their lifecycle.
    Interacts with p4p_task_mappings for period and company assignments.
    Enables task-level reporting and analysis for P4P operations.
    """
    __tablename__ = "p4p_master_info"
    p4p_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    p4p_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class p4p_task_mappings(Base):
    """
    Maps P4P tasks to periods, years, and companies.
    Links p4p_id to p4p_master_info for task details.
    Used for scheduling and tracking P4P tasks.
    Enables mapping between tasks and time/company dimensions for P4P operations.
    """
    __tablename__ = "p4p_task_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    p4p_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class ExtensionOwnershipMapping(Base):
    """
    Maps extension ownership to growing areas, periods, and crop types.
    Links growing_area_id to growing_area for area-specific ownership.
    Used for tracking ownership extensions and splits.
    Enables mapping between ownership and area/time dimensions.
    """
    __tablename__ = 'extension_ownership_mapping'

    extension_id = Column(String, nullable=False, primary_key=True)
    growing_area_id = Column(Integer(), nullable=True)
    period = Column(Integer(), nullable=True)
    week = Column(Integer(), nullable=True)
    total_value = Column(Float, nullable=True)
    crop_type = Column(String, nullable=True)
    crop_year = Column(String, nullable=True)
    year = Column(String, nullable=True)
    split = Column(String, nullable=True)
    status = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(),onupdate = func.now())


class price_variance_task(Base):
    """
    Stores price variance task information including name, description, and status.
    Used for managing price variance tasks and tracking their lifecycle.
    Interacts with price_variance_task_mapping for period and company assignments.
    Enables task-level reporting and analysis for price variance.
    """
    __tablename__ = "price_variance_task"
    price_variance_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class price_variance_task_mapping(Base):
    """
    Maps price variance tasks to periods, years, and companies.
    Links price_variance_task_id to price_variance_task for task details.
    Used for scheduling and tracking price variance tasks.
    Enables mapping between tasks and time/company dimensions for price variance.
    """
    __tablename__ = "price_variance_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    price_variance_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)


class inflation_deflation_task(Base):
    """
    Stores inflation/deflation task information including name, description, and status.
    Used for managing inflation/deflation tasks and tracking their lifecycle.
    Interacts with inflation_deflation_task_mappings for period and company assignments.
    Enables task-level reporting and analysis for inflation/deflation.
    """
    __tablename__ = "inflation_deflation_task"
    inflation_deflation_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class inflation_deflation_task_mappings(Base):
    """
    Maps inflation/deflation tasks to periods, years, and companies.
    Links inflation_deflation_task_id to inflation_deflation_task for task details.
    Used for scheduling and tracking inflation/deflation tasks.
    Enables mapping between tasks and time/company dimensions for inflation/deflation.
    """
    __tablename__ = "inflation_deflation_task_mappings"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    inflation_deflation_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)

class MarketFlexMapping(Base): 
    """
    Maps market flex values to ownership, grower, and growing area.
    Links grower_id and growing_area_id to growers and growing_area tables.
    Used for tracking market flexibility and ownership relationships.
    Enables mapping between ownership, grower, and area dimensions.
    """
    __tablename__ = 'ownership_grower_growing_area_market_area_mapping'
    row_id = Column(String, nullable=False, primary_key=True)
    growing_area_id = Column(Integer(), nullable=True)
    grower_id = Column(Integer(), nullable=True)
    ownership_id = Column(String, nullable=True)
    status = Column(String, nullable=True)
    market_flex_value = Column(Integer(), nullable=True)


class solid_task_master(Base):
    """
    Stores solid task master information including name, description, and status.
    Used for managing solid tasks and tracking their lifecycle.
    Interacts with solids_task_mapping for period and country assignments.
    Enables task-level reporting and analysis for solids.
    """
    __tablename__ = "solid_task_master"
    solids_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    order_position = Column(Integer, nullable=True)


class solids_task_mapping(Base): 
    """
    Maps solids tasks to periods, years, and country codes.
    Links solids_task_id to solid_task_master for task details.
    Used for scheduling and tracking solids tasks.
    Enables mapping between tasks and time/country dimensions for solids.
    """
    __tablename__ = "solids_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    solids_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    country_code = Column(String, nullable=True)


class country_division_name(Base): 
    """
    Stores country division names and related information for task grouping.
    Used for organizing tasks and reporting by division.
    Interacts with other tables via division_name_id for division-based analysis.
    Enables division-level grouping and reporting.
    """
    __tablename__ = "country_division_name"
    division_name_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    division_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class pc_plan_volume_usage(Base): 
    """
    Stores plan volume usage for crops, periods, weeks, and years.
    Used for planning and forecasting production volumes.
    Links crop_type and period to crop and time tables for analysis.
    Enables volume tracking and reporting across planning dimensions.
    """
    """Class representing plan_volume_usage table"""
    __tablename__ = "plan_volume_usage"
    plan_volume_id = Column(String, nullable=False, primary_key=True)
    crop_type = Column(Integer, nullable=True)
    period = Column(Integer, nullable=True)
    week = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    volume = Column(Integer, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())

class pc_volume_usage_plan(Base):
    """
    Stores PC volume usage plan for crops, periods, weeks, and years.
    Used for planning and forecasting PC volumes.
    Links crop_type and period to crop and time tables for analysis.
    Enables volume tracking and reporting across planning dimensions.
    """
    __tablename__ = "pc_volume_usage_plan"
    pc_volume_plan_id = Column(String, nullable=False, primary_key=True)
    crop_type = Column(Integer, nullable=True)
    period = Column(Integer, nullable=True)
    week = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    volume = Column(Integer, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())

class erp_logs_table(Base): 
    """
    Logs ERP file upload and processing events, including counts and timestamps.
    Used for tracking data pipeline status and audit trails.
    Interacts with other tables via id for log-based analysis.
    Enables traceability and error reporting for ERP operations.
    """
    __tablename__ = "erp_logs"
    id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    records_deleted = Column(Integer, nullable=True)
    records_inserted = Column(Integer, nullable=True)
    date_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    pipeline_status = Column(String, nullable=True)

class user_information(Base):
    """
    Stores user information, including email, country, admin status, and access details.
    Used for authentication, authorization, and user management.
    Links user_id to user_page_mapping for access control.
    Enables user-level reporting and analysis across the platform.
    """
    __tablename__ = "user_information"
    user_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    email = Column(String, nullable=True)
    country = Column(String, nullable=True)
    user_status = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=True)
    created_by = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now())

class page_information(Base): 
    """
    Stores page information, including name, status, description, and access details.
    Used for managing pages and access control.
    Links page_id to user_page_mapping for user access assignments.
    Enables page-level reporting and analysis across the platform.
    """
    __tablename__ = "page_information"
    page_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    page_name = Column(String, nullable=True)
    page_status = Column(Boolean, default=True)
    page_description = Column(String, nullable=True)
    created_by = Column(String, nullable=True,default='SYSTEM')
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True,default='SYSTEM')
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    is_read_only = Column(Boolean, default=False)

class user_page_mapping(Base): 
    """
    Maps users to pages and access types, including country and access IDs.
    Links user_id and page_id to user_information and page_information tables.
    Used for access control and permission management.
    Enables mapping between users, pages, and access levels.
    """
    __tablename__ = "user_page_mapping"
    user_id = Column(Integer(), nullable=False, primary_key=True)
    page_id = Column(Integer(), nullable=False, primary_key=True)
    access_id = Column(Integer(), nullable=False, primary_key=True)
    country_id = Column(Integer(), nullable=False, primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'page_id','access_id','country_id'),
    )

class access_type_information(Base): 
    """
    Stores access type information, including access name and value.
    Used for defining and managing access levels across the platform.
    Links access_id to user_page_mapping for permission assignments.
    Enables access-level reporting and analysis.
    """
    __tablename__ = "access_type_information"
    access_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    access_name = Column(String, nullable=True)
    access_value = Column(Integer, nullable=True)

class country_information(Base): 
    """
    Stores country information, including country name and ID.
    Used for grouping and filtering data by country.
    Links country_id to user_page_mapping for access assignments.
    Enables country-level reporting and analysis.
    """
    __tablename__ = "country_information"
    country_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    country_name = Column(String, nullable=True)


class user_log(Base): 
    """
    Logs user actions and events, including email, timestamps, and page details.
    Used for auditing and tracking user activity.
    Links user_id to user_information for user-level analysis.
    Enables traceability and reporting of user actions.
    """
    __tablename__ = "user_log"

    id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=False,
                       default=datetime.now().strftime("%Y-%m-%d %H:%M"))
    date = Column(DateTime, nullable=False)

class FileUploadTemplate(Base): 
    """
    Stores file upload templates and processing status, including user and timestamps.
    Used for managing file uploads and tracking their lifecycle.
    Links file_process_id to other tables for file-based analysis.
    Enables reporting and auditing of file upload events.
    """
    """Class representing freight_cost_rate table"""
    __tablename__ = "file_template_upload"

    file_process_id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    file_process_status = Column(Boolean, default=False)
    file_uploaded_user = Column(String, nullable=True)
    message = Column(String, nullable=True)
    file_uploaded_time = Column(TIMESTAMP(timezone=False),
                          nullable=False, server_default=func.now())
    file_process_time = Column(TIMESTAMP(timezone=False),
                          default=None, onupdate=func.now())

class export_excel_payload(Base):
    """
    Stores export Excel payloads, including payload content and IDs.
    Used for managing and tracking Excel export operations.
    Links Payload_ID to other tables for export-based analysis.
    Enables reporting and auditing of export events.
    """
    __tablename__ = "export_excel_payload"
    Payload_ID = Column(Integer, primary_key=True, autoincrement=False)
    Payload = Column(String, nullable=True)

class journal_all(Base): 
    """
    Logs journal entries for all pages, including comments, user, and timestamps.
    Used for tracking and auditing journal activity across the platform.
    Links journal_id to other tables for journal-based analysis.
    Enables reporting and traceability of journal entries.
    """
    __tablename__ = "journal_all"
    
    journal_id = Column(Integer(), primary_key=True, autoincrement=True)
    comments = Column(String, nullable=False)
    page_name = Column(String, nullable=True)
    page_id = Column(Integer(),nullable = True)
    user_first_name = Column(String, nullable=False)
    user_last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    user_id = Column(Integer(), nullable=False)
    created_time = Column(DateTime, nullable=False)
    img_url = Column(String, nullable=True)
    parent_journal_id = Column(Integer(), nullable=True)

class journal_ownership(Base): 
    """
    Logs journal entries for ownership pages, including comments, user, and ownership details.
    Used for tracking and auditing ownership-related journal activity.
    Links journal_id and ownership_id to ownership and user tables.
    Enables reporting and traceability of ownership journal entries.
    """
    __tablename__ = "journal_ownership"
    
    journal_id = Column(Integer(), primary_key=True, autoincrement=True)
    comments = Column(String, nullable=False)
    user_first_name = Column(String, nullable=False)
    user_last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    user_id = Column(Integer(), nullable=False)
    created_time = Column(DateTime, nullable=False)
    ownership_id = Column(String, nullable = False)
    growing_area_name = Column(String, nullable = False)
    growing_area_desc = Column(String, nullable = False)
    img_url = Column(String, nullable=True)
    region = Column(String, nullable=True)
    year = Column(Integer(), nullable=True)
    crop_type = Column(String, nullable = True)
    crop_year = Column(String, nullable = True)
    filter_year_1 = Column(Integer(), nullable = True)
    filter_year_2 = Column(Integer(), nullable = True)
    parent_journal_id = Column(Integer(), nullable=True)
    
class btl_task_info(Base): 
    """
    Stores BTL task information including name, description, and status.
    Used for managing BTL tasks and tracking their lifecycle.
    Links btl_task_id to btl_task_mappings for period and company assignments.
    Enables task-level reporting and analysis for BTL operations.
    """
    __tablename__ = "btl_task_info"
    btl_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class btl_task_mappings(Base): 
    """
    Maps BTL tasks to periods, years, and companies.
    Links btl_task_id to btl_task_info for task details.
    Used for scheduling and tracking BTL tasks.
    Enables mapping between tasks and time/company dimensions for BTL operations.
    """
    __tablename__ = "btl_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    btl_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)

class btl_plan_task_info(Base):
    """
    Stores BTL plan task information including name, description, and status.
    Used for managing planned BTL tasks and tracking their lifecycle.
    Links btl_plan_task_id to btl_plan_task_mapping for period and company assignments.
    Enables plan task-level reporting and analysis for BTL operations.
    """
    __tablename__ = "btl_plan_task_info"
    btl_plan_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class btl_plan_task_mapping(Base): 
    """
    Maps BTL plan tasks to periods, years, and companies.
    Links btl_plan_task_id to btl_plan_task_info for plan task details.
    Used for scheduling and tracking planned BTL tasks.
    Enables mapping between plan tasks and time/company dimensions for BTL operations.
    """
    __tablename__ = "btl_plan_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    btl_plan_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)
    
class productivity_task_info(Base): 
    """
    Stores productivity task information including name, description, and status.
    Used for managing productivity tasks and tracking their lifecycle.
    Links productivity_task_id to productivity_task_mapping for period and company assignments.
    Enables task-level reporting and analysis for productivity operations.
    """
    __tablename__ = "productivity_task_info"
    productivity_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class productivity_task_mapping(Base): 
    """
    Maps productivity tasks to periods, years, and companies.
    Links productivity_task_id to productivity_task_info for task details.
    Used for scheduling and tracking productivity tasks.
    Enables mapping between tasks and time/company dimensions for productivity operations.
    """
    __tablename__ = "productivity_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    productivity_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)

class productivity_plan_task_info(Base): 
    """
    Stores productivity plan task information including name, description, and status.
    Used for managing planned productivity tasks and tracking their lifecycle.
    Links productivity_plan_task_id to productivity_plan_task_mapping for period and company assignments.
    Enables plan task-level reporting and analysis for productivity operations.
    """
    __tablename__ = "productivity_plan_task_info"
    productivity_plan_task_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=True)
    task_desc = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(TIMESTAMP(timezone=False), nullable=False, server_default=func.now())


class productivity_plan_task_mapping(Base): 
    """
    Maps productivity plan tasks to periods, years, and companies.
    Links productivity_plan_task_id to productivity_plan_task_info for plan task details.
    Used for scheduling and tracking planned productivity tasks.
    Enables mapping between plan tasks and time/company dimensions for productivity operations.
    """
    __tablename__ = "productivity_plan_task_mapping"
    row_id = Column(Integer(), nullable=False, primary_key=True, autoincrement=True)
    period = Column(Integer, nullable=True)
    productivity_plan_task_id = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    company_name = Column(String, nullable=True)

class admin_alert(Base): 
    """
    Stores admin alerts for plant, vendor, and growing area events, including category and quantity.
    Used for monitoring and reporting alerts across production and logistics.
    Links plant_id, vendor_site_code, and growing_area to plant and site tables.
    Enables alert-level reporting and analysis.
    """
    __tablename__ = "admin_alert"
    alert_id = Column(Integer(), primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    bpa_number = Column(Integer(),nullable = False)
    Quantity_Accepted_MCWT = Column(Integer(), nullable=True)
    plant_name = Column(String, nullable=True)
    vendor_site_code = Column(String, nullable=True)
    vendor_name = Column(String, nullable=True)
    growing_area = Column(String, nullable=True)
    ship_to_org = Column(String, nullable=True)
    count = Column(Integer(),nullable = True)
    year = Column(Integer, nullable=True)
    period = Column(Integer, nullable=True)

class plant_status(Base): 
    """
    Stores plant status and category information, including year and timestamps.
    Used for tracking plant activity and status changes.
    Links plant_id to plant table for status analysis.
    Enables plant-level reporting and monitoring.
    """
    __tablename__ = "plant_status"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    plant_id = Column(Integer(), nullable=False)
    plant_name = Column(String, nullable=True)
    category_name  = Column(String, nullable=True)
    status = Column(String, default="ACTIVE")
    year = Column(Integer, nullable=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_time = Column(DateTime, nullable=False, server_default=func.now())

class plant_weekly_average(Base): 
    """
    Stores weekly average values for plants, including year and value.
    Used for analyzing plant performance and trends over time.
    Links plant_id to plant table for average calculations.
    Enables week-level reporting and performance analysis.
    """
    __tablename__ = "plant_weekly_average"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    plant_id = Column(Integer(), nullable=False)
    year = Column(Integer, nullable=True)
    value = Column(Float, nullable=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())


class PowerBIConfigJSON(Base):
    """
    Stores PowerBI configuration JSON data, including config name and timestamps.
    Used for managing PowerBI report configurations and settings.
    Links config_id to other tables for report-based analysis.
    Enables configuration-level reporting and auditing.
    """
    __tablename__ = "PowerBI_Config_JSON"

    config_id = Column(Integer, primary_key=True, index=True)
    config_name = Column(String(100), nullable=False, unique=True)
    config_json = Column(String, nullable=False)
    created_time = Column(DateTime, nullable=False, server_default=func.now())

class PotatoRateAreaCodeMapping(Base):
    """
    Maps potato rate area codes to growing areas and rates, including area name and activity status.
    Links growing_area_id and potato_rate_id to growing_area and potato_rates tables.
    Used for rate assignment and area-based analysis.
    Enables mapping between area codes and rate dimensions.
    """
    __tablename__ = "potato_rate_area_code_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    area_code = Column(String, nullable=False)
    growing_area_id = Column(Integer, nullable=True)
    growing_area_name = Column(String, nullable=True)
    potato_rate_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(String, nullable=True)
    created_time = Column(DateTime, nullable=False, server_default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(DateTime, nullable=False, server_default=func.now())

class powerbi_refresh_log(Base): 
    """
    Logs PowerBI refresh events and statuses, including report name, user, and timestamps.
    Used for tracking report refresh activity and completion.
    Links log_id to other tables for refresh-based analysis.
    Enables reporting and auditing of PowerBI refresh events.
    """
    __tablename__ = "powerbi_refresh_log"
    log_id = Column(Integer(), primary_key=True, autoincrement=True)
    report_name = Column(String, nullable=False)
    status = Column(String, nullable=True)
    trigger_datetime = Column(DateTime, nullable=True)
    completion_datetime = Column(DateTime, nullable=True)
    user_name = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    trigger_type = Column(String, nullable=True)

class OwnershipGrowerVariety(Base):
    """
    Maps ownership, grower, and variety for granular tracking, including contract and crop details.
    Links grower_id, growing_area_id, and variety_id to growers, growing_area, and variety tables.
    Used for detailed ownership and contract analysis at the variety level.
    Enables mapping between ownership, grower, area, and variety dimensions.
    """
    __tablename__ = 'ownership_growing_grower_variety_mapping'
    
    row_id = Column(String(100), primary_key=True)
    growing_area_id = Column(Integer(), nullable=False)
    grower_id = Column(Integer(), nullable=False)
    variety_id = Column(String(100), nullable=False)
    contract = Column(Integer(), nullable=True)
    year = Column(Integer(), nullable=True)
    shrinkage = Column(Float, nullable=True)
    shrinkage_volume = Column(Numeric(18, 3), nullable=True)
    market = Column(Float, nullable=True)
    flex = Column(Float, nullable=True)
    contract_erp = Column(Float, nullable=True)
    ownership_id = Column(String, nullable=True)
    crop_type = Column(String, nullable=True)
    crop_year = Column(String, nullable=False)
    status = Column(String, nullable=True)
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())

class Variety(Base):
    """
    Stores variety master data, including name, mapping, description, and status.
    Used for managing and tracking crop varieties across the platform.
    Links variety_id to OwnershipGrowerVariety for variety-level ownership analysis.
    Enables variety-level reporting and mapping.
    """

    __tablename__ = 'variety_master'

    variety_id = Column(Integer, primary_key=True, autoincrement=True)
    variety_name = Column(String(100), nullable=False, unique=True)
    variety_mapping = Column(String(100), nullable=False, unique=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_time = Column(DateTime, default=func.now())
    updated_by = Column(String, nullable=True)
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())

class Erp_Variety(Base):
    """
    Stores ERP variety data, including BPA number, release number, line number, shipment, crop type, and quantity accepted.
    Used for tracking variety information from ERP systems and integrating with ownership and grower data.
    By storing it in this table we avoid the daily refresh of the data.
    """

    __tablename__ = 'erp_variety'

    ID = Column(Integer, primary_key=True)
    BPA_Number = Column(BigInteger, nullable=True)
    Release_No = Column(BigInteger, nullable=True)
    Line_No = Column(BigInteger, nullable=True)
    Shipment = Column(BigInteger, nullable=True)
    Crop_Type = Column(String(100), nullable=True)
    Receipt_Date = Column(DateTime, nullable=True)
    Receipt_Year = Column(Integer, nullable=True)
    Period = Column(Integer, nullable=True)
    Week = Column(Integer, nullable=True)
    Grower_id = Column(Integer, nullable=True)
    Plant_id = Column(Integer, nullable=True)
    Growing_area_id = Column(Integer, nullable=True)
    Region_id = Column(Integer, nullable=True)
    Variety = Column(String(100), nullable=True)
    Variety_id = Column(Integer, nullable=True)
    Quantity_Accepted_MCWT = Column(Float, nullable=True)


# Views

"""
Database Views

The following section defines SQLAlchemy Table objects mapped to various database views.
These views aggregate, join, and summarize data for reporting, analytics, and dashboarding
across the potato sourcing matrix system. They provide precomputed results for costs,
rates, allocations, summaries, and user information, enabling efficient querying and
complex business logic without manual SQL. These views are essential for PowerBI,
dashboard APIs, and advanced reporting features.
"""

freight_cost_period_table = db.Table('View_freight_cost_period_combine', metadata, autoload=True, autoload_with=engine)
freight_cost_period_week_table = db.Table('View_freight_cost_week_view_combine', metadata, autoload=True,autoload_with=engine)
rate_growing_area_table = db.Table('View_freight_plan_actual_combine', metadata, autoload=True, autoload_with=engine)
View_p4p_result_table = db.Table('View_p4p_result', metadata, autoload=True, autoload_with=engine)
potato_rate_table_period = db.Table('View_potato_pricing_combine_period', metadata,  autoload=True,autoload_with=engine)
potato_rate_table_weekly = db.Table('View_potato_rates_period_week', metadata, autoload=True, autoload_with=engine)
solids_rate_table_period = db.Table('View_solid_plan_actual_combine_rate', metadata, autoload=True,autoload_with=engine)
dashboard_pc_volume_period = db.Table('View_dashboard_pc_volume_ratio', metadata, autoload=True, autoload_with=engine)
dashboard_weekly_combine = db.Table('View_dashboard_weekly_combine', metadata, autoload=True, autoload_with=engine)
dashboard_pc_usage_period= db.Table('View_dashboard_pc_usage_period',metadata, autoload_with=engine)
dashboard_pc_volume_period_country_combine = db.Table('View_dashboard_pc_volume_period_country_combine',metadata, autoload=True, autoload_with=engine)
dashboard_pc_volume_period_country_yearly = db.Table('View_dashboard_pc_volume_period_country_yearly',metadata, autoload=True, autoload_with=engine)
dashboard_pc_volume_yearly_country_combine = db.Table('View_dashboard_pc_volume_yearly_country_combine',metadata, autoload=True, autoload_with=engine)
summary_solids = db.Table('View_solid_summary',metadata, autoload=True,autoload_with=engine)
summary_price_variance= db.Table('view_summary_price_variance_reports',metadata, autoload=True,autoload_with=engine)
summary_overall_cost = db.Table('View_summary_UNION_OVERALL',metadata, autoload_with=engine)
summary_total_exp_wo_solids = db.Table('view_summary_union_TOTAL_EXP_Without_Solids',metadata, autoload_with=engine)
summary_total_exp_w_solids = db.Table('view_summary_union_TOTAL_EXP_With_Solids',metadata,autoload_with=engine)
summary_material_spend = db.Table('view_summary_union.Material_spend',metadata, autoload_with=engine)
summary_freight_spend = db.Table('view_summary_union.Freight_spend',metadata, autoload_with=engine)
summary_overall_cost_solids = db.Table('view_summary_union.Solids_Impact$',metadata,autoload_with=engine)
summary_category_spend = db.Table('view_summary_union.Category_Spend',metadata,autoload_with=engine)
summary_freight_total_yag = db.Table('view_summary_Freight_Total_EXP_YAG',metadata, autoload_with=engine)
summary_total_exp_w_solids_yag = db.Table('view_summary_TOTAL_Exp_With_Solids_YAG',metadata,autoload_with=engine)
summary_total_exp_wo_solids_yag = db.Table('view_summary_TOTAL_EXP_Without_Solids_YAG',metadata, autoload_with=engine)
inflation_deflation = db.Table('view_inflation_deflation_summary_main',metadata,  autoload=True,autoload_with=engine)
user_page_mapping_table = db.Table('View_user_information',metadata, autoload=True, autoload_with=engine)
user_information_mapping_view = db.Table('View_user_infomartion',metadata, autoload=True, autoload_with=engine)
solids_rate_plant_period = db.Table('View_solid_cost_period_combine', metadata, autoload=True, autoload_with=engine)
potato_rate_plant_period = db.Table('View_potato_cost_period_combine', metadata, autoload=True, autoload_with=engine)
potato_rate_plant_weekly = db.Table('View_potato_cost_week_view_combine', metadata, autoload=True,autoload_with=engine)
View_ownership_journal_info = db.Table('View_ownership_journal_info', metadata, autoload=True, autoload_with=engine)
View_erp_raw_alerts = db.Table('View_erp_raw_alerts', metadata, autoload=True, autoload_with=engine)
View_freight_fuel_cost_ga = db.Table('View_fuel_cost_calculation_growing_area', metadata, autoload=True, autoload_with=engine)
View_freight_fuel_cost = db.Table('View_fuel_cost_calculation_growing_area_plant', metadata, autoload=True, autoload_with=engine)
View_PlantMtrx_table = db.Table('View_PlantMtrx_table', metadata, autoload=True, autoload_with=engine) 
View_PlantMtrx_position = db.Table('View_PlantMtrx_position', metadata, autoload=True, autoload_with=engine)
View_plant_matrix_actual = db.Table('View_plant_matrix_actual', metadata, autoload=True, autoload_with=engine)
View_Matrix_growingarea = db.Table('View_Matrix_growingarea', metadata, autoload=True, autoload_with=engine)
View_site_plant_growing_area_mapping = db.Table('View_site_plant_growing_area_mapping', metadata,autoload=True, autoload_with=engine) 
view_plant_growing_area_Alice = db.Table('View_plant_growing_area', metadata,autoload=True, autoload_with=engine) 
view_growing_area_mapping_Alice = db.Table('view_growing_area_mapping', metadata,autoload=True, autoload_with=engine)
View_forecast_pcusage = db.Table('View_forecast_pcusage', metadata, autoload=True, autoload_with=engine)
View_Ownership = db.Table('View_Ownership', metadata, autoload=True, autoload_with=engine)
View_OwnershipMetrics_region = db.Table('View_OwnershipMetrics_region', metadata,  autoload=True,autoload_with=engine)
View_OwnershipMetrics_all = db.Table('View_OwnershipMetrics_all', metadata, autoload=True, autoload_with=engine)
View_OwnershipMetrics_country = db.Table('View_OwnershipMetrics_country', metadata, autoload=True, autoload_with=engine) 
View_growing_area_contract_erp = db.Table('View_growing_area_contract_erp', metadata, autoload=True,autoload_with=engine)
View_total_sum_growing_area = db.Table('View_total_sum_growing_area', metadata, autoload=True, autoload_with=engine)
View_p4p_result_table = db.Table('View_p4p_summary', metadata, autoload=True, autoload_with=engine)
View_p4p_result_update = db.Table('View_p4p_result_update', metadata, autoload=True,autoload_with=engine)