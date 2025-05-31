from enum import Enum



class BaseEnum(Enum):
    """
     Let's allow using an Enum class in model Field choices and make code more simple and modular.
     Ref: https://code.djangoproject.com/ticket/27910
     Ref: https://stackoverflow.com/questions/54802616/how-to-use-enums-as-a-choice-field-in-django-model
    """

    def __init__(self, *args):
        cls = self.__class__
        if any(self.value == e.value for e in cls):
            a = self.name
            e = cls(self.value).name

            raise ValueError("aliases not allowed in DuplicateFreeEnum:  %r --> %r" % (a, e))

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def exclude(cls, values: list = None):
        values = values or []
        return [(key.value, key.name) for key in cls if key.value not in values]

    @classmethod
    def values(cls):
        return [key.value for key in cls]

    @classmethod
    def keys(cls):
        return [key.name for key in cls]

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def get_key(cls, value):
        return [key.name for key in cls if key.value == value]

    @classmethod
    def validate(cls, items):
        available_item = []
        current_item = ''
        try:
            for item in items:
                current_item = item
                if cls.has_value(item):
                    available_item.append(item)
                else:
                    raise Exception
            return available_item
        except Exception as e:
            raise ValueError("Invalid choice:  %r for  %r" % (current_item, cls))

    @classmethod
    def make_json_compatible(cls):
        return [{key.name.lower(): key.value} for key in cls]

    @classmethod
    def exclude_values(cls, items):
        return [key.value for key in cls if key.value not in items]

    @classmethod
    def get_key_name(cls, value):
        for key in cls:
            if key.value == value:
                return key.name

    @classmethod
    def jsonify(cls):
        enum_dict = dict()
        for key in cls:
            source_name = key.name.split('_')
            full_source_name = ''
            if len(source_name) < 2:
                full_source_name = source_name[0].capitalize()
            elif len(source_name) > 1:
                for portion in source_name:
                    if full_source_name != '':
                        full_source_name += " "
                    full_source_name += portion.capitalize()
            enum_dict[key.value] = full_source_name
        return enum_dict


class UserStatus(BaseEnum):
    INVITED = "invited"
    RE_INVITED = "re-invited"
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

class ApprovalStatusChoices(BaseEnum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_REVIEW = "in_review"
    ON_HOLD = "on_hold"
    NEEDS_REVISION = "needs_revision"
    CANCELLED = "cancelled"


class CompanySizeEnum(BaseEnum):
    INDIVIDUAL = "individual"
    SMALL = "1-10"
    MEDIUM = "11-50"
    LARGE = "51-200"
    ENTERPRISE ="201+"


class UserRoleEnum(BaseEnum):
    INDIVIDUAL_OWNER = "individual_owner"
    REAL_ESTATE_BROKER = "real_estate_broker"
    REAL_ESTATE_DEVELOPER = "real_estate_developer"
    LUXURY_ASSETS_DEALER = "luxury_assets_dealer"
    SERVICE_PROFESSIONALS = "service_professionals"
    INVESTORS = "investors"

class UserPositionEnum(BaseEnum):
    # Individual Owners
    PROPERTY_OWNER = "property_owner"
    LANDLORD = "landlord"
    HOME_SELLER = "home_seller"
    VACATION_RENTAL_OWNER = "vacation_rental_owner"
    COMMERCIAL_PROPERTY_OWNER = "commercial_property_owner"
    RESIDENTIAL_INVESTOR = "residential_investor"
    AIRBNB_HOST = "airbnb_host"
    CONDOMINIUM_OWNER = "condominium_owner"
    PROPERTY_FLIPPER = "property_flipper"
    ESTATE_OWNER = "estate_owner"
    INDIVIDUAL_OTHER = "individual_other"

    # Real Estate Brokers
    BROKER = "broker"
    SALES_AGENT = "sales_agent"
    LEASING_AGENT = "leasing_agent"
    PROPERTY_MANAGER = "property_manager"
    REAL_ESTATE_CONSULTANT = "real_estate_consultant"
    LISTING_AGENT = "listing_agent"
    BUYERS_AGENT = "buyers_agent"
    COMMERCIAL_BROKER = "commercial_broker"
    RESIDENTIAL_BROKER = "residential_broker"
    REAL_ESTATE_TRAINER = "real_estate_trainer"
    BROKER_OTHER = "broker_other"

    # Real Estate Developers
    DEVELOPER = "developer"
    PROJECT_MANAGER = "project_manager"
    SALES_DIRECTOR = "sales_director"
    MARKETING_DIRECTOR = "marketing_director"
    CONSTRUCTION_MANAGER = "construction_manager"
    LAND_ACQUISITION_MANAGER = "land_acquisition_manager"
    FINANCIAL_ANALYST = "financial_analyst"
    ARCHITECT = "architect"
    URBAN_PLANNER = "urban_planner"
    DEVELOPMENT_CONSULTANT = "development_consultant"
    DEVELOPER_OTHER = "developer_other"

    # Luxury Assets Dealers
    DEALER = "dealer"
    SALES_EXECUTIVE = "sales_executive"
    STORE_MANAGER = "store_manager"
    AUCTIONEER = "auctioneer"
    ASSET_APPRAISER = "asset_appraiser"
    LUXURY_CAR_DEALER = "luxury_car_dealer"
    YACHT_BROKER = "yacht_broker"
    WATCH_SPECIALIST = "watch_specialist"
    LUXURY_RETAIL_MANAGER = "luxury_retail_manager"
    HIGH_NET_WORTH_CLIENT_ADVISOR = "high_net_worth_client_advisor"
    DEALER_OTHER = "dealer_other"

    # Service Professionals
    INTERIOR_DESIGNER = "interior_designer"
    FURNISHING_SPECIALIST = "furnishing_specialist"
    PROPERTY_MAINTENANCE_SUPERVISOR = "property_maintenance_supervisor"
    RENOVATION_CONTRACTOR = "renovation_contractor"
    LANDSCAPE_DESIGNER = "landscape_designer"
    HOME_STAGER = "home_stager"
    SECURITY_SYSTEM_INSTALLER = "security_system_installer"
    SMART_HOME_CONSULTANT = "smart_home_consultant"
    REAL_ESTATE_PHOTOGRAPHER = "real_estate_photographer"
    SERVICE_OTHER = "service_other"

    # Investors
    INDIVIDUAL_INVESTOR = "individual_investor"
    INSTITUTIONAL_INVESTOR = "institutional_investor"
    PORTFOLIO_MANAGER = "portfolio_manager"
    PROPERTY_FUND_MANAGER = "property_fund_manager"
    VENTURE_CAPITALIST = "venture_capitalist"
    PRIVATE_EQUITY_INVESTOR = "private_equity_investor"
    REAL_ESTATE_SYNDICATOR = "real_estate_syndicator"
    CROWDFUNDING_MANAGER = "crowdfunding_manager"
    ANGEL_INVESTOR = "angel_investor"
    REAL_ESTATE_INVESTMENT_CONSULTANT = "real_estate_investment_consultant"
    INVESTOR_OTHER = "investor_other"

    @classmethod
    def validate_user_position(cls, role, position):
        """
        Validate if a position is valid for a given role.
        """
        valid_positions = USER_ROLE_POSITION_MAPPER.get(role, [])
        if position in valid_positions:
            return True
        return False


# Mapper for validation
USER_ROLE_POSITION_MAPPER = {
    UserRoleEnum.INDIVIDUAL_OWNER.value: [
        UserPositionEnum.PROPERTY_OWNER.value,
        UserPositionEnum.LANDLORD.value,
        UserPositionEnum.HOME_SELLER.value,
        UserPositionEnum.VACATION_RENTAL_OWNER.value,
        UserPositionEnum.COMMERCIAL_PROPERTY_OWNER.value,
        UserPositionEnum.RESIDENTIAL_INVESTOR.value,
        UserPositionEnum.AIRBNB_HOST.value,
        UserPositionEnum.CONDOMINIUM_OWNER.value,
        UserPositionEnum.PROPERTY_FLIPPER.value,
        UserPositionEnum.ESTATE_OWNER.value,
        UserPositionEnum.INDIVIDUAL_OTHER.value,
    ],
    UserRoleEnum.REAL_ESTATE_BROKER.value: [
        UserPositionEnum.BROKER.value,
        UserPositionEnum.SALES_AGENT.value,
        UserPositionEnum.LEASING_AGENT.value,
        UserPositionEnum.PROPERTY_MANAGER.value,
        UserPositionEnum.REAL_ESTATE_CONSULTANT.value,
        UserPositionEnum.LISTING_AGENT.value,
        UserPositionEnum.BUYERS_AGENT.value,
        UserPositionEnum.COMMERCIAL_BROKER.value,
        UserPositionEnum.RESIDENTIAL_BROKER.value,
        UserPositionEnum.REAL_ESTATE_TRAINER.value,
        UserPositionEnum.BROKER_OTHER.value,
    ],
    UserRoleEnum.REAL_ESTATE_DEVELOPER.value: [
        UserPositionEnum.DEVELOPER.value,
        UserPositionEnum.PROJECT_MANAGER.value,
        UserPositionEnum.SALES_DIRECTOR.value,
        UserPositionEnum.MARKETING_DIRECTOR.value,
        UserPositionEnum.CONSTRUCTION_MANAGER.value,
        UserPositionEnum.LAND_ACQUISITION_MANAGER.value,
        UserPositionEnum.FINANCIAL_ANALYST.value,
        UserPositionEnum.ARCHITECT.value,
        UserPositionEnum.URBAN_PLANNER.value,
        UserPositionEnum.DEVELOPMENT_CONSULTANT.value,
        UserPositionEnum.DEVELOPER_OTHER.value,
    ],
    UserRoleEnum.LUXURY_ASSETS_DEALER.value: [
        UserPositionEnum.DEALER.value,
        UserPositionEnum.SALES_EXECUTIVE.value,
        UserPositionEnum.STORE_MANAGER.value,
        UserPositionEnum.AUCTIONEER.value,
        UserPositionEnum.ASSET_APPRAISER.value,
        UserPositionEnum.LUXURY_CAR_DEALER.value,
        UserPositionEnum.YACHT_BROKER.value,
        UserPositionEnum.WATCH_SPECIALIST.value,
        UserPositionEnum.LUXURY_RETAIL_MANAGER.value,
        UserPositionEnum.HIGH_NET_WORTH_CLIENT_ADVISOR.value,
        UserPositionEnum.DEALER_OTHER.value,
    ],
    UserRoleEnum.SERVICE_PROFESSIONALS.value: [
        UserPositionEnum.INTERIOR_DESIGNER.value,
        UserPositionEnum.FURNISHING_SPECIALIST.value,
        UserPositionEnum.PROPERTY_MAINTENANCE_SUPERVISOR.value,
        UserPositionEnum.RENOVATION_CONTRACTOR.value,
        UserPositionEnum.LANDSCAPE_DESIGNER.value,
        UserPositionEnum.HOME_STAGER.value,
        UserPositionEnum.SECURITY_SYSTEM_INSTALLER.value,
        UserPositionEnum.SMART_HOME_CONSULTANT.value,
        UserPositionEnum.REAL_ESTATE_PHOTOGRAPHER.value,
        UserPositionEnum.SERVICE_OTHER.value,
    ],
    UserRoleEnum.INVESTORS.value: [
        UserPositionEnum.INDIVIDUAL_INVESTOR.value,
        UserPositionEnum.INSTITUTIONAL_INVESTOR.value,
        UserPositionEnum.PORTFOLIO_MANAGER.value,
        UserPositionEnum.PROPERTY_FUND_MANAGER.value,
        UserPositionEnum.VENTURE_CAPITALIST.value,
        UserPositionEnum.PRIVATE_EQUITY_INVESTOR.value,
        UserPositionEnum.REAL_ESTATE_SYNDICATOR.value,
        UserPositionEnum.CROWDFUNDING_MANAGER.value,
        UserPositionEnum.ANGEL_INVESTOR.value,
        UserPositionEnum.REAL_ESTATE_INVESTMENT_CONSULTANT.value,
        UserPositionEnum.INVESTOR_OTHER.value,
    ],
}


class TokenTypeEnum(BaseEnum):
    TFA = "tfa"
    SIGN_UP = "sign_up"
    FORGOTTEN_PASSWORD = "forgotten_password"
    EMAIL_VERIFY = "email_verify"
    number_verify = "number_verify"


class TypicalUnitStatus(BaseEnum):
    AVAILABLE = "available"
    SOLD_OUT = "sold_out"
    SECONDARY_MARKET = "secondary_market"

class EventType(BaseEnum):
    ONLINE = "online"
    OFFLINE = "offline"

class EventStatus(BaseEnum):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING = 'pending'
    NEEDS_REVISION = "needs_revision"

class EventCategoryEnum(BaseEnum):
    REAL_ESTATE = "real_estate"
    LUXURY_ASSET = "luxury_asset"
    EDUCATIONAL_AND_TRAINING = "educational_and_training"
    NETWORKING_AND_BUSINESS_GROWTH = "networking_and_business_growth"
    WEBINARS_ONLINE = "webinars_online"
    SOCIAL_AND_EXCLUSIVE = "social_and_exclusive"

class EventSubCategoryEnum(BaseEnum):
    # Real Estate
    PROPERTY_SHOWCASE_LAUNCH = "property_showcase_launch"
    INVESTOR_SUMMIT = "investor_summit"
    DEVELOPER_MEETUP = "developer_meetup"
    REAL_ESTATE_EXPO_TRADE_SHOW = "real_estate_expo_trade_show"
    GOVERNMENT_LEGAL_UPDATE = "government_legal_update"

    # Luxury Asset
    LUXURY_CAR_EXHIBITION = "luxury_car_exhibition"
    YACHT_JET_SHOWCASE = "yacht_jet_showcase"
    LUXURY_WATCH_COLLECTIBLE = "luxury_watch_collectible"

    # Educational & Training
    REAL_ESTATE_SALES_TRAINING = "real_estate_sales_training"
    INVESTMENT_FINANCIAL_WORKSHOP = "investment_financial_workshop"
    LUXURY_MARKET_INSIGHT = "luxury_market_insight"
    MARKETING_DIGITAL_GROWTH_TRAINING = "marketing_digital_growth_training"

    # Networking & Business Growth
    VIP_NETWORKING_EVENT = "vip_networking_event"
    B2B_COLLABORATION_MEETUP = "b2b_collaboration_meetup"
    INDUSTRY_PANEL_DISCUSSION = "industry_panel_discussion"

    # Webinars & Online
    LIVE_REAL_ESTATE_WEBINAR = "live_real_estate_webinar"
    LUXURY_MARKET_INSIGHT_WEBINAR = "luxury_market_insight_webinar"
    DEVELOPER_QA_SESSION = "developer_qa_session"
    TRAINING_ACADEMY_WEBINAR = "training_academy_webinar"

    # Social & Exclusive
    PRIVATE_INVITATION_ONLY_EVENT = "private_invitation_only_event"
    EXCLUSIVE_PROPERTY_TOUR = "exclusive_property_tour"
    PROPADYA_COMMUNITY_MEETUP = "propadya_community_meetup"

    @classmethod
    def validate_event_sub_categories(cls, categories, sub_categories):
        """
        Validate if all sub-categories belong to at least one of the provided categories.
        Returns a tuple: (is_valid, invalid_sub_categories).
        """
        valid_sub_categories = set()  # Collect all valid sub-categories for given categories

        for category in categories:
            valid_sub_categories.update(EVENT_CATEGORY_MAPPING.get(category, []))

        # Find invalid sub-categories
        invalid_sub_categories = [sub for sub in sub_categories if sub not in valid_sub_categories]
        if invalid_sub_categories:
            return False, invalid_sub_categories
        else:
            return True, None

# Mapping Subcategories to Categories
EVENT_CATEGORY_MAPPING = {
    EventCategoryEnum.REAL_ESTATE.value: [
        EventSubCategoryEnum.PROPERTY_SHOWCASE_LAUNCH.value,
        EventSubCategoryEnum.INVESTOR_SUMMIT.value,
        EventSubCategoryEnum.DEVELOPER_MEETUP.value,
        EventSubCategoryEnum.REAL_ESTATE_EXPO_TRADE_SHOW.value,
        EventSubCategoryEnum.GOVERNMENT_LEGAL_UPDATE.value,
    ],
    EventCategoryEnum.LUXURY_ASSET.value: [
        EventSubCategoryEnum.LUXURY_CAR_EXHIBITION.value,
        EventSubCategoryEnum.YACHT_JET_SHOWCASE.value,
        EventSubCategoryEnum.LUXURY_WATCH_COLLECTIBLE.value,
    ],
    EventCategoryEnum.EDUCATIONAL_AND_TRAINING.value: [
        EventSubCategoryEnum.REAL_ESTATE_SALES_TRAINING.value,
        EventSubCategoryEnum.INVESTMENT_FINANCIAL_WORKSHOP.value,
        EventSubCategoryEnum.LUXURY_MARKET_INSIGHT.value,
        EventSubCategoryEnum.MARKETING_DIGITAL_GROWTH_TRAINING.value,
    ],
    EventCategoryEnum.NETWORKING_AND_BUSINESS_GROWTH.value: [
        EventSubCategoryEnum.VIP_NETWORKING_EVENT.value,
        EventSubCategoryEnum.B2B_COLLABORATION_MEETUP.value,
        EventSubCategoryEnum.INDUSTRY_PANEL_DISCUSSION.value,
    ],
    EventCategoryEnum.WEBINARS_ONLINE.value: [
        EventSubCategoryEnum.LIVE_REAL_ESTATE_WEBINAR.value,
        EventSubCategoryEnum.LUXURY_MARKET_INSIGHT_WEBINAR.value,
        EventSubCategoryEnum.DEVELOPER_QA_SESSION.value,
        EventSubCategoryEnum.TRAINING_ACADEMY_WEBINAR.value,
    ],
    EventCategoryEnum.SOCIAL_AND_EXCLUSIVE.value: [
        EventSubCategoryEnum.PRIVATE_INVITATION_ONLY_EVENT.value,
        EventSubCategoryEnum.EXCLUSIVE_PROPERTY_TOUR.value,
        EventSubCategoryEnum.PROPADYA_COMMUNITY_MEETUP.value,
    ],
}


class UserAssignedRoleEnum(BaseEnum):
    SUPER_USER = "superuser"
    ADMIN = "admin"
    MANAGER = "manager"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"
    SUPPORT = "support"

class UserStatusEnum(BaseEnum):
    INVITED = "invited"
    PENDING = "pending"
    ACTIVE = "active"
    IN_ACTIVE = "inactive"
    EXPIRED = "expired"
    REJECTED = "rejected"


class SubscriptionTypes(BaseEnum):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"

class SubscriptionDuration(BaseEnum):
    FOURTEEN_DAYS = "14_days"
    ONE_MONTH = "1_month"
    THREE_MONTHS = "3_months"
    SIX_MONTHS = "6_months"
    TWELVE_MONTHS = "12_months"

class PaymentStatus(BaseEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class InvoiceType(BaseEnum):
    REGULAR = "regular"
    FREE = "free"
    MANUAL = "manual"
    REFUND = "refund"

DURATION_DAYS_MAPPING = {
    SubscriptionDuration.FOURTEEN_DAYS.value: 14,
    SubscriptionDuration.ONE_MONTH.value: 30,
    SubscriptionDuration.THREE_MONTHS.value: 90,
    SubscriptionDuration.SIX_MONTHS.value: 180,
    SubscriptionDuration.TWELVE_MONTHS.value: 365
}